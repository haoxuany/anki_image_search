#!/usr/bin/env python3
import importlib

def report(s_err):
  if importlib.util.find_spec("aqt"):
    from aqt.utils import showWarning
    showWarning(s_err, title="Image Search")
  else:
    print(s_err)
