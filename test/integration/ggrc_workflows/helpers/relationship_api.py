# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Relationship related helper functions for REST API calls."""

from ggrc import utils


def get_relationship_post_dict(source, destination):
    """Get Relationship JSON representation for POST API call.

    Args:
        source: Relationship source instance.
        destination: Relationship destination instance
    Returns:
        Relationship object dict representation for using in POST request.
    """
    return {
        "relationship": {
            "source": utils.create_stub(source),
            "destination": utils.create_stub(destination),
            "context": utils.create_stub(source.context),
        }
    }
