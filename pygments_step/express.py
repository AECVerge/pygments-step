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
    version_added = "0.1"

    # EXPRESS keywords are case insensitive (ISO 10303-11, clause 7).
    flags = re.IGNORECASE | re.MULTILINE

    _DECL = ("schema", "entity", "type", "function", "procedure", "rule",
             "constant", "subtype_constraint")

    _KEYWORDS = (
        "abstract", "alias", "and", "andor", "array", "as", "bag", "based_on",
        "begin", "by", "case", "constant", "derive", "div", "else", "end",
        "end_alias", "end_case", "end_constant", "end_entity", "end_function",
        "end_if", "end_local", "end_procedure", "end_repeat", "end_rule",
        "end_schema", "end_subtype_constraint", "end_type", "escape", "for",
        "from", "if", "in", "inverse", "like", "local", "mod", "not", "of",
        "oneof", "optional", "or", "otherwise", "query", "reference",
        "renamed", "repeat", "return", "self", "skip", "subtype", "supertype",
        "then", "to", "total_over", "unique", "until", "use", "var", "where",
        "while", "with", "xor",
    )

    _TYPES = ("aggregate", "binary", "boolean", "enumeration", "extensible",
              "generic", "generic_entity", "integer", "list", "logical",
              "number", "real", "select", "set", "string")

    _CONSTANTS = ("true", "false", "unknown", "const_e", "pi")

    _BUILTINS = (
        "abs", "acos", "asin", "atan", "blength", "cos", "exists", "exp",
        "format", "hibound", "hiindex", "insert", "length", "lobound",
        "loindex", "log", "log2", "log10", "nvl", "odd", "remove", "rolesof",
        "sin", "sizeof", "sqrt", "tan", "typeof", "usedin", "value",
        "value_in", "value_unique",
    )

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"--.*?$", Comment.Single),                 # tail remark
            (r"\(\*", Comment.Multiline, "comment"),     # embedded remark
            # Declaration head: give the declared name its own token.
            (words(_DECL, prefix=r"\b", suffix=r"\b(\s+)([a-z_]\w*)"),
             bygroups(Keyword.Declaration, Whitespace, Name.Class)),
            (words(_DECL, prefix=r"\b", suffix=r"\b"), Keyword.Declaration),
            (words(_CONSTANTS, prefix=r"\b", suffix=r"\b"), Keyword.Constant),
            (words(_TYPES, prefix=r"\b", suffix=r"\b"), Keyword.Type),
            (words(_KEYWORDS, prefix=r"\b", suffix=r"\b"), Keyword),
            (words(_BUILTINS, prefix=r"\b", suffix=r"\b(\s*\()"),
             bygroups(Name.Builtin, Punctuation)),
            (r"'", String.Single, "string"),
            (r'"[0-9a-f]*"', String.Other),              # encoded string literal
            (r"%[01]+", Number.Bin),                     # binary literal
            (r"\d+\.\d*(e[+-]?\d+)?", Number.Float),
            (r"\d+", Number.Integer),
            (r"[a-z_]\w*", Name),
            (r":=|:<>:|:=:|<[*>=]?|>=?|<>|\*\*|\|\||[-+*/=|?@\\]", Operator),
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
            (r"[^']+", String.Single),
        ],
    }
