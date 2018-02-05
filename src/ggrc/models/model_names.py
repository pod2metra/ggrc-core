# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

""" Model for labels association table."""

from ggrc import db
from ggrc.models import mixins


class Model(mixins.base.Identifiable, db.Model):
  """Represent model names."""
  __tablename__ = 'models'

  name = db.Column(db.String, nullable=False, unique=True)
