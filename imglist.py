#!/usr/bin/env python3
from . import shared
from .log import *
from .download import *

# string -> string list
def fetch_image_list(s_query):
  (bsoo_image_page, so_error) = \
      fetch_page(shared.image_search_url(s_query))
  if so_error:
    report("Google Images: %s" % so_error)
    return []

  l_s_images = shared.scrape_image_urls(
      bsoo_image_page[0].decode("utf-8"))
  if l_s_images == []:
    report("Image search returned nothing, "
    "either there are no results, a network error, or outdated scraping")

  return l_s_images
