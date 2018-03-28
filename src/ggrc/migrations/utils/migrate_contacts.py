# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
""""Migrate contacts

Migration helper that migrates contact fields to the access control list"""

from alembic import op


def migrate_contacts(type_, table_type, mappings=None):
    """Creates new access control roles and migrates existing contacts"""

    connection = op.get_bind()
    if mappings is None:
        mappings = ({
            'name': 'Primary Contacts',
            'column': 'contact_id',
        }, {
            'name': 'Secondary Contacts',
            'column': 'secondary_contact_id',
        })
    # 1. Create new custom roles:
    sql = """
      INSERT INTO access_control_roles
                  (name, object_type, created_at, updated_at)
           VALUES ('{first_role}', '{type}', NOW(), NOW()),
                  ('{second_role}', '{type}', NOW(), NOW())
  """.format(
        type=type_,
        first_role=mappings[0]['name'],
        second_role=mappings[1]['name'])
    op.execute(sql)

    # 2. Fetch ids for newly created roles
    results = connection.execute("""
      SELECT id, name
        FROM access_control_roles
       WHERE (name = '{first_role}' OR name = '{second_role}')
         AND object_type = '{object_type}'
    ORDER BY id
  """.format(
        object_type=type_,
        first_role=mappings[0]['name'],
        second_role=mappings[1]['name'])).fetchall()

    # 3. Migrate each contact field to access_control_list
    for contact_name, role_id in ((mappings[0]['column'], results[0][0]),
                                  (mappings[1]['column'], results[1][0])):
        extra = ''  # Used for extra conditions needed by polymorphic tables
        if table_type == 'directives':
            extra = "AND meta_kind = '{}'".format(type_)
        elif type_ == 'Process':
            extra = "AND is_biz_process = 1"
        elif type_ == 'System':
            extra = "AND is_biz_process = 0"
        sql = """
      INSERT INTO access_control_list
                  (person_id, ac_role_id, object_id, object_type,
                   created_at, updated_at)
           SELECT {contact_name}, {role_id}, id, '{object_type}', NOW(), NOW()
             FROM {table_type}
            WHERE {contact_name} IS NOT null {extra}""".format(
            role_id=role_id,
            contact_name=contact_name,
            object_type=type_,
            table_type=table_type,
            extra=extra)
        op.execute(sql)
