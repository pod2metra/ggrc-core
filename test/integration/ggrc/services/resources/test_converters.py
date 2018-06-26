# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""Tests for import/export endpoints.

Endpoints:

  - /api/people/person_id/imports
  - /api/people/person_id/exports

"""

import json

from datetime import datetime

import threading
import ddt
import mock

from google.appengine.ext import deferred

from ggrc import db
from ggrc.models import all_models

from integration.ggrc import api_helper
from integration.ggrc.models import factories
from integration.ggrc.services import TestCase


@ddt.ddt
class TestImportExports(TestCase):
  """Tests for imports/exports endpoints."""

  def setUp(self):
    super(TestImportExports, self).setUp()
    self.client.get("/login")
    self.headers = {
        "Content-Type": "application/json",
        "X-Requested-By": ["GGRC"],
    }
    self.api = api_helper.Api()
    self.init_taskqueue()

  def run_full_import(self, user, imp_exp_obj):
    """Emulate full cycle of data importing.

    Args:
        user: User object under which import should be run.
        imp_exp_obj: Instance of ImportExport containing data
          should be imported.
    """
    response = self.client.put(
        "/api/people/{}/imports/{}/start".format(user.id, imp_exp_obj.id),
        headers=self.headers,
    )
    self.assert200(response)

    tasks = self.taskqueue_stub.get_filtered_tasks()
    self.assertEqual(len(tasks), 1)

    def run_task():
      """Run deferred import job."""
      # check_for_previous_run is mocked as we don't use webapp2
      # in test environment
      with mock.patch("ggrc.views.converters.check_for_previous_run"):
        deferred.run(tasks[0].payload)

    # Run import job in separate thread to emulate work of appengine queue
    task_thread = threading.Thread(target=run_task, args=())
    task_thread.start()
    task_thread.join()

  @mock.patch("ggrc.gdrive.file_actions.get_gdrive_file_data",
              new=lambda x: (x, None, None))
  def test_failed_imports_post(self):
    """Test imports post"""
    user = all_models.Person.query.first()
    data = [
        ['Object type'],
        ['invalid control', 'Title'],
        ['', 'Title'],
        [],
        [],
        ['Object type'],
        ['Control', 'Title'],
        ['', 'Title'],
        [],
        ['Object type'],
        ['Assessment', 'Title'],
        ['', 'Title'],
        [],
    ]
    response = self.client.post(
        "/api/people/{}/imports".format(user.id),
        data=json.dumps(data),
        headers=self.headers)
    self.assert200(response)
    self.assertFalse(response.json["objects"])
    self.assertEqual(response.json["import_export"]["status"],
                     "Analysis Failed")
    self.assertEqual(len(response.json["import_export"]["results"]), 3)
    for block in response.json["import_export"]["results"]:
      if block["name"] == "":
        self.assertEqual(block["rows"], 1)
        self.assertIn(u"Line 2", block["block_errors"][0])
      else:
        self.assertEqual(block["rows"], 1)
        self.assertFalse(block["block_errors"])

  @mock.patch("ggrc.gdrive.file_actions.get_gdrive_file_data",
              new=lambda x: (x, None, None))
  def test_imports_post(self):
    """Test imports post"""
    user = all_models.Person.query.first()
    data = [
        ['Object type'],
        ['CONTROL', 'Title'],
        ['', 'Title1'],
        ['', 'Title2'],
        [],
        ['Object type'],
        ['Control', 'Title'],
        ['', 'Title3'],
        [],
        ['Object type'],
        ['Assessment', 'Title'],
        ['', 'Title3'],
        [],
        ['Object type'],
        ['Audit', 'Title'],
        ['', ''],
    ]
    response = self.client.post(
        "/api/people/{}/imports".format(user.id),
        data=json.dumps(data),
        headers=self.headers)
    self.assert200(response)
    self.assertEqual(response.json["import_export"]["status"], "Not Started")
    self.assertEqual(response.json["objects"]["Assessment"], 1)
    self.assertEqual(response.json["objects"]["Control"], 3)

  @ddt.data("Import", "Export")
  def test_get(self, job_type):
    """Test imports/exports get"""
    user = all_models.Person.query.first()
    ie1 = factories.ImportExportFactory(job_type=job_type,
                                        created_by=user,
                                        created_at=datetime.now())
    factories.ImportExportFactory(job_type=job_type,
                                  created_by=user,
                                  created_at=datetime.now())
    response = self.client.get(
        "/api/people/{}/{}s/{}".format(user.id, job_type.lower(), ie1.id),
        headers=self.headers)
    self.assert200(response)
    self.assertEqual(response.json["id"], ie1.id)

    response = self.client.get(
        "/api/people/{}/{}s".format(user.id, job_type.lower()),
        headers=self.headers)
    self.assert200(response)
    self.assertEqual(len(response.json), 2)

    response = self.client.get(
        "/api/people/{}/{}s?id__in={}".format(user.id, job_type.lower(),
                                              ie1.id),
        headers=self.headers)
    self.assert200(response)
    self.assertEqual(response.json[0]["id"], ie1.id)

  def test_imports_put(self):
    """Test imports put"""
    user = all_models.Person.query.first()
    ie1 = factories.ImportExportFactory(job_type="Import",
                                        status="Not Started",
                                        created_by=user,
                                        created_at=datetime.now())
    response = self.client.put(
        "/api/people/{}/imports/{}/start".format(user.id, ie1.id),
        headers=self.headers)
    self.assert200(response)
    self.assertEqual(response.json["id"], ie1.id)
    self.assertEqual(response.json["status"], "Analysis")

  def test_imports_get_all(self):
    """Test imports get all items"""
    user = all_models.Person.query.first()
    factories.ImportExportFactory(job_type="Import",
                                  status="Finished",
                                  created_by=user,
                                  created_at=datetime.now())
    response = self.api.client.get(
        "/api/people/{}/imports".format(user.id),
        headers=self.headers
    )
    result = json.loads(response.data)
    self.assertEqual(len(result), 1)
    self.assertEqual(set(all_models.ImportExport.DEFAULT_COLUMNS),
                     set(result[0].keys()))

  def test_imports_get_by_id(self):
    """Test imports get item by id"""
    user = all_models.Person.query.first()
    import_job = factories.ImportExportFactory(
        job_type="Import",
        status="Finished",
        created_by=user,
        created_at=datetime.now()
    )
    response = self.api.client.get(
        "/api/people/{}/imports/{}".format(user.id, import_job.id),
        headers=self.headers
    )
    result = json.loads(response.data)
    observed_columns = set(result.keys())
    expected_columns = set(
        column.name for column in all_models.ImportExport.__table__.columns
        if column.name not in ('content', 'gdrive_metadata')
    )
    self.assertEqual(observed_columns, expected_columns)

  @ddt.data("Import", "Export")
  def test_delete(self, job_type):
    """Test imports/exports delete"""
    user = all_models.Person.query.first()
    ie1 = factories.ImportExportFactory(job_type=job_type,
                                        created_by=user,
                                        created_at=datetime.now())

    response = self.client.delete(
        "/api/people/{}/{}s/{}".format(user.id, job_type.lower(), ie1.id),
        headers=self.headers)
    self.assert200(response)
    self.assertIsNone(all_models.ImportExport.query.get(ie1.id))

  def test_exports_post(self):
    """Test exports post"""
    user = all_models.Person.query.first()
    assessment = factories.AssessmentFactory()
    response = self.client.post(
        "/api/people/{}/exports".format(user.id),
        data=json.dumps({
            "objects": [{
                "object_name": "Assessment",
                "ids": [assessment.id]}],
            "current_time": str(datetime.now())}),
        headers=self.headers)
    self.assert200(response)

  @ddt.data("Import", "Export")
  def test_download(self, job_type):
    """Test imports/exports download"""
    user = all_models.Person.query.first()
    ie1 = factories.ImportExportFactory(
        job_type=job_type,
        status="Finished",
        created_at=datetime.now(),
        created_by=user,
        title="test.csv",
        content="test content")
    response = self.client.get(
        "/api/people/{}/{}s/{}/download?export_to=csv".format(
            user.id,
            job_type.lower(),
            ie1.id),
        headers=self.headers)
    self.assert200(response)
    self.assertEqual(response.data, "test content")

  @ddt.data(("Import", "Analysis"),
            ("Export", "In Progress"))
  @ddt.unpack
  def test_import_stop(self, job_type, status):
    """Test import/export stop"""
    user = all_models.Person.query.first()
    ie1 = factories.ImportExportFactory(
        job_type=job_type,
        status=status,
        created_at=datetime.now(),
        created_by=user,
        title="test.csv",
        content="test content")
    response = self.client.put(
        "/api/people/{}/{}s/{}/stop".format(user.id,
                                            job_type.lower(),
                                            ie1.id),
        headers=self.headers)
    self.assert200(response)
    self.assertEqual(json.loads(response.data)["status"], "Stopped")

  @ddt.data(("Not Started", True),
            ("Blocked", True),
            ("Finished", False))
  @ddt.unpack
  @mock.patch("ggrc.gdrive.file_actions.get_gdrive_file_data",
              new=lambda x: (x, None, None))
  def test_delete_previous_imports(self, status, should_be_none):
    """Test deletion of previous imports"""
    user = all_models.Person.query.first()
    ie_item = factories.ImportExportFactory(
        job_type="Import",
        status=status,
        created_at=datetime.now(),
        created_by=user).id

    response = self.client.post(
        "/api/people/{}/imports".format(user.id),
        data=json.dumps([]),
        headers=self.headers)

    self.assert200(response)
    if should_be_none:
      self.assertIsNone(all_models.ImportExport.query.get(ie_item))
    else:
      self.assertIsNotNone(all_models.ImportExport.query.get(ie_item))

    ie_item_in_progress = factories.ImportExportFactory(
        job_type="Import",
        status="In Progress",
        created_at=datetime.now(),
        created_by=user).id
    response = self.client.post(
        "/api/people/{}/imports".format(user.id),
        data=json.dumps([]),
        headers=self.headers)
    self.assert400(response)
    self.assertIsNotNone(all_models.ImportExport.query.get(
        ie_item_in_progress))

  @mock.patch(
      "ggrc.gdrive.file_actions.get_gdrive_file_data",
      new=lambda x: (x, None, None)
  )
  def test_import_control_revisions(self):
    """Test if new revisions created during import."""
    data = "Object type,,,\n" \
           "Control,Code*,Title*,Admin*\n" \
           ",,Test control,user@example.com"

    user = all_models.Person.query.first()
    imp_exp = factories.ImportExportFactory(
        job_type="Import",
        status="Blocked",
        created_by=user,
        created_at=datetime.now(),
        content=data,
    )

    self.run_full_import(user, imp_exp)
    # We need to reopen session to grab newly created data
    db.session.close()

    control = all_models.Control.query.filter_by(title="Test control").first()
    self.assertIsNotNone(control)
    revision_actions = db.session.query(all_models.Revision.action).filter(
        all_models.Revision.resource_type == "Control",
        all_models.Revision.resource_id == control.id
    )
    self.assertEqual({"created"}, {a[0] for a in revision_actions})

  @mock.patch(
      "ggrc.gdrive.file_actions.get_gdrive_file_data",
      new=lambda x: (x, None, None)
  )
  def test_import_snapshot(self):
    """Test if snapshots can be created from imported objects."""
    data = "Object type,,,\n" \
           "Control,Code*,Title*,Admin*\n" \
           ",,Control1,user@example.com\n" \
           ",,Control2,user@example.com\n" \
           ",,Control3,user@example.com"

    user = all_models.Person.query.first()
    with factories.single_commit():
      imp_exp = factories.ImportExportFactory(
          job_type="Import",
          status="Blocked",
          created_at=datetime.now(),
          created_by=user,
          content=data,
      )
      audit_id = factories.AuditFactory().id

    self.run_full_import(user, imp_exp)
    # We need to reopen session to grab newly created data
    db.session.close()

    controls = all_models.Control.query
    self.assertEqual(3, controls.count())

    audit = all_models.Audit.query.get(audit_id)
    snapshots = self._create_snapshots(audit, controls.all())
    self.assertEqual(3, len(snapshots))
