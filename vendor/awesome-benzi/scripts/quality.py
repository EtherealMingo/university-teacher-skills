#!/usr/bin/env python3
"""Compatibility CLI for content, document and package quality gates."""

from core import quality_gates as _impl

globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("__")})


if __name__ == "__main__":
    raise SystemExit(_impl.main())
