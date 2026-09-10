#!/usr/bin/env python3
"""Compatibility CLI for semantic extraction and prepared sessions."""

from core import template_schema as _impl

globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("__")})


if __name__ == "__main__":
    raise SystemExit(_impl.main())
