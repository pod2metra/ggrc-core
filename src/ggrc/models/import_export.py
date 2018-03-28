# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
""" ImportExport model."""

from sqlalchemy.dialects import mysql

from ggrc import db
from ggrc.models.mixins.base import Identifiable


class ImportExport(Identifiable, db.Model):
    """ImportExport Model."""

    __tablename__ = 'import_exports'

    IMPORT_EXPORT_STATUSES = [
        'Not Started',
        'Analysis',
        'In Progress',
        'Blocked',
        'Analysis Failed',
        'Stopped',
        'Failed',
        'Finished',
    ]

    job_type = db.Column(db.Enum('Import', 'Export'), nullable=False)
    status = db.Column(
        db.Enum(*IMPORT_EXPORT_STATUSES),
        nullable=False,
        default='Not Started')
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False)
    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    created_by_id = db.Column(
        db.Integer, db.ForeignKey('people.id'), nullable=False)
    created_by = db.relationship(
        'Person', foreign_keys='ImportExport.created_by_id', uselist=False)
    results = db.Column(mysql.LONGTEXT)
    title = db.Column(db.Text),
    content = db.Column(mysql.LONGTEXT)
    gdrive_metadata = db.Column('gdrive_metadata', db.Text)
