#!/usr/bin/env python3
"""Compatibility CLI for legacy builds and two-phase verified delivery."""

from core import docx_writer as _impl

globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("__")})


if __name__ == "__main__":
    raise SystemExit(_impl.main())
