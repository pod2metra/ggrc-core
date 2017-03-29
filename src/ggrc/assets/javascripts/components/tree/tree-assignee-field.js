/*!
  Copyright (C) 2017 Google Inc., authors, and contributors <see AUTHORS file>
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

(function (can) {
  'use strict';

  GGRC.Components('treeAssigneeField', {
    tag: 'tree-assignee-field',
    template: '<content/>',
    viewModel: can.Map.extend({
      type: '@',
      instance: '@',
      assigneeStr: '',
      init: function () {
        this.attr('assigneeStr', this.sliceAssignees());
        this.attr('instance').bind('change', function () {
          this.attr('assigneeStr', this.sliceAssignees());
        }.bind(this));
      },
      sliceAssignees: function () {
        var result = '';
        var assignees;
        var instance = this.attr('instance');
        if (!instance || !instance.assignees) {
          return result;
        }
        assignees = instance.assignees[this.attr('type')];
        if (assignees) {
          result = assignees.map(function (e) {
            return e.email.replace(/@.*$/, '');
          }).join(' ');
        }
        return result;
      }
    })
  });
})(window.can);
