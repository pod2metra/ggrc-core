# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
"""This module contains TestSetup class definition with functionality for
test data installation."""
# pylint: disable=too-many-arguments
from ggrc import db, app
from ggrc.models import inflector
from ggrc.snapshotter.rules import Types

from integration.ggrc.models import factories

from api_search.base import SetupData, OPERATIONS, TEST_REPEAT_COUNT, \
    MULTIPLE_ITEMS_COUNT
from api_search.helpers import field_exists, create_reindexed_snapshots, \
    create_rand_person
from api_search.setters import init_globals, FIELD_SETTERS


class SetupEnvironment(object):
    """Single setup class (data will be installed only in first call)"""

    def __init__(self):
        """Set up basic test fixture with the following data:
    - Persons and Roles
    - Searchable model instance
    - basic test cases
    """
        if not db.engine.dialect.has_table(db.engine, SetupData.__tablename__):
            SetupData.__table__.create(db.engine)

        objects = []
        init_globals(Types.all)
        with factories.single_commit():
            audit_id = factories.AuditFactory().id
            for model in Types.all:
                for field in FIELD_SETTERS:
                    if field_exists(inflector.get_model(model), field):
                        for operation in OPERATIONS:
                            objects += self.base_single_setup(
                                model, field, operation)
                            objects += self.base_multiple_setup(
                                model, field, operation)

        with app.app.app_context():
            create_reindexed_snapshots(audit_id, objects)

    def base_single_setup(self, model_name, field, operation):
        """Set up basic test fixture with the following data:
    - Persons and Roles
    - Searchable model instance
    - basic test cases
    """
        setup_func = self.get_setup_func(operation, True)
        objects = []
        for _ in range(TEST_REPEAT_COUNT):
            objects.append(setup_func(model_name, field, create_rand_person()))
        return objects

    def base_multiple_setup(self, model_name, field, operation):
        """Set up basic test fixture with the following data:
    - Persons and Roles
    - Searchable model instance
    - basic test cases
    """
        persons = []
        for _ in range(MULTIPLE_ITEMS_COUNT + 1):
            persons.append(create_rand_person())
        setup_func = self.get_setup_func(operation, False)
        return setup_func(model_name, field, persons)

    def single_setup_equal(self, model_name, field, person, operator="="):
        """Setup single entry for equal operation"""
        obj_factory = self.get_factory(model_name)
        obj = obj_factory(**FIELD_SETTERS[field](model_name, person))
        db.session.add(
            SetupData(
                model=model_name,
                operator=operator,
                field=field,
                single=True,
                obj_id=obj.id,
                searchable_id=person.id,
                searchable_type=person.type))
        return obj

    def multiple_setup_equal(self, model_name, field, persons, operator="="):
        """Setup multiple entry for equal operation"""
        obj_factory = self.get_factory(model_name)
        objects = []
        for num, _ in enumerate(persons):
            # Set one person for several objects
            if num < MULTIPLE_ITEMS_COUNT:
                person = persons[0]
            else:
                person = persons[num]

            obj = obj_factory(**FIELD_SETTERS[field](model_name, person))
            db.session.add(
                SetupData(
                    model=model_name,
                    operator=operator,
                    field=field,
                    single=False,
                    obj_id=obj.id,
                    searchable_id=person.id,
                    searchable_type=person.type))
            objects.append(obj)
        return objects

    def single_setup_not_equal(self, model_name, field, person, operator="!="):
        # For now single setup is the same
        return self.single_setup_equal(model_name, field, person, operator)

    def multiple_setup_not_equal(self,
                                 model_name,
                                 field,
                                 persons,
                                 operator="!="):
        # For now multiple setup is the same
        return self.multiple_setup_equal(model_name, field, persons, operator)

    def single_setup_contains(self, model_name, field, person, operator="~"):
        # For now single setup is the same
        return self.single_setup_equal(model_name, field, person, operator)

    def multiple_setup_contains(self, model_name, field, persons,
                                operator="~"):
        # For now multiple setup is the same
        return self.multiple_setup_equal(model_name, field, persons, operator)

    def single_setup_not_contains(self,
                                  model_name,
                                  field,
                                  person,
                                  operator="!~"):
        # For now single setup is the same
        return self.single_setup_equal(model_name, field, person, operator)

    def multiple_setup_not_contains(self,
                                    model_name,
                                    field,
                                    persons,
                                    operator="!~"):
        # For now multiple setup is the same
        return self.multiple_setup_equal(model_name, field, persons, operator)

    def single_setup_is_empty(self,
                              model_name,
                              field,
                              person,
                              operator="is empty"):
        # For now single setup is the same
        return self.single_setup_equal(model_name, field, person, operator)

    def multiple_setup_is_empty(self,
                                model_name,
                                field,
                                persons,
                                operator="is empty"):
        """Setup multiple entry for is_empty operation"""
        obj_factory = self.get_factory(model_name)
        objects = []
        for num, _ in enumerate(persons):
            # Don't set searchable field for several objects, they should be empty
            if num >= MULTIPLE_ITEMS_COUNT:
                obj = obj_factory(**FIELD_SETTERS[field](model_name,
                                                         persons[num]))
            else:
                obj = factories.get_model_factory(model_name)()
            db.session.add(
                SetupData(
                    model=model_name,
                    operator=operator,
                    field=field,
                    single=False,
                    obj_id=obj.id,
                    searchable_id=persons[num].id,
                    searchable_type=persons[num].type))
            objects.append(obj)
        return objects

    def get_setup_func(self, operation, single):
        """Find setup func by test case parameters"""
        setup_name = "{}_setup_{}".format(
            "single" if single else "multiple",
            OPERATIONS[operation],
        )
        if not getattr(self, setup_name):
            raise NotImplementedError(
                "Setup {} was not implemented in BaseSetup class".format(
                    setup_name))
        return getattr(self, setup_name)

    def get_factory(self, model_name):
        """Get object factory class for model"""
        # pylint: disable=no-self-use
        base_factory = factories.get_model_factory(model_name)
        # Modify base factory to have possibility to create ACL
        # and CA in one step
        return type(base_factory.__name__ + "WithACL_CA",
                    (base_factory, factories.WithACLandCAFactory), {})
