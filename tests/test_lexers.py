"""Regression tests for the EXPRESS and STEP Part 21 lexers.

Run with ``pytest``, or directly with ``python tests/test_lexers.py``.

The fixtures are small hand-written snippets that are committed to the repo on
purpose: the real buildingSMART ``*.exp`` schemas are gitignored and fetched
over the network, so they cannot serve as a reproducible test corpus.
"""

from __future__ import annotations

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


def test_express_declared_names():
    pairs = tokens_of(ExpressLexer(), "sample.exp")
    declared = {v for t, v in pairs if t is Name.Class}
    assert {"geometry_primitives", "cartesian_point", "dimension_of"} <= declared
    assert (Keyword.Declaration, "ENTITY") in pairs


def test_express_instance_comparison_operators():
    """`:=:` must not be shadowed by `:=` (ISO 10303-11 rel_op)."""
    for src, op in (("a :=: b", ":=:"), ("a :<>: b", ":<>:")):
        assert (Operator, op) in list(ExpressLexer().get_tokens(src)), src


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
