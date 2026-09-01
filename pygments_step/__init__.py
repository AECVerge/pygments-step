"""Pygments lexers for the ISO 10303 (STEP) language family.

Provides two schema-agnostic lexers:

* :class:`ExpressLexer`  -- EXPRESS schema language (ISO 10303-11), ``*.exp``
* :class:`StepFileLexer` -- Part 21 exchange files (ISO 10303-21),
  ``*.p21``/``*.stp``/``*.step``

Both are registered with Pygments through ``pygments.lexers`` entry points, so
installing this package is enough -- no MkDocs configuration is required.
"""

from __future__ import annotations

from pygments_step.express import ExpressLexer
from pygments_step.step21 import StepFileLexer

__all__ = ["ExpressLexer", "StepFileLexer"]
__version__ = "0.1.0"
