# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Set ACL roles for Regulation and Objectives snapshots

Create Date: 2017-11-01 08:19:55.468754
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = '413d6c32ccf5'
down_revision = '33d043d8ba29'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    # Enable creation of temp tables
    op.execute("SET AUTOCOMMIT = 1;")
    op.execute("""
      CREATE TEMPORARY TABLE temp_control_snapshots (
        snapshot_id int(11)
      );
  """)
    op.execute("""
      INSERT INTO temp_control_snapshots(snapshot_id)
      SELECT snap_id
      FROM (
        SELECT r.destination_id AS snap_id
        FROM relationships r
        JOIN assessments a ON a.id = r.source_id
        JOIN snapshots s ON s.id = r.destination_id
        WHERE r.source_type = 'Assessment' AND
              r.destination_type = 'Snapshot' AND
              s.child_type = 'Control'
        UNION ALL
        SELECT r.source_id
        FROM relationships r
        JOIN assessments a ON a.id = r.destination_id
        JOIN snapshots s ON s.id = r.source_id
        WHERE r.destination_type = 'Assessment' AND
              r.source_type = 'Snapshot' AND
              s.child_type = 'Control'
      ) tmp
      GROUP BY snap_id;
  """)

    # Regulation and Objective snapshots should receive same assignee roles as
    # Control snapshot to which they mapped
    op.execute("""
      INSERT INTO access_control_list(
        person_id, ac_role_id, object_id, object_type,
        created_at, updated_at, context_id, parent_id
      )
      SELECT control_acl.person_id, control_acl.ac_role_id,
        tmp.mapped_id, 'Snapshot', now(), now(),
        NULL, control_acl.parent_id
      FROM
      (
        SELECT r.source_id AS control_snap_id,
               r.destination_id AS mapped_id
        FROM relationships r
        JOIN snapshots s ON s.id = r.destination_id
        WHERE r.source_type = 'Snapshot' AND
            r.destination_type = 'Snapshot' AND
            s.child_type IN ('Regulation', 'Objective')
        UNION ALL
        SELECT r.destination_id, r.source_id
        FROM relationships r
        JOIN snapshots s ON s.id = r.source_id
        WHERE r.source_type = 'Snapshot' AND
            r.destination_type = 'Snapshot' AND
            s.child_type IN ('Regulation', 'Objective')
      ) tmp
      JOIN temp_control_snapshots tcs
        ON tcs.snapshot_id = tmp.control_snap_id
      JOIN access_control_list control_acl
        ON control_acl.object_type = 'Snapshot' AND
           control_acl.object_id = tmp.control_snap_id
      JOIN access_control_roles acr ON acr.id = control_acl.ac_role_id
      LEFT JOIN access_control_list self_acl ON
        self_acl.person_id = control_acl.person_id AND
        self_acl.ac_role_id = control_acl.ac_role_id AND
        self_acl.object_id = tmp.mapped_id AND
        self_acl.object_type = 'Snapshot'
      WHERE acr.name IN (
        'Creators Mapped', 'Assignees Mapped', 'Verifier Mapped'
      ) AND self_acl.id IS NULL
      GROUP BY control_acl.person_id, control_acl.ac_role_id, tmp.mapped_id,
        control_acl.parent_id;
  """)

    op.execute("DROP TABLE IF EXISTS temp_control_snapshots;")
    op.execute("SET AUTOCOMMIT = 0;")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute("SET SESSION SQL_SAFE_UPDATES = 0;")
    op.execute("""
      DELETE acl
      FROM access_control_list acl
      JOIN access_control_roles acr ON acr.id = acl.ac_role_id
      JOIN snapshots s ON s.id = acl.object_id AND acl.object_type = 'Snapshot'
      LEFT JOIN relationships r1 ON
        r1.source_type = 'Snapshot' AND
        r1.source_id = s.id AND
        r1.destination_type = 'Assessment'
      LEFT JOIN relationships r2 ON
        r2.destination_type = 'Snapshot' AND
        r2.destination_id = s.id AND
        r2.source_type = 'Assessment'
      WHERE r1.id IS NULL AND
        r2.id IS NULL AND
        s.child_type IN ('Regulation', 'Objective') AND
        acr.name IN (
          'Creators Mapped', 'Assignees Mapped', 'Verifier Mapped'
        );
  """)
