# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""Package contains Person related setup helper.

It helps to setup Person related data for tests.
"""

import string
from ggrc.models import all_models
from integration.ggrc.models import factories
from integration.ggrc_basic_permissions.models import factories as bp_factories
from integration.ggrc_workflows.helpers import rbac_helper


class PersonSetup(object):
    """Setup helper for Person related objects setup.

  Attributes:
      email_template: String template to generate user with predictable email.
          {g_rname}: Global role name.
          {m_rname}: Model related role name. Or any string for no role.
          {random_ascii}: Random ASCII string.
  """

    def __init__(self, model_name):
        self.email_template = "{}_{}_{}_{}@google.com".format(
            model_name,
            "{g_rname}",
            "{m_rname}",
            "{random_ascii}",
        )

    def setup_person(self, g_rname, m_rname):
        """Generate Person with Global Role using Factories.

    Args:
        g_rname: Global Role name for user.
        m_rname: Model related ACR name. If user should not have role in
            scope of Model, it can be any other string.

    Returns:
        Generated person.
    """
        email = self._gen_email(g_rname, m_rname)
        person = factories.PersonFactory(email=email)
        bp_factories.UserRoleFactory(
            person=person, role=rbac_helper.G_ROLES[g_rname])
        return person

    def _gen_email(self, g_rname, m_rname):
        """Generate Person's email.

    Args:
        g_rname: Global Role name.
        m_rname: Model related ACR name.

    Returns:
        String with generated predictable email.
        It has next structure:
            prefix: '{model name}_{global role name}_{model role name}_'
            body: '{6 random ascii letters}'
            suffix: '@google.com'
        Generated email to return:
            prefix + body + suffix
    """
        m_rname = m_rname.replace(" ", "_")
        random_ascii = factories.random_str(
            length=6, chars=string.ascii_letters)
        return self.email_template.format(
            g_rname=g_rname, m_rname=m_rname, random_ascii=random_ascii)

    def get_people(self, g_rname, m_rname):
        """Query all people who match email template.

    Args:
        g_rname: Global Role name.
        m_rname: Model related Access Control Role name.
    Returns:
        List of people with predictable email template.
    """
        m_rname = m_rname.replace(" ", "_")
        query_email_templ = self.email_template.format(
            g_rname=g_rname, m_rname=m_rname, random_ascii="%")
        return all_models.Person.query.filter(
            all_models.Person.email.like(query_email_templ)).all()

    def get_person(self, g_rname, m_rname):
        """Query person who match email template.

    Args:
        g_rname: Global Role name.
        m_rname: Model related Access Control Role name.
    Returns:
        Person instance, if only one Person in DB with predictable email.
        None, if list of people match template or nobody.
    """
        people = self.get_people(g_rname, m_rname)
        if len(people) == 1:
            return people[0]
        return None
