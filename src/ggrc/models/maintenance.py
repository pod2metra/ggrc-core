# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Models for maintenance."""

from ggrc import db
from ggrc.models.mixins.base import Identifiable


class Maintenance(Identifiable, db.Model):
    """Maintenance
  Model holds flags. These flags will be used on migration, reindex, revision
  refresh and computed attribute.
  """
    __tablename__ = 'maintenance'

    under_maintenance = db.Column(db.Boolean, nullable=False, default=False)


class MigrationLog(Identifiable, db.Model):
    """Model holds migration related details and logs."""
    __tablename__ = 'migration_log'

    down_version_num = db.Column(db.String)
    version_num = db.Column(db.String)
    is_migration_complete = db.Column(db.Boolean, nullable=False, default=True)
    log = db.Column(db.String)


class RevisionRefreshLog(Identifiable, db.Model):
    """Model holds revision refresh details and logs."""
    __tablename__ = 'revision_refresh_log'

    run_revision_refresh = db.Column(db.Boolean, nullable=False, default=False)
    is_revision_refresh_complete = db.Column(
        db.Boolean, nullable=False, default=True)
    log = db.Column(db.String)


class ReindexLog(Identifiable, db.Model):
    """Model holds reindex details and logs."""
    __tablename__ = 'reindex_log'

    is_reindex_complete = db.Column(db.Boolean, nullable=False, default=True)
    log = db.Column(db.String)
