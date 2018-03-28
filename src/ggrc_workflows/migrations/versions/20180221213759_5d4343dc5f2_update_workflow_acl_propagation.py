# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
update workflow acl propagation

NOTE:

This code is mostly copy pasted from
 - src/ggrc_workflows/models/hooks/workflow.py

The changes here are just for deleting all propagated roles and tables are
reflected instead of created from our models.

Create Date: 2018-02-21 21:37:59.908381
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '5d4343dc5f2'
down_revision = '54418614dec4'

object_name_map = {
    "AccessControlRole": "access_control_roles",
    "AccessControlList": "access_control_list",
    "Workflow": "workflows",
    "TaskGroup": "task_groups",
    "TaskGroupTask": "task_group_tasks",
    "TaskGroupObject": "task_group_objects",
    "Cycle": "cycles",
    "CycleTaskGroup": "cycle_task_groups",
    "CycleTaskGroupObjectTask": "cycle_task_group_object_tasks",
    "CycleTaskEntry": "cycle_task_entries",
}

WF_PROPAGATED_ROLES = {
    "Admin",
    "Workflow Member",
}

WF_PROPAGATED_ROLES_MAPPED = {
    "Admin Mapped",
    "Workflow Member Mapped",
}


def _get_child_ids(meta, parent_ids, child_type):
    """Get all acl ids for acl entries with the given parent ids

  Args:
    parent_ids: list of parent acl entries or query with parent ids.

  Returns:
    list of ACL ids for all children from the given parents.
  """
    acl = meta.tables["access_control_list"]
    return sa.select([acl.c.id]).where(
        acl.c.parent_id.in_(parent_ids)).where(acl.c.object_type == child_type)


def _insert_select_acls(meta, select_statement):
    """Insert acl records from the select statement

  Args:
    select_statement: sql statement that contains the following columns
      person_id,
      ac_role_id,
      object_id,
      object_type,
      created_at,
      updated_at,
      parent_id,
  """

    acl = meta.tables["access_control_list"]

    inserter = acl.insert().prefix_with("IGNORE")

    op.execute(
        inserter.from_select([
            acl.c.person_id,
            acl.c.ac_role_id,
            acl.c.object_id,
            acl.c.object_type,
            acl.c.created_at,
            acl.c.updated_at,
            acl.c.parent_id,
        ], select_statement))


def _propagate_to_wf_children(meta, new_wf_acls, child_type):
    """Propagate newly added roles to workflow objects.

  Args:
    wf_new_acl: list of all newly created acl entries for workflows

  Returns:
    list of newly created acl entries for task groups.
  """

    child_table = meta.tables[object_name_map[child_type]]
    acl = meta.tables["access_control_list"]
    acr = meta.tables["access_control_roles"].alias("parent_acr")
    acr_mapped_table = meta.tables["access_control_roles"].alias("mapped")

    select_statement = sa.select([
        acl.c.person_id,
        acr_mapped_table.c.id,
        child_table.c.id,
        sa.literal(child_type),
        sa.func.now(),
        sa.func.now(),
        acl.c.id,
    ]).select_from(
        sa.join(
            sa.join(
                sa.join(child_table, acl,
                        sa.and_(
                            acl.c.object_id == child_table.c.workflow_id,
                            acl.c.object_type == "Workflow",
                        )),
                acr,
            ), acr_mapped_table, acr_mapped_table.c.name == sa.func.concat(
                acr.c.name, " Mapped"))).where(acl.c.id.in_(new_wf_acls))

    _insert_select_acls(meta, select_statement)

    return _get_child_ids(meta, new_wf_acls, child_type)


def _propagate_to_children(meta, new_tg_acls, child_type, id_name,
                           parent_type):
    """Propagate new acls to objects related to task groups

  Args:
    new_tg_acls: list of ids of newly created acl entries for task groups

  Returns:
    list of ids for newy created task group task or task group object entries.
  """

    child_table = meta.tables[object_name_map[child_type]]
    acl = meta.tables["access_control_list"]

    parent_id_filed = getattr(child_table.c, id_name)

    select_statement = sa.select([
        acl.c.person_id,
        acl.c.ac_role_id,
        child_table.c.id,
        sa.literal(child_type),
        sa.func.now(),
        sa.func.now(),
        acl.c.id,
    ]).select_from(
        sa.join(child_table, acl,
                sa.and_(
                    acl.c.object_id == parent_id_filed,
                    acl.c.object_type == parent_type,
                ))).where(acl.c.id.in_(new_tg_acls), )

    _insert_select_acls(meta, select_statement)

    return _get_child_ids(meta, new_tg_acls, child_type)


