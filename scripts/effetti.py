#!/usr/bin/env python3
"""Il punto di ingresso: python scripts/effetti.py --elenco"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from effetti.cli import main  # noqa: E402

main()
