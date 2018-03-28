# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Test relationship hooks."""

import unittest

import ddt
import mock

from ggrc.models.hooks import relationship


@ddt.ddt
class TestFromSession(unittest.TestCase):
    """Test session-listener wrapper.

  Models are substituted with builtin types as they can be used for
  isinstance checks too.
  """

    N_INT = 1
    N_STR = "2"
    M_INT = 3
    M_STR = "4"
    D_INT = 5
    D_STR = "6"

    NEW = {N_INT, N_STR}
    DIRTY = {M_INT, M_STR}
    DELETED = {D_INT, D_STR}

    @staticmethod
    def target(objects):
        return list(objects)

    def setUp(self):
        super(TestFromSession, self).setUp()
        self.session = mock.Mock(
            new=self.NEW,
            dirty=self.DIRTY,
            deleted=self.DELETED,
        )

    @ddt.data(
        ((False, False, False), (), set()),
        ((False, False, False), (int, ), set()),
        ((False, False, False), (str, ), set()),
        ((False, False, False), (int, str), set()),
        ((False, False, True), (), set()),
        ((False, False, True), (int, ), {D_INT}),
        ((False, False, True), (str, ), {D_STR}),
        ((False, False, True), (int, str), {D_INT, D_STR}),
        ((False, True, False), (), set()),
        ((False, True, False), (int, ), {M_INT}),
        ((False, True, False), (str, ), {M_STR}),
        ((False, True, False), (int, str), {M_INT, M_STR}),
        ((False, True, True), (), set()),
        ((False, True, True), (int, ), {M_INT, D_INT}),
        ((False, True, True), (str, ), {M_STR, D_STR}),
        ((False, True, True), (int, str), {M_INT, M_STR, D_INT, D_STR}),
        ((True, False, False), (), set()),
        ((True, False, False), (int, ), {N_INT}),
        ((True, False, False), (str, ), {N_STR}),
        ((True, False, False), (int, str), {N_INT, N_STR}),
        ((True, False, True), (), set()),
        ((True, False, True), (int, ), {N_INT, D_INT}),
        ((True, False, True), (str, ), {N_STR, D_STR}),
        ((True, False, True), (int, str), {N_INT, N_STR, D_INT, D_STR}),
        ((True, True, False), (), set()),
        ((True, True, False), (int, ), {N_INT, M_INT}),
        ((True, True, False), (str, ), {N_STR, M_STR}),
        ((True, True, False), (int, str), {N_INT, N_STR, M_INT, M_STR}),
        ((True, True, True), (), set()),
        ((True, True, True), (int, ), {N_INT, M_INT, D_INT}),
        ((True, True, True), (str, ), {N_STR, M_STR, D_STR}),
        ((True, True, True),
         (int, str), {N_INT, N_STR, M_INT, M_STR, D_INT, D_STR}),
    )
    @ddt.unpack
    def test_from_session(self, (new, dirty, deleted), types, expected):
        """@from_session filters correct sets and types."""
        decorated = relationship.from_session(
            new=new, dirty=dirty, deleted=deleted, *types)(self.target)

        result = decorated(self.session, None, None)

        self.assertItemsEqual(result, expected)
