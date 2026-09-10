#!/usr/bin/env python3
"""Compatibility CLI for read-only intake and routing."""

from core import intake as _impl

globals().update({name: value for name, value in vars(_impl).items() if not name.startswith("__")})


if __name__ == "__main__":
    raise SystemExit(_impl.main())
