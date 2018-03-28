# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Migrate Requests to Assessments

Create Date: 2016-12-21 08:48:29.292341
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import re

from alembic import op
import sqlalchemy
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '1aa39778da75'
down_revision = '42b22b9ca859'


def ensure_assessment_slug_uniqueness(connection):
    """Append a unique suffix to every Request.slug == Assessment.slug."""

    slugs_conflict = connection.execute("""
      select exists (
          select requests.slug
          from requests join assessments on requests.slug = assessments.slug
      )
  """).fetchone()[0]

    if not slugs_conflict:
        return

    # Change every Request slug present in Assessment slug into a new unique slug
    # formatting it like "{old_slug}-request-{unique_numeric_suffix}", i.e.
    # SLUG-request-1, where 1 is the number of attempted renames for SLUG

    # Table to map old Request slugs to new Request slugs:
    # - if old_slug is NULL, new_slug contains an already present Assessment slug
    # - if blocked_slug is not NULL, there was an unsuccessful INSERT of
    #   a mapping from $blocked_slug to $new_slug
    connection.execute("""
      create temporary table old_new_slugs_map (
          old_slug varchar(250) null,
          new_slug varchar(250) not null unique,
          blocked_slug varchar(250) null
      )
  """)
    # Table to hold the slugs that were not inserted successfully into the
    # previous table (a copy of unique values from blocked_slug column)
    connection.execute("""
      create temporary table blocked_req_slugs (
          slug varchar(250) not null unique
      )
  """)

    # Fill in Assessment slugs into the mapping table to detect conflicts
    connection.execute("""
      insert into old_new_slugs_map (new_slug) select slug from assessments
  """)

    insert_mapping_row_query = """
      insert into old_new_slugs_map (old_slug, new_slug)
      select slug, {new_slug_expr} from {table}
      on duplicate key update blocked_slug = slug
  """

    # Try to fill in the initial Request slugs without renaming
    connection.execute(
        insert_mapping_row_query.format(
            table="requests", new_slug_expr="slug"))

    attempt_number = 0
    while True:
        # Store the blocked slugs in a special table
        store_blocked_slugs = connection.execute("""
        insert ignore into blocked_req_slugs (slug)
        select blocked_slug from old_new_slugs_map
        where blocked_slug is not NULL
    """)

        if store_blocked_slugs.rowcount == 0:
            # all conflicting slugs were renamed
            break

        # Clean the blocked slugs in the mapping table
        connection.execute("""
        update old_new_slugs_map set blocked_slug = NULL
    """)

        attempt_number += 1

        # Try to fill in the blocked Request slugs with a numeric suffix
        connection.execute(
            text(
                insert_mapping_row_query.format(
                    table="blocked_req_slugs",
                    new_slug_expr="concat(slug, '-', :suffix)",
                )),
            suffix=str(attempt_number),
        )

        # Clean the blocked slugs from the previous iteration
        connection.execute("""
        truncate blocked_req_slugs
    """)

    # Change the slugs of requests from $old_slug to $new_slug
    connection.execute("""
      update requests
             join old_new_slugs_map
                 on requests.slug = old_new_slugs_map.old_slug
      set requests.slug = old_new_slugs_map.new_slug
  """)

    connection.execute("drop temporary table old_new_slugs_map")
    connection.execute("drop temporary table blocked_req_slugs")


