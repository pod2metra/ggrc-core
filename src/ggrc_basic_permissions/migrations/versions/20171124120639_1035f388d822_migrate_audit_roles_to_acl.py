# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Migrate audit roles to ACL

Create Date: 2017-11-16 11:54:34.683066
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from collections import namedtuple
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '1035f388d822'
down_revision = '5a7fd43e43ae'

AC_TABLE = namedtuple("AC_TABLE", "type table role parent_role")
AC_PERMISSIONS = namedtuple(
    "AC_PERMISSIONS",
    "read update delete mandatory my_work default_to_current_user object_type")
ROLES = {
    "Auditors": AC_PERMISSIONS(1, 0, 0, 0, 1, 0, "Audit"),
    "Audit Captains": AC_PERMISSIONS(1, 1, 1, 1, 1, 1, "Audit"),
}
MAPPED_ROLES = {
    "Audit Captains Mapped": AC_PERMISSIONS(1, 1, 1, 0, 0, 0, "Audit"),
    "Auditors Mapped": AC_PERMISSIONS(1, 0, 0, 0, 0, 0, "Audit"),
    "Auditors Assessment Mapped": AC_PERMISSIONS(1, 1, 0, 0, 0, 0,
                                                 "Assessment"),
    "Auditors Document Mapped": AC_PERMISSIONS(1, 1, 0, 0, 0, 0, "Document"),
    "Auditors Snapshot Mapped": AC_PERMISSIONS(1, 1, 0, 0, 0, 0, "Snapshot"),
    "Auditors Issue Mapped": AC_PERMISSIONS(1, 1, 0, 0, 0, 0, "Issue"),
}
ALL_ROLES = dict(ROLES, **MAPPED_ROLES)


def _check_new_role_names(connection):
    """Check if new role names already exist in the acr table.
     Throws an exception and stops the migratoin if they do"""
    res = connection.execute(
        text("""
          SELECT name
          FROM access_control_roles
          WHERE name IN :assignee_roles
      """),
        assignee_roles=ALL_ROLES.keys()).fetchone()

    if res:
        raise Exception("Custom Role with name '{}' already exists in db. "
                        "Migration will be stopped".format(res[0]))


def _create_new_roles(connection):
    """Inserts new roles based on ALL_ROLES list"""
    for role, permissions in ALL_ROLES.items():
        connection.execute(
            text("""
            INSERT INTO access_control_roles(
                name, object_type, created_at, updated_at, `read`, `update`,
                `delete`, mandatory, non_editable, internal, my_work,
                default_to_current_user
            )
            VALUES(
                :role, :object_type, NOW(), NOW(), :read, :update,
                :delete, :mandatory, :non_editable, :internal, :my_work,
                :default_to_current_user
            );
        """),
            role=role,
            object_type=permissions.object_type,
            read=permissions.read,
            update=permissions.update,
            delete=permissions.delete,
            mandatory=permissions.mandatory,
            my_work=permissions.my_work,
            default_to_current_user=permissions.default_to_current_user,
            non_editable="1",
            internal="1" if role in MAPPED_ROLES else "0",
        )


def _migrate_auditors(connection):
    """Migrate Auditors from user roles to access_control_list"""
    # 1. Migrate user_roles to Auditors acr
    connection.execute(
        text("""
  INSERT INTO access_control_list(
      person_id, ac_role_id, object_id, object_type,
      created_at, updated_at, context_id)
  SELECT ur.person_id, acr.id, c.related_object_id, c.related_object_type,
         ur.created_at, ur.updated_at, ur.context_id
  FROM user_roles AS ur
  JOIN roles AS r ON ur.role_id = r.id
  JOIN contexts as c on ur.context_id = c.id
  JOIN access_control_roles as acr on acr.name = 'Auditors'
  WHERE r.name = 'Auditor' AND c.related_object_id is not NULL;
  """))
    # 2. Migrate Audit context objects using context_id
    # snapshots, assessments, documents, issues, assessment templates, snapshots
    _insert_acl_from_mapped([
        AC_TABLE("Snapshot", "snapshots", "Auditors Snapshot Mapped",
                 "Auditors"),
        AC_TABLE("Assessment", "assessments", "Auditors Assessment Mapped",
                 "Auditors"),
        AC_TABLE("Issue", "issues", "Auditors Issue Mapped", "Auditors"),
        AC_TABLE("AssessmentTemplate", "assessment_templates",
                 "Auditors Mapped", "Auditors"),
    ], connection)

    # 3. Migrate Second level objects:
    _insert_acl_from_second_level([
        AC_TABLE("Document", "Assessment", "Auditors Document Mapped",
                 "Auditors Assessment Mapped"),
        AC_TABLE("Comment", "Assessment", "Auditors Mapped",
                 "Auditors Assessment Mapped"),
        AC_TABLE("Document", "Issue", "Auditors Document Mapped",
                 "Auditors Issue Mapped"),
        AC_TABLE("Comment", "Issue", "Auditors Mapped",
                 "Auditors Issue Mapped")
    ], connection)


