#!/usr/bin/env python3
from . import shared
from .download import *
from .log import *
from .imgbuffer import *

from tempfile import *

from anki.hooks import addHook
from anki.utils import stripHTMLMedia
from aqt import mw
from aqt.qt import *

# Editor -> string * string option -> string -> string
def push_media_data(editor, bbo, s_name):
  (b_data, s_suffix) = bbo
  if not s_suffix:
    s_suffix = ".bmp" # haoxuany - dunno what to do, yolo
  (i_file, s_path) = mkstemp(prefix=s_name, suffix=s_suffix)
  os.write(i_file, b_data)
  os.close(i_file)

  # haoxuany - Anki's file extension list is pretty awful, so
  # it's easier for me to just do this manually
  s_fname = editor.mw.col.media.addFile(s_path)
  try:
    os.unlink(s_path)
  except:
    pass

  return shared.image_tag(s_fname)

# Note -> string
def src_str_dst_field(note):
  (s_query, i_dest_field) = shared.get_src_str_dst_field(note)
  return (stripHTMLMedia(s_query), i_dest_field)

ibo_current_buffer = None

# Editor -> (unit -> bool) -> unit
def display_image(editor, f_buffer_succ):
  global ibo_current_buffer
  (s_query, i_dest) = src_str_dst_field(editor.note)

  if len(s_query) == 0:
    return

  b_changed = not \
    (ibo_current_buffer and ibo_current_buffer.s_query == s_query)

  if b_changed:
    mw.progress.start()
    ibo_current_buffer = ImgBuffer(s_query)
    mw.progress.finish()
  else:
    if not f_buffer_succ():
      return

  mw.progress.start()
  bboo_result = ibo_current_buffer.get()
  mw.progress.finish()
  if not bboo_result:
    report("Couldn't load any of the images")
    return

  s_imgtag = push_media_data(editor, bboo_result, s_query)
  s_script = shared.image_insert_js(s_imgtag)
  editor.web.eval("focusField(%d);" % i_dest)
  editor.web.eval(s_script)

# Editor -> unit
def search_image(editor):
  def truth():
    return True
  display_image(editor, truth)

# Editor -> unit
def previous_image(editor):
  def image_check():
    global ibo_current_buffer
    if not ibo_current_buffer.prev():
      report("Beginning of image queue")
      return False
    return True
  display_image(editor, image_check)

# Editor -> unit
def next_image(editor):
  def image_check():
    global ibo_current_buffer
    if not ibo_current_buffer.next():
      report("End of image queue")
      return False
    return True
  display_image(editor, image_check)

# string list -> Editor -> unit
def hook_image_buttons(righttopbtns, editor):
  i_more_idx = 0
  for s_btns in righttopbtns:
    if "pycmd('more')" in s_btns:
      break
    i_more_idx += 1

  l_t_ssssuu_IMAGE_BUTTONS = \
    [ ("image", "search_image", "Search Google Images",
      shared.s_SEARCH_IMAGE_SHORTCUT, search_image)
    , ("arrow-thick-left", "previous_image", "Previous Image",
      shared.s_PREV_IMAGE_SHORTCUT, previous_image)
    , ("arrow-thick-right", "next_image", "Next Image",
      shared.s_NEXT_IMAGE_SHORTCUT, next_image)
    ]

  for (s_icon, s_cmd, s_tip, s_key, func) in l_t_ssssuu_IMAGE_BUTTONS:
    s_icon_path = shared.path_to("icons", s_icon + "-2x.png")
    s_tip = _(s_tip + " (" + s_key + ")")
    righttopbtns.insert(i_more_idx, editor.addButton(
      s_icon_path, s_cmd, func, tip=s_tip, keys=s_key))
    i_more_idx += 1

  return righttopbtns

addHook("setupEditorButtons", hook_image_buttons)
