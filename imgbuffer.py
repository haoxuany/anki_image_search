#!/usr/bin/env python3
from threading import *

from . import shared
from .log import *
from .download import *
from .imglist import *

# ImgBuffer -> int -> unit
def load_image(ib_buffer, i_index):
  (bsoo_response, so_error) = \
      fetch_page(ib_buffer.l_s_url[i_index])
  ib_buffer.l_bsoo_images[i_index] = bsoo_response

class ImgBuffer:
  def __init__(self, s_query):
    # haoxuany - pretend that you're in a nonshitty language
    # for a moment and these are products as we know it
    self.s_query = s_query
    self.l_s_url = fetch_image_list(s_query)
    self.i_len = len(self.l_s_url)
    self.i_index = 0
    self.l_bsoo_images = [None] * self.i_len # haoxuany - python b.s. lol
    self.l_to_threads = [None] * self.i_len
    if self.i_len > 0:
      self.load(0)

  def __str__(self):
    return "Query of '%s' with %d results" % (self.s_query, self.i_len)

  # int -> unit
  def load(self, i_index):
    i_low = max(self.i_index - shared.i_BUFFER_LEN, 0)
    i_high = min(self.i_index + shared.i_BUFFER_LEN + 1, self.i_len)
    for i_idx in range(i_low, i_high):
      if self.l_bsoo_images[i_idx]:
        continue
      elif self.l_to_threads[i_idx]:
        if self.l_to_threads[i_idx].is_alive():
          continue
        else:
          # haoxuany - confusing docs, but probably means fetch failed
          # and we should just try again.
          pass
      else:
        # no threads run in the first place, restart
        pass
      self.l_to_threads[i_idx] = \
          Thread(target=load_image, args=(self, i_idx))
      self.l_to_threads[i_idx].start()

  # unit -> (byte * string option) option
  def retrieve_current(self):
    self.load(self.i_index)

    if self.l_to_threads[self.i_index]:
      self.l_to_threads[self.i_index].join(
          timeout=shared.i_THREAD_TIMEOUT)
      # haoxuany - according to docs a thread
      # can be joined multiple times, no clue how that works

    return self.l_bsoo_images[self.i_index]

  # unit -> (byte * string option) option
  def get(self):
    i_current = self.i_index
    for i in range(i_current, self.i_len):
      self.i_index = i
      bsoo_response = self.retrieve_current()
      if bsoo_response:
        return bsoo_response
    self.i_index = i_current
    return None

  # unit -> bool
  def next(self):
    i_current = self.i_index
    for i in range(i_current + 1, self.i_len):
      self.i_index = i
      bsoo_response = self.retrieve_current()
      if bsoo_response:
        return True
    self.i_index = i_current
    return False

  # unit -> bool
  def prev(self):
    i_current = self.i_index
    for i in range(i_current - 1, -1, -1):
      self.i_index = i
      bsoo_response = self.retrieve_current()
      if bsoo_response:
        return True
    self.i_index = i_current
    return False
