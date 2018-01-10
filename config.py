#!/usr/bin/env python3
import json
import os

from .log import *

# type Config = (string, dyn) dictionary
# type Config' = (string, dyn option) dictionary

# string -> Config' option
def load_config(s_fname):
  try:
    with open(s_fname, "r") as file:
      config = json.load(file)
      return config
  except (OSError, FileNotFoundError, json.JSONDecodeError):
    return None

# Config -> Config' option -> Config
def fill_config(config_default, config):
  if not config:
    return config_default
  else:
    for s_key, d_val in config_default.items():
      if s_key not in config:
        config[s_key] = d_val
    return config

# Config -> string -> unit
def write_config(config, s_fname):
  with open(s_fname, "w") as file:
    file.write(json.dumps(config))