def find_request_type_cad_id(connection):
    """Find (create if not exists) the id of the CAD for request_type values."""

    query_for_request_type_cad = text("""
      select id from custom_attribute_definitions
      where title like :title and
            (multi_choice_options like 'documentation,interview' or
             multi_choice_options like 'interview,documentation') and
            definition_type = 'assessment' and
            definition_id is NULL
  """)
    request_type_cad_id = connection.execute(
        query_for_request_type_cad, title="Type").first()
    if not request_type_cad_id:
        cad_title = base_cad_title = "Type"
        attempt = 0

        found_unused_title = False
        while not found_unused_title:
            if connection.execute(
                    text("""
          select id from custom_attribute_definitions
          where title like :title and
                definition_type = 'assessment'
      """),
                    title=cad_title).first() is None:
                # No CAD with title=cad_title, we can use this title
                found_unused_title = True
            else:
                # cad_title is used, generate a new title with a numeric suffix
                attempt += 1
                cad_title = base_cad_title + " ({})".format(attempt)

        connection.execute(
            text("""
        insert into custom_attribute_definitions (
            created_at, updated_at, title, helptext, attribute_type,
            definition_type, definition_id, multi_choice_options, mandatory
        )
        values (
            NOW(), NOW(), :title, 'Assessment type', 'Dropdown',
            'assessment', NULL, 'Documentation,Interview', 0
        )
    """),
            title=cad_title)
        request_type_cad_id = connection.execute(
            query_for_request_type_cad, title=cad_title).fetchone()

    # (cad_id,) -> cad_id
    request_type_cad_id = request_type_cad_id[0]

    return request_type_cad_id


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""

    connection = op.get_bind()

    ensure_assessment_slug_uniqueness(connection)

    request_type_cad_id = find_request_type_cad_id(connection)

    # create new Assessments from Requests
    op.execute("""
      insert into assessments (os_state,
                               test_plan,
                               end_date,
                               start_date,
                               status,
                               notes,
                               description,
                               title,
                               slug,
                               created_at,
                               modified_by_id,
                               updated_at,
                               context_id,
                               finished_date,
                               verified_date,
                               recipients,
                               send_by_default)
      select 'Draft',
             test,
             end_date,
             start_date,
             status,
             notes,
             description,
             title,
             slug,
             NOW(),
             modified_by_id,
             NOW(),
             context_id,
             finished_date,
             verified_date,
             recipients,
             send_by_default
      from requests
  """)

    # migrate Request.request_type into a special global CA
    connection.execute(
        text("""
      insert into custom_attribute_values (context_id,
                                           created_at,
                                           updated_at,
                                           custom_attribute_id,
                                           attributable_id,
                                           attributable_type,
                                           attribute_value)
      select requests.context_id,
             NOW(),
             NOW(),
             :cad_id,
             assessments.id,
             'Assessment',
             case requests.request_type
                  when 'documentation' then 'Documentation'
                  when 'interview' then 'Interview'
                  else NULL
             end
      from requests join assessments on requests.slug = assessments.slug
  """),
        cad_id=request_type_cad_id)

    # migrate global custom attributes definitions
    op.execute("""
      update custom_attribute_definitions
      set definition_type = 'assessment',
          title = CONCAT(title, ' (migrated from Requests on ',
                         CURRENT_DATE(), ')')
      where definition_type = 'request';
  """)

    # update all m2m references to Requests
    m2m_update_query_skeleton = ("""
      update {table}
             join requests on {table}.{relationship}_type = 'Request' and
                              {table}.{relationship}_id = requests.id
             join assessments on requests.slug = assessments.slug
      set {relationship}_type = 'Assessment',
          {relationship}_id = assessments.id
  """)

    updates_required = (
        ("custom_attribute_values", "attributable"),
        ("object_documents", "documentable"),
        ("object_people", "personable"),
        ("relationships", "source"),
        ("relationships", "destination"),
    )

    for table, relationship in updates_required:
        op.execute(
            m2m_update_query_skeleton.format(
                table=table, relationship=relationship))

    # create Assessment->Audit Relationships from requests.audit_id FK
    # IGNORE for the case with Relationship(Audit(id=1), Request(audit_id=1))
    op.execute("""
      insert ignore into relationships (source_id,
                                 source_type,
                                 destination_id,
                                 destination_type,
                                 created_at,
                                 updated_at)
      select assessments.id,
             'Assessment',
             requests.audit_id,
             'Audit',
             NOW(),
             NOW()
      from assessments join requests on assessments.slug = requests.slug
  """)

    # update Request-related Assignees
    assignee_translation = {
        "Requester": "Creator",
        "Assignee": "Assessor",
    }

    assignee_type_query = connection.execute("""
      SELECT id, relationship_id, attr_name, attr_value
      FROM relationship_attrs
      WHERE attr_name = 'AssigneeType'
  """)

    attr_delete_ids = []
    attr_update_str = []
    attr_update_val = {}

    for i, attr in enumerate(assignee_type_query):
        # Split the assignees csv; replace every Request-specific assignee with its
        # Assessment variant; discard empty assignees
        new_assignees = ",".join(
            sorted({
                assignee_translation.get(assignee, assignee)
                for assignee in (attr.attr_value or "").split(",") if assignee
            }))
        if not new_assignees:
            attr_delete_ids.append(attr.id)
        elif new_assignees != attr.attr_value:
            attr_update_str.append(
                "(:id{i}, :relationship_id{i}, :attr_name{i}, "
                ":attr_value{i})".format(i=i))
            attr_update_val["id{}".format(i)] = attr.id
            attr_update_val["relationship_id{}".format(
                i)] = attr.relationship_id
            attr_update_val["attr_name{}".format(i)] = attr.attr_name
            attr_update_val["attr_value{}".format(i)] = new_assignees
        else:
            # same set of assignees, no action required
            pass

    if attr_delete_ids:
        connection.execute(
            "delete from relationship_attrs where id in ({})".format(
                ",".join(str(id_) for id_ in attr_delete_ids)))
    if attr_update_val:
        connection.execute(
            text("""
        REPLACE INTO relationship_attrs (
            id,
            relationship_id,
            attr_name,
            attr_value
        )
        VALUES
        {}
        """.format(", ".join(attr_update_str))), **attr_update_val)

    # The following block logically belongs to ggrc_workflows but is included
    # here to ensure that it is executed before dropping the Requests table.
    try:
        op.execute("select 1 from task_group_objects limit 1")
    except sqlalchemy.exc.ProgrammingError as e:
        if re.search(r"""\(1146, "Table '.+' doesn't exist"\)$""", e.message):
            # task_group_objects does not exist, most probably the installation
            # doesn't have workflows installed
            pass
        else:
            raise
    else:
        op.execute(
            m2m_update_query_skeleton.format(
                table="task_group_objects", relationship="object"))


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    # skipping since Requests are currently deprecated in favor of Assessments
    pass
