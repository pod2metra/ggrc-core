/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

describe('GGRC.Components.accessControlListRolesHelper', function () {
  'use strict';

  var viewModel;

  beforeAll(function () {
    GGRC.access_control_roles = [
      {
        object_type: 'Assessment',
        id: 5,
        name: 'Admin',
        default_to_current_user: true
      },
      {
        object_type: 'Control',
        id: 6,
        name: 'Primary Contact',
        default_to_current_user: true
      },
      {
        object_type: 'Assessment',
        id: 7,
        name: 'SuperAdmin',
        default_to_current_user: true
      },
      {
        object_type: 'Assessment',
        id: 8,
        name: 'Primary contacts',
        default_to_current_user: false
      }
    ];
  });

  afterAll(function () {
    delete GGRC.access_control_roles;
  });

  beforeEach(function () {
    viewModel = GGRC.Components
      .getViewModel('accessControlListRolesHelper');
  });

  describe('"setAutoPopulatedRoles" method', function () {
    var instance;

    it('should set current user for 2 roles', function () {
      instance = new CMS.Models.Assessment({id: 25});
      viewModel.attr('instance', instance);
      expect(instance.access_control_list.length).toEqual(0);
      viewModel.setAutoPopulatedRoles();
      expect(instance.access_control_list.length).toEqual(2);
      expect(instance.access_control_list[0].ac_role_id)
        .toEqual(5);
      expect(instance.access_control_list[1].ac_role_id)
        .toEqual(7);
      expect(instance.access_control_list[0].person.id)
        .toEqual(1);
    });

    it('should set current user for 1 role', function () {
      instance = new CMS.Models.Control({id: 25});
      viewModel.attr('instance', instance);
      expect(instance.access_control_list).toBe(undefined);
      viewModel.setAutoPopulatedRoles();
      expect(instance.access_control_list.length).toEqual(1);
      expect(instance.access_control_list[0].ac_role_id)
        .toEqual(6);
      expect(instance.access_control_list[0].person.id)
        .toEqual(1);
    });
  });
});
