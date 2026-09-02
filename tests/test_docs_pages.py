"""Production tests for the documentation test pages.

These pages live in ``docs/express`` and ``docs/step`` and are meant to be an
exhaustive rendered corpus for the two lexers. The docs build in CI runs with
``mkdocs build --strict``, but that does not inspect Pygments token output, so
these tests close the gap:

* every `````express```` / ````step21```` fence on the test pages must lex with
  **zero** ``Error`` tokens;
* each category page must actually contain the whole family of tokens it claims
  to cover, so the pages cannot quietly drift out of date.

Run with ``pytest tests/test_docs_pages.py`` (or ``python tests/test_docs_pages.py``).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from pygments.lexers import get_lexer_by_name
from pygments.token import Error

from pygments_step.express import ExpressLexer
from pygments_step.step21 import StepFileLexer

# The complete reserved-word families come from the lexers themselves, so the
# pages and the lexer cannot disagree about what "all keywords" means.
_DECL = set(ExpressLexer._DECL)
_KEYWORDS = set(ExpressLexer._KEYWORDS)
_TYPES = set(ExpressLexer._TYPES)
_WORD_OPERATORS = set(ExpressLexer._WORD_OPERATORS)
_CONSTANTS = set(ExpressLexer._CONSTANTS) | {"?"}
_BUILTINS = set(ExpressLexer._BUILTINS)

# The 77 reserved words of ISO 10303-11 clause 7.2 table 1 are exactly the
# declaration heads plus the statement keywords plus the types.
TABLE_1 = sorted(_DECL | _KEYWORDS | _TYPES)

STEP_STRUCTURE_KEYWORDS = [
    "ISO-10303-21", "END-ISO-10303-21", "HEADER", "DATA",
    "ENDSEC", "ANCHOR", "REFERENCE", "SIGNATURE",
]

DOCS = Path(__file__).parent.parent / "docs"


def _fences(language: str):
    """Return {doc_name: [fence_text, ...]} for ``language`` fences across the test docs."""
    docs = sorted((DOCS / "express").glob("*.md")) + sorted((DOCS / "step").glob("*.md"))
    result: dict[str, list[str]] = {}
    opening = re.compile(r"^```(\w+)(.*)$")
    closing = re.compile(r"^```\s*$")
    for path in docs:
        text = path.read_text(encoding="utf-8")
        fences: list[str] = []
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            m = opening.match(lines[i])
            if m and m.group(1) == language:
                i += 1
                buf: list[str] = []
                while i < len(lines) and not closing.match(lines[i]):
                    buf.append(lines[i])
                    i += 1
                fences.append("\n".join(buf))
            i += 1
        if fences:
            result[path.name] = fences
    return result


def _all_fences(language: str) -> list[str]:
    return [f for fences in _fences(language).values() for f in fences]


def _error_tokens(lexer, text: str) -> list[str]:
    return [v for t, v in lexer.get_tokens(text) if t is Error]


# --------------------------------------------------------------------------
# Clean lexing
# --------------------------------------------------------------------------

def test_express_test_pages_lex_cleanly():
    lexer = ExpressLexer()
    bad: dict[str, list[str]] = {}
    for name, fences in _fences("express").items():
        for i, fence in enumerate(fences):
            errors = _error_tokens(lexer, fence)
            if errors:
                bad.setdefault(name, []).extend(f"{i}: {e!r}" for e in errors)
    assert bad == {}, f"EXPRESS test pages produced Error tokens: {bad}"


def test_step_test_pages_lex_cleanly():
    lexer = StepFileLexer()
    bad: dict[str, list[str]] = {}
    for name, fences in _fences("step21").items():
        for i, fence in enumerate(fences):
            errors = _error_tokens(lexer, fence)
            if errors:
                bad.setdefault(name, []).extend(f"{i}: {e!r}" for e in errors)
    assert bad == {}, f"STEP test pages produced Error tokens: {bad}"


# --------------------------------------------------------------------------
# Completeness: the pages must cover their family of tokens
# --------------------------------------------------------------------------

def _contains_word(text: str, word: str) -> bool:
    """True if ``word`` appears as a standalone, case-insensitive token."""
    if re.fullmatch(r"\w+", word):          # identifiers need real boundaries
        return re.search(rf"\b{re.escape(word.lower())}\b", text, re.IGNORECASE) is not None
    return word in text                     # `?` `$` `*` are matched literally


def _words_present(language: str, doc: str, words) -> list[str]:
    text = "\n".join(_fences(language).get(doc, []))
    return [w for w in words if not _contains_word(text, w)]


def test_express_keywords_page_covers_all_reserved_words():
    missing = _words_present("express", "keywords.md", TABLE_1)
    assert len(TABLE_1) == 77, f"expected 77 reserved words, got {len(TABLE_1)}"
    assert missing == [], f"keywords.md missing reserved words: {missing}"


def test_express_operators_page_covers_all_word_operators():
    missing = _words_present("express", "operators.md", _WORD_OPERATORS)
    assert len(_WORD_OPERATORS) == 9
    assert missing == [], f"operators.md missing word operators: {missing}"


def test_express_types_page_covers_all_types():
    missing = _words_present("express", "types.md", _TYPES)
    assert len(_TYPES) == 17
    assert missing == [], f"types.md missing types: {missing}"


def test_express_constants_page_covers_all_constants():
    missing = _words_present("express", "constants.md", _CONSTANTS)
    assert len(_CONSTANTS) == 7
    # `?` is a single character; make sure it is actually there as a token.
    assert "?" in "\n".join(_fences("express").get("constants.md", [])), "constants.md missing `?`"
    assert missing == [], f"constants.md missing constants: {missing}"


def test_express_builtins_page_covers_all_builtins():
    missing = _words_present("express", "builtins.md", _BUILTINS)
    assert len(_BUILTINS) == 31
    assert missing == [], f"builtins.md missing built-ins: {missing}"


def test_step_keywords_page_covers_all_structure_keywords():
    missing = _words_present("step21", "keywords.md", STEP_STRUCTURE_KEYWORDS)
    assert missing == [], f"keywords.md missing structure keywords: {missing}"


def test_step_enumerations_page_covers_enum_and_value_tokens():
    text = "\n".join(_fences("step21").get("enumerations.md", []))
    for token in (".T.", ".F.", ".UNSPECIFIED.", "$", "*"):
        assert token in text, f"enumerations.md missing {token!r}"


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
    print("\n" + ("all docs tests passed" if not failures else f"{failures} failure(s)"))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_main())
