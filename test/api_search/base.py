# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""This module contains SingleSetupQueryAPITest class definition."""
# pylint: disable=too-many-arguments
from sqlalchemy import Column, Integer, String, Boolean

from ggrc import app  # noqa  # pylint: disable=unused-import
from ggrc import db  # noqa  # pylint: disable=unused-import
from ggrc.models import Snapshot
from integration.ggrc import TestCase
from integration.ggrc.query_helper import WithQueryApi

TEST_REPEAT_COUNT = 3
MULTIPLE_ITEMS_COUNT = 2

OPERATIONS = {
    "=": "equal",
    "!=": "not_equal",
    "~": "contains",
    "!~": "not_contains",
    "is empty": "is_empty",
}

# pylint: disable=invalid-name
snapshot_mapping = {}  # Mapping snapshot_id to object id


# pylint: disable=too-few-public-methods
class SetupData(db.Model):
    """Class containing all test cases information"""
    __tablename__ = 'setup_data'

    id = Column(Integer, primary_key=True)
    model = Column(String(100))
    operator = Column(String(30))
    field = Column(String(200))
    single = Column(Boolean, nullable=False, default=True)
    obj_id = Column(Integer)
    searchable_id = Column(Integer)
    searchable_type = Column(String(100))


# pylint: disable=too-few-public-methods
class SingleSetupQueryAPITest(TestCase, WithQueryApi):
    """
  Base Class for a test container, setting up the environment for the exact
  test fixture
  """
    _data_installed = False

    def setUp(self):
        """Set up working environment"""
        if not SingleSetupQueryAPITest._data_installed:
            SingleSetupQueryAPITest._data_installed = True
            # pylint: disable=global-statement
            global snapshot_mapping
            snapshot_mapping.update(
                db.session.query(Snapshot.id, Snapshot.child_id))

        self._custom_headers = {}
        self.client.get("/login")
