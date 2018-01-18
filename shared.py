#!/usr/bin/env python3
import json
import os
from os.path import dirname, abspath, realpath
import re
from urllib.parse import urlencode

from aqt import mw

# haoxuany - other plugins please do not touch

## Path Defaults
s_CURRENT_DIR = dirname(abspath(realpath(__file__)))
def path_to(*args):
  return os.path.join(s_CURRENT_DIR, *args)
def config_path(*args):
  return path_to("user_files", *args)

## Page Requests
# haoxuany - grabbed from
# http://www.useragentstring.com/pages/useragentstring.php?name=Chrome
# hopefully good enough
s_GENERIC_USER_AGENT = \
  "Mozilla/5.0 (Windows NT 6.1) "\
  "AppleWebKit/537.36 (KHTML, like Gecko) "\
  "Chrome/41.0.2228.0 "\
  "Safari/537.36"

d_s_SEND_HEADERS = \
  { "User-Agent" : s_GENERIC_USER_AGENT
  }

# Config Files
s_CONFIG = config_path("config.json")
s_NETWORK_CONFIG = config_path("netconfig.json")

# type Config = (string, dyn) dictionary
# type Config' = (string, dyn option) dictionary

# Config Defaults
config_netconfigdefault = \
  { "use_system_proxy" : True # bool
  , "proxy_addr" : "http://127.0.0.1" # string
  , "proxy_port" : 1087 # int
  , "assign_https_context" : False # bool
  }

config_mainconfigdefault = \
  {
  }

config_netconfig = None
config_mainconfig = None

# Scrapping Defaults
# string -> string
def image_search_url(s_query):
  s_search_url = "https://www.google.com/search"
  d_s_params = \
    { "authuser" : "0"
    , "tbm" : "isch"
    , "query" : s_query
    }
  return s_search_url + "?" + urlencode(d_s_params)

# haoxuany - observed page format for Google Images
s_GIMG_META_HEADER = r"\<div[^\>]*?class[^\>]*?rg_meta[^\>]*?\>"
s_GIMG_META_FOOTER = r"\<\/div\>"
reobj_GIMG_META = re.compile(
  s_GIMG_META_HEADER +
  r"(.*?)" +
  s_GIMG_META_FOOTER)
s_GIMG_META_URL_FIELD = u"ou"

# string -> string list
def scrape_image_urls(s_content):
  l_s_meta = reobj_GIMG_META.findall(s_content)
  l_s_urls = []
  for s_json_elem in l_s_meta:
    try:
      d_meta = json.loads(s_json_elem)
      if s_GIMG_META_URL_FIELD in d_meta:
        l_s_urls.append(d_meta[s_GIMG_META_URL_FIELD])
    except json.JSONDecodeError:
      pass
  return l_s_urls

## Image Fetch Defaults
i_BUFFER_LEN = 2
i_THREAD_TIMEOUT = 7

## Note Manipulation Defaults
s_IMAGE_SEARCH_ID = "imgsearch"
# haoxuany - oh lord
# this main reason this is so convoluted is that
# this is the only thing i tried that actually works lol
s_IMAGE_REPLACE_JS = \
'''var image = document.getElementById("%s");
if (image)
{
  var elem = document.createElement('div');
  elem.innerHTML = '%s';
  image.replaceWith(elem.firstChild);
}
else { setFormat('inserthtml', '%s'); }'''

# string -> string
def image_insert_js(s_imgtag):
  return s_IMAGE_REPLACE_JS % \
    (s_IMAGE_SEARCH_ID, s_imgtag, s_imgtag)

# string -> string
def image_tag(s_fname):
  d_s_meta = \
    { "src" : s_fname
    , "id" : s_IMAGE_SEARCH_ID
    }

  l_s_tag_components = \
    ['%s="%s"' % (s_key, s_val) for s_key, s_val in d_s_meta.items()]

  return "<img " + " ".join(l_s_tag_components) + ">"

# Note -> string * int
def get_src_str_dst_field(note):
  s_model_name = note.model()['name'].lower()
  l_s_fields = mw.col.models.fieldNames(note.model())

  i_query_field = 0
  i_dest_field = 1

  # haoxuany - grabbed from the japanese plugin
  if "japanese" in s_model_name:
    i_query_field = l_s_fields.index("Expression")
    i_dest_field = l_s_fields.index("Meaning")
  else:
    # haoxuany - yolo here, first two fields probably good enough
    i_query_field = 0
    i_dest_field = 1

  return (note.fields[i_query_field], i_dest_field)

## UI Defaults
s_PROXY_WARN = \
'''Warning: These changes will apply to all calls to urlopen in urllib.request,
although if you need to mess with these settings you probably need them for all requests anyway.
If you need a complicated proxy setup, you should probably use a management tool. Proceed with caution.'''
s_PROXY_HTTPS_VERIFY_BYPASS_INFO = \
"You will likely want this, but disabled by default for security reasons. "\
"For more information, see <a href=\""\
"https://stackoverflow.com/questions/27835619/"\
"urllib-and-ssl-certificate-verify-failed-error"\
"\">this</a> and <a href=\""\
"https://bugs.python.org/issue28414"\
"\">this</a>."

s_GOOGLE_IMG = path_to("images", "powered_by_google_on_white.png")

s_ABOUT = \
'''You can track project progress and updates on
<a href="https://github.com/haoxuany/anki_image_search">GitHub</a>. <br>
I don't think this actually violates Google's Terms of Service, <br>
but just in case, and since Google is pretty awesome anyway,
here's the Powered by Google logo:<br>
<img src="%s" /><br>
Editor icons are provided by
<a href="https://useiconic.com/open">Open Iconic</a>
, and licensed under the MIT License. <br>
The entire project (Anki Image Search) is licensed under GPL version 2.
''' % s_GOOGLE_IMG

s_SEARCH_IMAGE_SHORTCUT = "Ctrl+/"
s_PREV_IMAGE_SHORTCUT = "Ctrl+Left"
s_NEXT_IMAGE_SHORTCUT = "Ctrl+Right"
