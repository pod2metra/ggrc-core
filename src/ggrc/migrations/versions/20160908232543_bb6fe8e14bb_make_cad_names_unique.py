# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""
Make cad names unique

Create Date: 2016-09-08 23:25:43.508159
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

from alembic import op

# revision identifiers, used by Alembic.
revision = "bb6fe8e14bb"
down_revision = "4450e7d1e441"

# current reserved words were generated with:
# set((alias["display_name"] if isinstance(alias, dict) else alias).lower()
#     for model in all_models
#     for alias in AttributeInfo.gather_aliases(model).values() if alias)

_reserved_words = {
    "access group url", "actual finish date", "actual verified date",
    "assertions", "assessment url", "assessor", "assignee", "audit",
    "auditors", "categories", "clause url", "code", "company",
    "conclusion: design", "conclusion: operation", "contact", "contract url",
    "control url", "creator", "custom attributes", "custom email message",
    "cycle", "data asset url", "default assessors", "default test plan",
    "default verifier", "description", "details", "due on", "editor",
    "effective date", "email", "end", "end date", "evidence", "facility url",
    "finished date", "force real-time email updates", "fraud related",
    "frequency", "internal audit lead", "issue url", "kind/nature",
    "kind/type", "link", "manager", "market url", "member", "name",
    "network zone", "no access", "notes", "object", "object under assessment",
    "objective url", "objects", "org group url", "owner", "planned end date",
    "planned report period from", "planned report period to",
    "planned start date", "policy / regulation / standard / contract",
    "policy url", "primary contact", "principal assessor", "process url",
    "product url", "program", "program url", "project url", "reader",
    "recipients", "reference url", "regulation url", "request type",
    "requester", "risk counsel", "risk manager", "role", "secondary assessor",
    "secondary contact", "section url", "send by default", "significance",
    "standard url", "start", "start date", "starts on", "state", "status",
    "stop date", "summary", "system url", "task description", "task details",
    "task group", "task type", "template", "test", "test plan",
    "text of clause", "text of section", "threat url", "title", "type/means",
    "url", "use control test plan", "vendor url", "verified date", "verifier",
    "workflow"
}

_duplicates_sql = """
    SELECT title, COUNT(id) AS id_count
    FROM custom_attribute_definitions
    GROUP BY title, definition_id
    HAVING id_count > 1
"""


def _get_bad_names(conn):
    """Get a list of bad names in single quotes."""
    res = conn.execute(_duplicates_sql)
    results = res.fetchall()
    bad_names = _reserved_words.union({item[0] for item in results})
    return ["'{}'".format(name) for name in bad_names]


def _remove_duplicates_step(conn):
    """rename duplicate entries in the database.

  This function changes the names of all badly named custom attributes. Because
  the new name can still clash with an existing attribute name, this function
  must be called until there are no changes made anymore.
  """
    bad_names = _get_bad_names(conn)
    query = """
    UPDATE custom_attribute_definitions
    SET title=CONCAT(title, " - ", id) WHERE title IN ({});
  """.format(",".join(bad_names))

    return conn.execute(query)


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""

    conn = op.get_bind()

    res = _remove_duplicates_step(conn)
    while res.rowcount > 0:
        res = _remove_duplicates_step(conn)


def downgrade():
    """Ne need to add duplicate names here."""
