# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Utility functions for string operations."""

import random
import string
import uuid

BLANK = ''
COMMA = ','  # comma is used as delimiter for multi-choice values
LESS = '<'  # need exclude this character due to issue GGRC-527
DOUBLE_QUOTES = '"'  # need exclude this character due to issue GGRC-931
BACKSLASH = '\\'  # need exclude this character due to issue GGRC-931
EXCLUDE = COMMA + LESS + DOUBLE_QUOTES + BACKSLASH
SPECIAL = BLANK.join(_ for _ in string.punctuation if _ not in EXCLUDE)


def random_string(size=5, chars=string.letters + string.digits + SPECIAL):
  """Return string with corresponding size that filled by values from selected
 chars.
 """
  return BLANK.join(random.choice(chars) for position in range(size))


def random_uuid(length=13):
  """Return string with predefined length base on UUID."""
  return str(uuid.uuid4())[:length]


def random_list_strings(list_len=3, item_size=5,
                        chars=string.letters + string.digits + SPECIAL):
  """Return list of random strings separated by comma."""
  return COMMA.join(random_string(item_size, chars) for i in range(list_len))


def get_bool_from_string(str_to_bool):
  """Return True for 'Yes' and False for 'No'."""
  if str_to_bool.title() == 'Yes':
    return True
  elif str_to_bool.title() == 'No':
    return False
  else:
    raise ValueError("'{}' can't be converted to boolean".format(str_to_bool))


def remap_keys_for_list_dicts(dict_transformation_keys, list_dicts):
  """Remap keys names for old list of dictionaries according
 transformation dictionary {OLD KEY: NEW KEY} and return new updated
 list of dictionaries.
 """
  return [{dict_transformation_keys[key]: value for key, value
           in dic.iteritems()} for dic in list_dicts]


def convert_to_list(items):
  """Converts items to list items:
  - if items are already list items then skip;
  - if are not list items then convert to list items."""
  list_items = items if isinstance(items, list) else [items, ]
  return list_items
