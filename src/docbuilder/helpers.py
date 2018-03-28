# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Template helpers."""

from textwrap import dedent


def title(text, underscore='='):
    """
  Returns ReST title.

  ..  code-block:: pycon

      >>> text = 'Hello'
      >>> print(title(text))
      Hello
      =====
      >>> print(title(text, '-'))
      Hello
      -----

  """
    return text + '\n' + underscore * len(text)


def doc(descriptor, indent=0):
    """
  Format ``doc`` attribute of ``descriptor``.

  If doc is ``None`` returns warning admonition. If ``indent`` argument
  is specified, the result will be indented by the number of spaces.

  """
    if descriptor.doc is None:
        result = dedent("""
        ..  warning::
            Missing doc-string of ``%s``
    """ % descriptor.name).strip()
    else:
        result = descriptor.doc
    return textblock(result, indent)


def textblock(text, indent=0):
    """
  Indent textblock by specified number of spaces.

  ..  code-block:: pycon

      >>> block = 'one\ntwo'
      >>> print(textblock(block))
      one
      two
      >>> print(textblock(block), 4)
          one
          two

  """
    if indent:
        return ('\n' + ' ' * indent).join(text.splitlines())
    return text