def _migrate_captains(connection):
    """Migrate Audit Captain from audit field to access_control_list"""
    # 1. Migrate audit captains to access_control_list
    connection.execute(
        text("""
  INSERT INTO access_control_list(
      person_id, ac_role_id, object_id, object_type,
      created_at, updated_at, context_id)
  SELECT a.contact_id, acr.id, a.id, 'Audit',
         a.created_at, a.updated_at, a.context_id
  FROM audits AS a
  JOIN access_control_roles AS acr ON acr.name = 'Audit Captains'
  JOIN people AS p ON a.contact_id = p.id;
  """))
    # 2. Migrate Audit context objects using context_id
    # snapshots, assessments, documents, issues, assessment templates, snapshots
    _insert_acl_from_mapped([
        AC_TABLE("Snapshot", "snapshots", "Audit Captains Mapped",
                 "Audit Captains"),
        AC_TABLE("Assessment", "assessments", "Audit Captains Mapped",
                 "Audit Captains"),
        AC_TABLE("Issue", "issues", "Audit Captains Mapped", "Audit Captains"),
        AC_TABLE("AssessmentTemplate", "assessment_templates",
                 "Audit Captains Mapped", "Audit Captains"),
    ], connection)

    # 3. Migrate Second level objects:
    _insert_acl_from_second_level([
        AC_TABLE("Document", "Assessment", "Audit Captains Mapped",
                 "Audit Captains Mapped"),
        AC_TABLE("Comment", "Assessment", "Audit Captains Mapped",
                 "Audit Captains Mapped"),
        AC_TABLE("Document", "Issue", "Audit Captains Mapped",
                 "Audit Captains Mapped"),
        AC_TABLE("Comment", "Issue", "Audit Captains Mapped",
                 "Audit Captains Mapped")
    ], connection)


def _insert_acl_from_mapped(tables, connection):
    """Insert access_control_list rows from multiple tables"""
    for table in tables:
        connection.execute(
            text("""
    INSERT INTO access_control_list(
        person_id, ac_role_id, object_id, object_type,
        created_at, updated_at, context_id, parent_id)
    SELECT acl.person_id, nacr.id, s.id, '{type}',
           acl.created_at, acl.updated_at, acl.context_id, acl.id
    FROM {table} AS s
    JOIN access_control_list AS acl ON acl.context_id = s.context_id
    JOIN access_control_roles AS acr ON acl.ac_role_id = acr.id
    JOIN access_control_roles AS nacr ON nacr.name = '{role}'
    WHERE acr.name = '{parent_role}';
    """.format(**table._asdict())))


def _insert_acl_from_second_level(tables, connection):
    """Add acls for second level objects (Documents & Comments)"""
    for table in tables:

        # Mapped through source:
        connection.execute(
            text("""
    INSERT INTO access_control_list(
        person_id, ac_role_id, object_id, object_type,
        created_at, updated_at, context_id, parent_id)
    SELECT acl.person_id, acrn.id, r.destination_id, r.destination_type,
           acl.created_at, acl.updated_at, acl.context_id, acl.id
    FROM access_control_list AS acl
    JOIN access_control_roles AS acr ON acr.id = acl.ac_role_id
    JOIN access_control_roles AS acrn ON acrn.name = '{role}'
    JOIN relationships AS r on r.source_id = acl.object_id
     AND r.source_type = acl.object_type
    WHERE acl.object_type = '{table}'
      AND acr.name = '{parent_role}'
      AND (r.destination_type = '{type}');
    """.format(**table._asdict())))

        # Mapped through destination:
        connection.execute(
            text("""
    INSERT INTO access_control_list(
        person_id, ac_role_id, object_id, object_type,
        created_at, updated_at, context_id, parent_id)
    SELECT acl.person_id, acrn.id, r.source_id, r.source_type,
           acl.created_at, acl.updated_at, acl.context_id, acl.id
    FROM access_control_list AS acl
    JOIN access_control_roles AS acr ON acr.id = acl.ac_role_id
    JOIN access_control_roles AS acrn ON acrn.name = '{role}'
    JOIN relationships AS r on r.destination_id = acl.object_id
     AND r.destination_type = acl.object_type
    WHERE acl.object_type = '{table}'
      AND acr.name = '{parent_role}'
      AND (r.source_type = '{type}');
    """.format(**table._asdict())))


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    connection = op.get_bind()
    _check_new_role_names(connection)
    _create_new_roles(connection)
    _migrate_auditors(connection)
    _migrate_captains(connection)


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    connection = op.get_bind()
    connection.execute(
        text("""
          DELETE acl
          FROM access_control_list acl
          JOIN access_control_roles acr ON acr.id = acl.ac_role_id
          WHERE acr.name IN :assignee_types
      """),
        assignee_types=ALL_ROLES.keys())
    connection.execute(
        text("""
          DELETE FROM access_control_roles
          WHERE name IN :assignee_types
      """),
        assignee_types=ALL_ROLES.keys())
