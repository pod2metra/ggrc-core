# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Handle the interface to GGRC models for all login methods.
"""


def get_next_url(request, default_url):
    """Returns next url from requres or default url if it's not found."""
    if 'next' in request.args:
        next_url = request.args['next']
        return next_url
    else:
        return default_url
