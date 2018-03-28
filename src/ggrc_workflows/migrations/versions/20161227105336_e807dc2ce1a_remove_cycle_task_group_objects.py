# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Remove cycle_task_group_objects

Create Date: 2016-12-27 10:53:36.110159
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'e807dc2ce1a'
down_revision = '4cb78ab9a321'


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    op.drop_constraint(
        "cycle_task_group_object_tasks_ibfk_3",
        "cycle_task_group_object_tasks",
        type_="foreignkey")
    op.drop_column("cycle_task_group_object_tasks",
                   "cycle_task_group_object_id")
    op.drop_table("cycle_task_group_objects")


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    op.execute("""
      CREATE TABLE `cycle_task_group_objects` (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `cycle_task_group_id` int(11) NOT NULL,
        `task_group_object_id` int(11) NOT NULL,
        `contact_id` int(11) DEFAULT NULL,
        `status` varchar(250) DEFAULT NULL,
        `end_date` date DEFAULT NULL,
        `start_date` date DEFAULT NULL,
        `description` text,
        `title` varchar(250) NOT NULL,
        `created_at` datetime NOT NULL,
        `modified_by_id` int(11) DEFAULT NULL,
        `updated_at` datetime NOT NULL,
        `context_id` int(11) DEFAULT NULL,
        `cycle_id` int(11) NOT NULL,
        `object_id` int(11) NOT NULL,
        `object_type` varchar(250) NOT NULL,
        `next_due_date` date DEFAULT NULL,
        `secondary_contact_id` int(11) DEFAULT NULL,
        PRIMARY KEY (`id`),
        KEY `task_group_object_id` (`task_group_object_id`),
        KEY `fk_cycle_task_group_objects_contact` (`contact_id`),
        KEY `fk_cycle_task_group_objects_contexts` (`context_id`),
        KEY `ix_cycle_task_group_objects_updated_at` (`updated_at`),
        KEY `fk_cycle_task_group_objects_secondary_contact`
            (`secondary_contact_id`),
        KEY `cycle_task_group_objects_cycle` (`cycle_id`),
        KEY `cycle_task_group_objects_ibfk_3` (`cycle_task_group_id`),
        CONSTRAINT `cycle_task_group_objects_cycle` FOREIGN KEY (`cycle_id`)
            REFERENCES `cycles` (`id`) ON DELETE CASCADE,
        CONSTRAINT `cycle_task_group_objects_ibfk_1` FOREIGN KEY (`contact_id`)
            REFERENCES `people` (`id`),
        CONSTRAINT `cycle_task_group_objects_ibfk_2` FOREIGN KEY (`context_id`)
            REFERENCES `contexts` (`id`),
        CONSTRAINT `cycle_task_group_objects_ibfk_3` FOREIGN KEY
            (`cycle_task_group_id`) REFERENCES `cycle_task_groups` (`id`)
                ON DELETE CASCADE
      )
  """)
    op.add_column(
        "cycle_task_group_object_tasks",
        sa.Column("cycle_task_group_object_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key("cycle_task_group_object_tasks_ibfk_3",
                          "cycle_task_group_object_tasks",
                          "cycle_task_group_objects",
                          ["cycle_task_group_object_id"], ["id"])
