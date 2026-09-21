"""Regression tests for the EXPRESS and STEP Part 21 lexers.

Run with ``pytest``, or directly with ``python tests/test_lexers.py``.

The fixtures are small hand-written snippets that are committed to the repo on
purpose: the real buildingSMART ``*.exp`` schemas are gitignored and fetched
over the network, so they cannot serve as a reproducible test corpus.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.token import (Comment, Error, Keyword, Name, Number, Operator,
                            Punctuation, String)

from pygments_step import ExpressLexer, StepFileLexer

FIXTURES = Path(__file__).parent / "fixtures"

EXPRESS_ALIASES = ["express", "exp", "iso-10303-11"]
STEP_ALIASES = ["step21", "p21", "step", "stp", "spf", "iso-10303-21"]


def tokens_of(lexer, filename):
    source = (FIXTURES / filename).read_text(encoding="utf-8")
    return list(lexer.get_tokens(source))


def joined(pairs, token_type):
    return "".join(v for t, v in pairs if t is token_type)


# --------------------------------------------------------------------------
# Registration
# --------------------------------------------------------------------------

def test_express_aliases_resolve():
    for alias in EXPRESS_ALIASES:
        assert get_lexer_by_name(alias).name == "EXPRESS", alias


def test_step_aliases_resolve():
    for alias in STEP_ALIASES:
        assert get_lexer_by_name(alias).name == "STEP Part 21", alias


def test_filename_dispatch():
    assert get_lexer_for_filename("schema.exp").name == "EXPRESS"
    for name in ("model.stp", "model.step", "model.p21"):
        assert get_lexer_for_filename(name).name == "STEP Part 21", name


def test_no_application_protocol_is_privileged():
    """IFC is just one SPF format; the lexer must not claim it specifically."""
    lexer = StepFileLexer()
    assert "ifc" not in lexer.aliases
    assert "*.ifc" not in lexer.filenames


# --------------------------------------------------------------------------
# No unrecognised input
# --------------------------------------------------------------------------

def test_express_fixture_lexes_cleanly():
    bad = [v for t, v in tokens_of(ExpressLexer(), "sample.exp") if t is Error]
    assert bad == [], f"unlexed EXPRESS input: {bad[:10]}"


def test_step_fixture_lexes_cleanly():
    bad = [v for t, v in tokens_of(StepFileLexer(), "sample.p21") if t is Error]
    assert bad == [], f"unlexed Part 21 input: {bad[:10]}"


# --------------------------------------------------------------------------
# EXPRESS specifics
# --------------------------------------------------------------------------

def test_express_remarks_nest():
    """`(* outer (* inner *) still outer *)` must stay entirely a comment."""
    pairs = tokens_of(ExpressLexer(), "sample.exp")
    assert "clause 7.1.6" in joined(pairs, Comment.Multiline)


def test_express_tail_remark():
    pairs = tokens_of(ExpressLexer(), "sample.exp")
    assert any("tail remark" in v for t, v in pairs if t is Comment.Single)


def test_express_literals():
    pairs = tokens_of(ExpressLexer(), "sample.exp")
    assert (String.Escape, "''") in pairs          # doubled-quote escape
    assert (Number.Bin, "%10110") in pairs         # binary literal
    assert (String.Other, '"000000E9"') in pairs   # encoded string literal


def test_express_encoded_string_literal_is_lexed_permissively():
    """Colouring, not validating: any hex run in quotes is one string token.

    Clause 7.5.4 wants whole characters, four octets each, but a partial group
    must stay a single String.Other rather than being split into Error, a
    number and an identifier.
    """
    lexer = ExpressLexer()
    for src in ('"000000E9"', '"00000041000000E9"', '"1F2A3B"', '""'):
        pairs = list(lexer.get_tokens(src))
        assert (String.Other, src) in pairs, src
        assert [v for t, v in pairs if t is Error] == [], src
    # A non-hexadecimal character is still not an encoded string literal.
    assert (String.Other, '"0000004G"') not in list(lexer.get_tokens('"0000004G"'))


def test_express_unterminated_string_stops_at_the_line_end():
    """A missing closing quote must not swallow the rest of the file.

    A string literal never spans a physical line boundary (clause 7.5.4), so
    the newline ends the runaway literal instead of everything after it.
    """
    pairs = list(ExpressLexer().get_tokens("s := 'oops\nx := 1;\n"))
    assert "".join(v for t, v in pairs if t is String.Single) == "'oops\n"
    assert (Name, "x") in pairs
    assert (Number.Integer, "1") in pairs
    assert [v for t, v in pairs if t is Error] == []


def test_express_identifier_starts_with_a_letter():
    """`simple_id` = letter { letter | digit | "_" } (ISO 10303-11 clause 7.4)."""
    lexer = ExpressLexer()
    for src in ("cartesian_point", "a_b1", "x1"):
        assert (Name, src) in list(lexer.get_tokens(src)), src
    # A leading underscore is not part of an identifier.
    pairs = list(lexer.get_tokens("_x"))
    assert (Name, "_x") not in pairs
    assert (Error, "_") in pairs


def test_express_declared_names():
    pairs = tokens_of(ExpressLexer(), "sample.exp")
    declared = {v for t, v in pairs if t is Name.Class}
    assert {"geometry_primitives", "cartesian_point", "dimension_of"} <= declared
    assert (Keyword.Declaration, "ENTITY") in pairs


def test_express_declaration_head_does_not_swallow_a_reserved_word():
    """`ENTITY ENUMERATION` declares nothing: ENUMERATION is a type keyword."""
    pairs = list(ExpressLexer().get_tokens("ENTITY ENUMERATION;"))
    assert (Keyword.Declaration, "ENTITY") in pairs
    assert (Keyword.Type, "ENUMERATION") in pairs
    assert (Name.Class, "ENUMERATION") not in pairs


def test_express_bare_declaration_heads_stay_heads():
    """Back-to-back heads, as on the declarations page, are all heads."""
    heads = ["SCHEMA", "ENTITY", "TYPE", "FUNCTION", "PROCEDURE", "RULE",
             "CONSTANT", "SUBTYPE_CONSTRAINT"]
    pairs = list(ExpressLexer().get_tokens("\n".join(heads)))
    assert [v for t, v in pairs if t is Keyword.Declaration] == heads
    assert [v for t, v in pairs if t is Name.Class] == []


def test_express_declared_name_is_an_identifier():
    """The name may start *like* a keyword, but not be one, and needs a letter."""
    assert (Name.Class, "types") in list(ExpressLexer().get_tokens("TYPE types;"))
    assert (Name.Class, "_x") not in list(ExpressLexer().get_tokens("ENTITY _x;"))


def test_express_instance_comparison_operators():
    """`:=:` must not be shadowed by `:=` (ISO 10303-11 rel_op)."""
    for src, op in (("a :=: b", ":=:"), ("a :<>: b", ":<>:")):
        assert (Operator, op) in list(ExpressLexer().get_tokens(src)), src


def test_express_at_sign_is_not_an_operator():
    """`@` is a character of the EXPRESS character set, but not a symbol.

    Clause 7.1.3 lists it among the special characters, so it is legal inside a
    string literal, but clause 7.3 table 6 has no `@` and no operator uses it.
    """
    pairs = list(ExpressLexer().get_tokens("@x"))
    assert (Operator, "@") not in pairs
    assert (Error, "@") in pairs
    assert (String.Single, "a@b") in list(ExpressLexer().get_tokens("'a@b'"))


def test_express_fixed_keyword():
    """FIXED closes a width_spec: `STRING(n) FIXED` (ISO 10303-11)."""
    pairs = list(ExpressLexer().get_tokens("x : STRING(3) FIXED;"))
    assert (Keyword, "FIXED") in pairs


def test_express_aggregation_types_agree():
    """ARRAY, BAG, LIST and SET are one family and must lex alike."""
    for kw in ("ARRAY", "BAG", "LIST", "SET"):
        assert (Keyword.Type, kw) in list(ExpressLexer().get_tokens(kw)), kw


def test_express_builtin_call_keeps_whitespace_separate():
    pairs = list(ExpressLexer().get_tokens("SIZEOF (a)"))
    assert (Name.Builtin, "SIZEOF") in pairs
    assert (Punctuation, "(") in pairs


def test_express_word_operators():
    """Table 2 keeps operator reserved words apart from table 1 keywords."""
    src = "IF a AND NOT b OR c XOR d THEN"
    pairs = list(ExpressLexer().get_tokens(src))
    for op in ("AND", "NOT", "OR", "XOR"):
        assert (Operator.Word, op) in pairs, op
    # IF/THEN stay ordinary keywords.
    assert (Keyword, "IF") in pairs
    assert (Keyword, "THEN") in pairs


def test_express_andor_not_split_into_and():
    """`ANDOR` must win over `AND` despite sharing a prefix."""
    pairs = list(ExpressLexer().get_tokens("a ANDOR b"))
    assert (Operator.Word, "ANDOR") in pairs


def test_express_builtin_constants():
    """Table 3 of ISO 10303-11:2004 lists SELF and "?" as constants."""
    pairs = list(ExpressLexer().get_tokens("x := SELF; y := ?;"))
    assert (Keyword.Constant, "SELF") in pairs
    assert (Keyword.Constant, "?") in pairs


def test_express_unbounded_aggregate_bound():
    """`SET [0:?] OF` uses the indeterminate constant as its upper bound."""
    pairs = list(ExpressLexer().get_tokens("s : SET [0:?] OF thing;"))
    assert (Keyword.Constant, "?") in pairs
    assert [v for t, v in pairs if t is Error] == []


# --------------------------------------------------------------------------
# STEP Part 21 specifics
# --------------------------------------------------------------------------

def test_step_instance_definition_vs_reference():
    pairs = tokens_of(StepFileLexer(), "sample.p21")
    assert (Name.Label, "#1") in pairs      # `#1=` is a definition
    assert (Name.Variable, "#1") in pairs   # `,#1,` is a reference


def test_step_enumerations_and_unset():
    pairs = tokens_of(StepFileLexer(), "sample.p21")
    assert (Name.Constant, ".T.") in pairs
    assert (Name.Constant, ".UNSPECIFIED.") in pairs
    assert (Keyword.Constant, "$") in pairs   # unset
    assert (Keyword.Constant, "*") in pairs   # derived


def test_step_string_control_directives():
    pairs = tokens_of(StepFileLexer(), "sample.p21")
    escapes = [v for t, v in pairs if t is String.Escape]
    assert "\\X2\\00F8\\X0\\" in escapes
    assert "''" in escapes


def test_step_entity_names_and_literals():
    pairs = tokens_of(StepFileLexer(), "sample.p21")
    names = {v for t, v in pairs if t is Name.Class}
    assert "CARTESIAN_POINT" in names
    assert "!USER_DEFINED_KEYWORD" in names     # user-defined keyword
    assert (Number.Hex, '"0F3A"') in pairs
    assert (Keyword.Namespace, "ISO-10303-21") in pairs
    assert (Keyword.Namespace, "END-ISO-10303-21") in pairs


def test_step_end_marker_is_not_split():
    """The alternation must try END-ISO-10303-21 before ISO-10303-21."""
    pairs = list(StepFileLexer().get_tokens("END-ISO-10303-21;"))
    assert (Keyword.Namespace, "END-ISO-10303-21") in pairs


def test_step_print_directives_in_string():
    r"""\N\ and \F\ are print control directives (ISO 10303-21 table 6)."""
    pairs = list(StepFileLexer().get_tokens(r"#1=A('one\N\two');"))
    assert (String.Escape, "\\N\\") in pairs


def test_step_print_directives_outside_string():
    r"""They may appear wherever a token separator may appear (clause 11)."""
    src = "#1=A(1);\\N\\#2=B(2);\\F\\"
    bad = [v for t, v in StepFileLexer().get_tokens(src) if t is Error]
    assert bad == [], f"unlexed print control directive: {bad}"


# --------------------------------------------------------------------------
# Reserved word coverage, ISO 10303-11:2004 clause 7.2 tables 1-5
# --------------------------------------------------------------------------

TABLE_1_KEYWORDS = """
    ABSTRACT AGGREGATE ALIAS ARRAY AS BAG BASED_ON BEGIN BINARY BOOLEAN BY
    CASE CONSTANT DERIVE ELSE END END_ALIAS END_CASE END_CONSTANT END_ENTITY
    END_FUNCTION END_IF END_LOCAL END_PROCEDURE END_REPEAT END_RULE
    END_SCHEMA END_SUBTYPE_CONSTRAINT END_TYPE ENTITY ENUMERATION ESCAPE
    EXTENSIBLE FIXED FOR FROM FUNCTION GENERIC GENERIC_ENTITY IF INTEGER
    INVERSE LIST LOCAL LOGICAL NUMBER OF ONEOF OPTIONAL OTHERWISE PROCEDURE
    QUERY REAL RENAMED REFERENCE REPEAT RETURN RULE SCHEMA SELECT SET SKIP
    STRING SUBTYPE SUBTYPE_CONSTRAINT SUPERTYPE THEN TO TOTAL_OVER TYPE
    UNIQUE UNTIL USE VAR WHERE WHILE WITH
