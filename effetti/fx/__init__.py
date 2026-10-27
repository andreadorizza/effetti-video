"""Every effect is one file in this folder. Adding one is adding a file: see docs/nuovo-effetto.md."""
import importlib, os, pkgutil

for _m in sorted(m.name for m in pkgutil.iter_modules([os.path.dirname(__file__)])):
    importlib.import_module(f'{__name__}.{_m}')
