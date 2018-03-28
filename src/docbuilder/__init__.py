# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Documentation builder.

1. Generates API documentation using introspection of application objects.
2. Places generated ReST files into ``/docs/source/api``.
3. Builds generated and manually written documents into single HTML-site
   and place it into ``/docs/build/html``.

Use the following command to invoke build::

    $ build_docs

"""