""".split()

TABLE_2_OPERATORS = "AND ANDOR DIV IN LIKE MOD NOT OR XOR".split()

TABLE_3_CONSTANTS = "? SELF CONST_E PI FALSE TRUE UNKNOWN".split()

TABLE_4_FUNCTIONS = """
    ABS ACOS ASIN ATAN BLENGTH COS EXISTS EXP FORMAT HIBOUND HIINDEX LENGTH
    LOBOUND LOG LOG2 LOG10 LOINDEX NVL ODD ROLESOF SIN SIZEOF SQRT TAN
    TYPEOF USEDIN VALUE VALUE_IN VALUE_UNIQUE
""".split()

TABLE_5_PROCEDURES = "INSERT REMOVE".split()

# Every reserved word of ISO 10303-11 clause 7.2, tables 1 to 5, lowercase to
# match the tuples the lexer carries.
ALL_RESERVED_EXPECTED = {
    w.lower() for w in (TABLE_1_KEYWORDS + TABLE_2_OPERATORS + TABLE_3_CONSTANTS
                        + TABLE_4_FUNCTIONS + TABLE_5_PROCEDURES)
}


def sole_token(src):
    """Token type of the first non-whitespace token of ``src``."""
    for t, v in ExpressLexer().get_tokens(src):
        if v.strip():
            return t
    raise AssertionError(f"no token produced for {src!r}")


def test_table_sizes_match_the_standard():
    """Guard the transcription itself against edits."""
    assert len(TABLE_1_KEYWORDS) == 77
    assert len(TABLE_2_OPERATORS) == 9
    assert len(TABLE_3_CONSTANTS) == 7
    assert len(TABLE_4_FUNCTIONS) == 29
    assert len(TABLE_5_PROCEDURES) == 2


def test_every_table_1_keyword_is_recognised():
    missed = [w for w in TABLE_1_KEYWORDS if sole_token(w) is Name]
    assert missed == [], f"lexed as plain identifiers: {missed}"


def test_every_table_2_operator_is_an_operator():
    bad = [w for w in TABLE_2_OPERATORS if sole_token(w) is not Operator.Word]
    assert bad == [], f"not Operator.Word: {bad}"


def test_every_table_3_constant_is_a_constant():
    bad = [w for w in TABLE_3_CONSTANTS
           if sole_token(w) is not Keyword.Constant]
    assert bad == [], f"not Keyword.Constant: {bad}"


def test_every_built_in_routine_is_recognised():
    """Tables 4 and 5; built-ins are only meaningful in call position."""
    routines = TABLE_4_FUNCTIONS + TABLE_5_PROCEDURES
    bad = [w for w in routines if sole_token(w + "(x)") is not Name.Builtin]
    assert bad == [], f"not Name.Builtin: {bad}"


def test_no_reserved_word_lexes_as_an_error():
    every = (TABLE_1_KEYWORDS + TABLE_2_OPERATORS + TABLE_3_CONSTANTS
             + TABLE_4_FUNCTIONS + TABLE_5_PROCEDURES)
    for word in every:
        bad = [v for t, v in ExpressLexer().get_tokens(word) if t is Error]
        assert bad == [], f"{word} produced {bad}"


def test_table_1_tuples_partition_the_keyword_table():
    """_DECL, _KEYWORDS and _TYPES must split table 1 without overlapping.

    They sum to exactly the 77 keywords, so a word carried by two tuples (as
    CONSTANT once was) means one of the rules can never fire.
    """
    decl = set(ExpressLexer._DECL)
    keywords = set(ExpressLexer._KEYWORDS)
    types = set(ExpressLexer._TYPES)
    assert decl & keywords == set(), f"in _DECL and _KEYWORDS: {sorted(decl & keywords)}"
    assert decl & types == set(), f"in _DECL and _TYPES: {sorted(decl & types)}"
    assert keywords & types == set(), f"in _KEYWORDS and _TYPES: {sorted(keywords & types)}"
    assert len(decl) + len(keywords) + len(types) == len(TABLE_1_KEYWORDS) == 77


def test_reserved_word_set_covers_tables_1_to_5():
    """_ALL_RESERVED guards the declared name, so it must miss no reserved word."""
    reserved = set(ExpressLexer._ALL_RESERVED)
    # `?` is the single deliberate omission: it is a built-in constant (table
    # 3), but a declared name always starts with a letter, so it can never
    # appear where this set is consulted.
    assert reserved == ALL_RESERVED_EXPECTED - {"?"}
    assert len(reserved) == 123
    # Longest first, so a shorter word cannot shadow a longer one.
    lengths = [len(w) for w in ExpressLexer._ALL_RESERVED]
    assert lengths == sorted(lengths, reverse=True)
    # The alternation holds the same words, nothing more or less.
    assert set(re.findall(r"[a-z0-9_]+", ExpressLexer._RESERVED_ALT)) == reserved


# --------------------------------------------------------------------------

def _main():
    failures = 0
    for name, fn in sorted(globals().items()):
        if not name.startswith("test_") or not callable(fn):
            continue
        try:
            fn()
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {name}: {exc}")
        else:
            print(f"ok   {name}")
    print("\n" + ("all tests passed" if not failures else f"{failures} failure(s)"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_main())