def _propagate_to_tgt(meta, new_tg_acls):
    """Propagate ACL entries to task groups tasks.

  Args:
    new_tg_acls: list of propagated ACL ids that belong to task_groups.
  """
    print "Propagating roles to task groups tasks"
    return _propagate_to_children(
        meta,
        new_tg_acls,
        "TaskGroupTask",
        "task_group_id",
        "TaskGroup",
    )


def _propagate_to_tgo(meta, new_tg_acls):
    """Propagate ACL entries to task groups objects.

  Args:
    new_tg_acls: list of propagated ACL ids that belong to task_groups.
  """
    print "Propagating roles to task groups objects"
    return _propagate_to_children(
        meta,
        new_tg_acls,
        "TaskGroupObject",
        "task_group_id",
        "TaskGroup",
    )


def _propagate_to_ctg(meta, new_cycle_acls):
    """Propagate ACL entries to cycle task groups and its children.

  Args:
    new_ctg_acls: list of propagated ACL ids that belong to cycles.
  """
    print "Propagating roles to cycle task groups"
    new_ctg_acls = _propagate_to_children(
        meta,
        new_cycle_acls,
        "CycleTaskGroup",
        "cycle_id",
        "Cycle",
    )

    _propagate_to_cycle_tasks(meta, new_ctg_acls)


def _propagate_to_cycle_tasks(meta, new_ctg_acls):
    """Propagate ACL roles to cycle tasks and its children.

  Args:
    new_ctg_acls: list of propagated ACL ids that belong to cycle task groups.
  """
    print "Propagating roles to cycle task groups object tasks"
    new_ct_acls = _propagate_to_children(
        meta,
        new_ctg_acls,
        "CycleTaskGroupObjectTask",
        "cycle_task_group_id",
        "CycleTaskGroup",
    )

    _propagate_to_cte(meta, new_ct_acls)


def _propagate_to_cte(meta, new_ct_acls):
    """Propagate ACL roles from cycle tasks to cycle tasks entries.

  Args:
    new_ct_acls: list of propagated ACL ids that belong to cycle tasks.
  """
    print "Propagating roles to cycle task entries"
    return _propagate_to_children(
        meta,
        new_ct_acls,
        "CycleTaskEntry",
        "cycle_task_group_object_task_id",
        "CycleTaskGroupObjectTask",
    )


def _propagate_to_tg(meta, new_wf_acls):
    """Propagate workflow ACL roles to task groups and its children.

  Args:
    new_wf_acls: List of ACL ids on a workflow that should be propagated.
  """
    print "Propagating roles to task groups"
    new_tg_acls = _propagate_to_wf_children(meta, new_wf_acls, "TaskGroup")

    _propagate_to_tgt(meta, new_tg_acls)

    _propagate_to_tgo(meta, new_tg_acls)


def _propagate_to_cycles(meta, new_wf_acls):
    """Propagate workflow ACL roles to cycles and its children.

  Args:
    new_wf_acls: List of ACL ids on a workflow that should be propagated.
  """
    print "Propagating roles to cycles"
    new_cycle_acls = _propagate_to_wf_children(meta, new_wf_acls, "Cycle")

    _propagate_to_ctg(meta, new_cycle_acls)


def _propagate_new_wf_acls(meta, new_wf_acls):
    """Propagate ACL entries that were added to workflows.

  Args:
    new_wf_acls: List of ACL ids on a workflow that should be propagated.
  """

    _propagate_to_tg(meta, new_wf_acls)

    _propagate_to_cycles(meta, new_wf_acls)


def _add_propagated_roles(meta):
    """Add propagated roles to workflow related objects."""
    acl = meta.tables["access_control_list"]
    acr = meta.tables["access_control_roles"]

    wf_acl_query = sa.select([acl.c.id]).where(
        acl.c.ac_role_id.in_(
            sa.select([acr.c.id]).where(acr.c.name.in_(WF_PROPAGATED_ROLES))))
    print "Propagating all workflow roles."
    _propagate_new_wf_acls(meta, wf_acl_query)


def _remove_propagated_roles(meta):
    """Remove all workflow propagated acl entries."""
    acl = meta.tables["access_control_list"]
    acr = meta.tables["access_control_roles"]
    print "Removing all propagated workflow roles"

    op.execute(acl.delete().where(
        acl.c.ac_role_id.in_(
            sa.select([acr.c.id]).where(
                acr.c.name.in_(WF_PROPAGATED_ROLES_MAPPED)))))


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    bind = op.get_bind()
    meta = sa.MetaData()
    meta.reflect(bind=bind)

    _remove_propagated_roles(meta)

    _add_propagated_roles(meta)


def downgrade():
    """The migration does not require downgrade changes.

  Since we just fix parent states and the previous code does not rely on those
  we don't have to do any modifications for downgrade migration.
  """
