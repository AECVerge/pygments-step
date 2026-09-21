"""Pygments lexer for EXPRESS (ISO 10303-11)."""

from __future__ import annotations

import re

from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import (Comment, Keyword, Name, Number, Operator,
                            Punctuation, String, Whitespace)

__all__ = ["ExpressLexer"]


class ExpressLexer(RegexLexer):
    """Lexer for the EXPRESS data modelling language (ISO 10303-11).
    """

    name = "EXPRESS"
    aliases = ["express", "exp", "iso-10303-11"]
    filenames = ["*.exp"]
    mimetypes = ["text/x-express"]
    url = "https://en.wikipedia.org/wiki/EXPRESS_(data_modeling_language)"

    # EXPRESS keywords are case insensitive (ISO 10303-11, clause 7).
    # re.ASCII keeps the lexical space ASCII-only, as the standard requires:
    # without it ``\d`` and the case-insensitive ``[a-z]`` ranges also accept
    # non-ASCII input (Arabic-Indic digits, KELVIN SIGN, long s).
    flags = re.IGNORECASE | re.MULTILINE | re.ASCII

    _DECL = ("schema", "entity", "type", "function", "procedure", "rule",
             "constant", "subtype_constraint")

    # Statement keywords: table 1 minus the declaration heads (_DECL), which
    # already carries CONSTANT, and minus the built-in type keywords (_TYPES).
    # The three tuples therefore partition table 1 (8 + 52 + 17 = 77).
    _KEYWORDS = (
        "abstract", "alias", "as", "based_on", "begin", "by", "case",
        "derive", "else", "end", "end_alias", "end_case",
        "end_constant", "end_entity", "end_function", "end_if", "end_local",
        "end_procedure", "end_repeat", "end_rule", "end_schema",
        "end_subtype_constraint", "end_type", "escape", "fixed", "for",
        "from", "if", "inverse", "local", "of", "oneof", "optional",
        "otherwise", "query", "reference", "renamed", "repeat", "return",
        "skip", "subtype", "supertype", "then", "to", "total_over", "unique",
        "until", "use", "var", "where", "while", "with",
    )

    # Table 2 keeps these apart from the table 1 keywords: they are reserved
    # words that denote operators, so they carry an operator token.
    _WORD_OPERATORS = ("and", "andor", "div", "in", "like", "mod", "not",
                       "or", "xor")

    # array, bag, list and set are all aggregation_types (clause 172), so they
    # are classified together rather than split across Keyword/Keyword.Type.
    _TYPES = ("aggregate", "array", "bag", "binary", "boolean", "enumeration",
              "extensible", "generic", "generic_entity", "integer", "list",
              "logical", "number", "real", "select", "set", "string")

    # Table 3 of ISO 10303-11:2004 lists SELF and "?" among the built-in
    # constants, alongside CONST_E, PI, TRUE, FALSE and UNKNOWN.
    _CONSTANTS = ("true", "false", "unknown", "const_e", "pi", "self")

    _BUILTINS = (
        "abs", "acos", "asin", "atan", "blength", "cos", "exists", "exp",
        "format", "hibound", "hiindex", "insert", "length", "lobound",
        "loindex", "log", "log2", "log10", "nvl", "odd", "remove", "rolesof",
        "sin", "sizeof", "sqrt", "tan", "typeof", "usedin", "value",
        "value_in", "value_unique",
    )

    # Every reserved word of ISO 10303-11 clause 7.2 except the indeterminate
    # constant "?" (tables 1 to 5): clause 7.2 forbids all of them as
    # identifiers, and the declaration rule uses this set to keep a head from
    # swallowing the next reserved word as the declared name. Table 3's "?" is
    # left out because a declared name always starts with a letter.
    # Longest first, so a shorter word can never shadow a longer one.
    _ALL_RESERVED = tuple(sorted(
        set(_DECL + _KEYWORDS + _WORD_OPERATORS + _TYPES + _CONSTANTS
            + _BUILTINS),
        key=lambda word: (-len(word), word),
    ))
    _RESERVED_ALT = "|".join(re.escape(word) for word in _ALL_RESERVED)

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"--.*?$", Comment.Single),                 # tail remark
            (r"\(\*", Comment.Multiline, "comment"),     # embedded remark
            # Declaration head: give the declared name its own token, but never
            # let it be one of the reserved words, or the name would eat the
            # next token: `ENTITY ENUMERATION` is a declaration head followed
            # by a type keyword, not an entity called ENUMERATION. A rejected
            # name makes this rule fail, so the bare head rule below tokenises
            # the head on its own and the reserved word keeps its own token.
            (words(_DECL, prefix=r"\b",
                suffix=r"\b(\s+)(?!(?:" + _RESERVED_ALT + r")\b)([a-z][a-z0-9_]*)"),
                bygroups(Keyword.Declaration, Whitespace, Name.Class)
            ),
            (words(_DECL, prefix=r"\b", suffix=r"\b"), Keyword.Declaration),
            (words(_CONSTANTS, prefix=r"\b", suffix=r"\b"), Keyword.Constant),
            (words(_TYPES, prefix=r"\b", suffix=r"\b"), Keyword.Type),
            (words(_WORD_OPERATORS, prefix=r"\b", suffix=r"\b"), Operator.Word),
            (words(_KEYWORDS, prefix=r"\b", suffix=r"\b"), Keyword),
            (words(_BUILTINS, prefix=r"\b", suffix=r"\b(?=\s*\()"),
             Name.Builtin),
            (r"'", String.Single, "string"),
            # Encoded string literal. Clause 7.5.4 encodes each character as
            # four octets, that is eight hexadecimal digits, but a lexer colours
            # rather than validates: keeping a partial group as one string token
            # beats splitting it into Error, a number and an identifier.
            (r'"[0-9a-f]*"', String.Other),
            (r"%[01]+", Number.Bin),                     # binary literal
            (r"\d+\.\d*(e[+-]?\d+)?", Number.Float),
            (r"\d+", Number.Integer),
            (r"[a-z_]\w*", Name),
            # "?" is the indeterminate built-in constant (table 3), not an
            # operator, so it is matched before the operator character class.
            (r"\?", Keyword.Constant),
            # Longest-first: `:=` must not shadow `:=:` (rel_op, clause 282).
            (r":=:|:<>:|:=|<[*>=]?|>=?|<>|\*\*|\|\||[-+*/=|@\\]", Operator),
            (r"[;:,.()\[\]{}]", Punctuation),
        ],
        "comment": [
            (r"[^(*]+", Comment.Multiline),
            (r"\(\*", Comment.Multiline, "#push"),       # remarks nest
            (r"\*\)", Comment.Multiline, "#pop"),
            (r"[(*]", Comment.Multiline),
        ],
        "string": [
            (r"''", String.Escape),
            (r"'", String.Single, "#pop"),
            # A string literal never spans a physical line boundary (clause
            # 7.5.4), so a missing closing quote must not turn the rest of the
            # file into string text: the newline ends the runaway literal and
            # the next line lexes normally again.
            (r"[^'\n]+", String.Single),
            (r"\n", String.Single, "#pop"),
        ],
    }
