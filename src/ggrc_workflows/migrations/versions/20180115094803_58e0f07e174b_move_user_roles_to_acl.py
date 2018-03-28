# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Move Workflow user_roles to ACL

Create Date: 2018-01-15 09:48:03.344278
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name, too-many-locals

from collections import defaultdict
from datetime import datetime
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '58e0f07e174b'
down_revision = '3355d60d65d8'

acl_table = sa.sql.table(
    'access_control_list',
    sa.sql.column('person_id', sa.Integer),
    sa.sql.column('ac_role_id', sa.Integer),
    sa.sql.column('object_id', sa.Integer),
    sa.sql.column('object_type', sa.String),
    sa.sql.column('created_at', sa.DateTime),
    sa.sql.column('modified_by_id', sa.Integer),
    sa.sql.column('updated_at', sa.DateTime),
    sa.sql.column('context_id', sa.Integer),
    sa.sql.column('parent_id', sa.Integer),
)

_NOW = datetime.utcnow()

INSERT_CHUNK = 1000


def _get_acrs(conn):
    """Return dict of possible ACL."""
    rows = conn.execute("""
      SELECT id, name
      FROM access_control_roles
      WHERE object_type = "Workflow"
      """)
    # ACR.name to ACR.id + ACR.id to ACR.name mapping
    acrs = dict()
    for pacl in rows:
        acrs[pacl['name']] = pacl['id']
        acrs[pacl['id']] = pacl['name']
    return acrs


def _insert_parents(conn, acrs):
    """Procedure to insert parent roles."""
    rows = conn.execute("""
      SELECT id, name
      FROM roles
      WHERE name IN ("WorkflowOwner", "WorkflowMember")
      """)
    roles = {row['name']: row['id'] for row in rows}
    # Deprecated Workflow Role.id to new AccessControlRole.name mapping
    role_id_to_acr = {
        roles['WorkflowOwner']: 'Admin',
        roles['WorkflowMember']: 'Workflow Member'
    }
    # Create parent ACL records
    rows = conn.execute("""
      SELECT ur.role_id, ur.person_id, w.id, w.modified_by_id, w.context_id
      FROM user_roles AS ur
      INNER JOIN workflows AS w ON ur.context_id = w.context_id
      """)
    parent_acl_data = []
    for pacl in rows:
        role_id = pacl['role_id']
        acr_name = role_id_to_acr[role_id]
        parent_acl_data.append({
            'person_id': pacl['person_id'],
            'ac_role_id': acrs[acr_name],
            'object_id': pacl['id'],
            'object_type': 'Workflow',
            'created_at': _NOW,
            'modified_by_id': pacl['modified_by_id'],
            'updated_at': _NOW,
            'context_id': pacl['context_id'],
            'parent_id': None
        })
        if len(parent_acl_data) == INSERT_CHUNK:
            op.bulk_insert(acl_table, parent_acl_data)
            parent_acl_data = []
    op.bulk_insert(acl_table, parent_acl_data)


def _insert_context_based(conn, acrs):
    """Procedure to insert context based roles."""
    # Query created parent ACL records. Need id for parent_id in related ACL.
    rows = conn.execute("""
      SELECT id, person_id, ac_role_id, object_id, modified_by_id, context_id
      FROM access_control_list
      WHERE object_type = "Workflow"
      """)
    parent_acl = defaultdict(list)
    for pacl in rows:
        parent_acl[pacl['context_id']].append({
            'id':
            pacl['id'],
            'person_id':
            pacl['person_id'],
            'ac_role_id':
            pacl['ac_role_id'],
            'object_id':
            pacl['object_id'],
            'modified_by_id':
            pacl['modified_by_id']
        })

    # Create related ACL records based on `parent_acl`
    rows = conn.execute("""
      SELECT "TaskGroup" AS rtype, id, context_id
      FROM task_groups
      UNION
      SELECT "TaskGroupTask", id, context_id
      FROM task_group_tasks
      UNION
      SELECT "Cycle", id, context_id
      FROM cycles
      UNION
      SELECT "CycleTaskGroup", id, context_id
      FROM cycle_task_groups
      UNION
      SELECT "CycleTaskGroupObjectTask", id, context_id
      FROM cycle_task_group_object_tasks
      UNION
      SELECT "CycleTaskEntry", id, context_id
      FROM cycle_task_entries
      UNION
      SELECT "TaskGroupObject", id, context_id
      FROM task_group_objects
      """)
    related_acl_data = []
    for related in rows:
        context_id = related['context_id']
        for pacl in parent_acl[context_id]:
            parent_acr_id = pacl['ac_role_id']
            parent_acr_name = acrs[parent_acr_id]
            rel_acr_name = "{} Mapped".format(parent_acr_name)
            rel_acr_id = acrs[rel_acr_name]
            related_acl_data.append({
                'person_id': pacl['person_id'],
                'ac_role_id': rel_acr_id,
                'object_id': related['id'],
                'object_type': related['rtype'],
                'created_at': _NOW,
                'modified_by_id': pacl['modified_by_id'],
                'updated_at': _NOW,
                'context_id': context_id,
                'parent_id': pacl['id']
            })
            if len(related_acl_data) == INSERT_CHUNK:
                op.bulk_insert(acl_table, related_acl_data)
                related_acl_data = []
    op.bulk_insert(acl_table, related_acl_data)


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    conn = op.get_bind()
    acrs = _get_acrs(conn)
    _insert_parents(conn, acrs)
    _insert_context_based(conn, acrs)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute("""
      DELETE
      FROM access_control_list
      WHERE ac_role_id IN
        (SELECT id FROM access_control_roles WHERE object_type = "Workflow")
      """)
