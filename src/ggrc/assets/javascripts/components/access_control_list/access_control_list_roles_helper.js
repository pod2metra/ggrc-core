/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

(function (GGRC) {
  'use strict';

  GGRC.Components('accessControlListRolesHelper', {
    tag: 'access-control-list-roles-helper',

    viewModel: {
      instance: {},
      isNewInstance: false,
      setAutoPopulatedRoles: function () {
        var instance = this.attr('instance');
        var autoPopulatedRoles = _.filter(GGRC.access_control_roles, {
          object_type: instance.class.model_singular,
          default_to_current_user: true
        });

        if (!autoPopulatedRoles.length) {
          return;
        }

        if (!instance.attr('access_control_list')) {
          instance.attr('access_control_list', []);
        }

        autoPopulatedRoles.forEach(function (role) {
          instance.attr('access_control_list').push({
            ac_role_id: role.id,
            person: {type: 'Person', id: GGRC.current_user.id}
          });
        });
      }
    },
    events: {
      inserted: function () {
        if (this.viewModel.attr('isNewInstance')) {
          this.viewModel.setAutoPopulatedRoles();
        }
      }
    }
  });
})(window.GGRC);
