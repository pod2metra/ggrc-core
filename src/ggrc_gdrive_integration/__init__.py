# Copyright (C) 2017 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

from flask import Blueprint

from ggrc import db             # noqa
from ggrc import settings       # noqa
from ggrc.app import app        # noqa
from ggrc.models import Document
from ggrc.models import Meeting
from ggrc.services.registry import service
from ggrc_basic_permissions.contributed_roles import RoleContributions
import ggrc_gdrive_integration.models as models
from ggrc_gdrive_integration.models.object_file import Fileable
from ggrc_gdrive_integration.models.object_event import Eventable
import ggrc_gdrive_integration.views


blueprint = Blueprint(
    'gdrive',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/ggrc_gdrive_integration',
)


Document.__bases__ = (Fileable, ) + Document.__bases__
Document.late_init_fileable()
Meeting.__bases__ = (Eventable, ) + Meeting.__bases__
Meeting.late_init_eventable()
# TODO: now the Gdrive module is dependant on the Workflows module. it used to
# be the other way around but none of them are actually okay

'''
Some other spitballs from Dan here:

Folderable.extend_class(Program)
class ExtendableMixin(object):
  _publish_attrs = [..]

  def extend_class(cls, target_cls):
    pass

class ProgramWithGDrive(registry.get_model("Program")):
  @declared_attr
  def object_folders(cls):
    pass

ggrc.services.registry["Program"] = ProgramWithGDrive
/api/blah
/api/ggrc_basic_permissions/Program

@Resource.model_get.connect_via(Program)
def augment_program(programs):
  for p in programs:
    p["object_folders"] =
'''


# Initialize views
def init_extra_views(application):
  ggrc_gdrive_integration.views.init_extra_views(application)


contributed_services = [
    service('object_files', models.ObjectFile),
    service('object_events', models.ObjectEvent)
]


class GDriveRoleContributions(RoleContributions):
  contributions = {
      'Auditor': {
          'read': ['ObjectFile', 'ObjectEvent'],
      },
      'ProgramAuditEditor': {
          'read': ['ObjectFile', 'ObjectEvent'],
          'create': ['ObjectFile', 'ObjectEvent'],
          'update': ['ObjectFile', 'ObjectEvent'],
          'delete': ['ObjectFile', 'ObjectEvent'],
      },
      'ProgramAuditOwner': {
          'read': ['ObjectFile', 'ObjectEvent'],
          'create': ['ObjectFile', 'ObjectEvent'],
          'update': ['ObjectFile', 'ObjectEvent'],
          'delete': ['ObjectFile', 'ObjectEvent'],
      },
      'ProgramAuditReader': {
          'read': ['ObjectFile', 'ObjectEvent'],
          'create': ['ObjectFile', 'ObjectEvent'],
          'delete': ['ObjectFile', 'ObjectEvent'],
      },
      'ProgramOwner': {
          'read': [],
          'create': [],
          'update': [],
          'delete': [],
      },
      'Editor': {
          'read': ['ObjectFile', 'ObjectEvent'],
          'create': ['ObjectFile', 'ObjectEvent'],
          'update': ['ObjectFile', 'ObjectEvent'],
          'delete': ['ObjectFile', 'ObjectEvent'],
      },

  }

ROLE_CONTRIBUTIONS = GDriveRoleContributions()
