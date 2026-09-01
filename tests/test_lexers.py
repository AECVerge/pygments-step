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
from pygments.token import Comment, Error, Keyword, Name, Number, String

from pygments_step import ExpressLexer, StepFileLexer

FIXTURES = Path(__file__).parent / "fixtures"

EXPRESS_ALIASES = ["express", "exp", "iso-10303-11"]
STEP_ALIASES = ["step21", "p21", "step", "stp", "spf"]


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
