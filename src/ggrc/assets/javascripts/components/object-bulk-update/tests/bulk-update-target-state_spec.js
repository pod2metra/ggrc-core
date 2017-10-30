/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import Component from '../bulk-update-target-state.js';

var objectStateToWarningMap = {
  CycleTaskGroupObjectTask: {
    InProgress: 'Please be aware that Finished, Declined and Verified ' +
      'tasks cannot be moved to In Progress state.',
    Finished: 'Please be aware that Assigned and Verified ' +
      'tasks cannot be moved to Finished state.',
    Declined: 'Please be aware that Assigned, In Progress and Verified ' +
      'tasks cannot be moved to Declined state.',
    Verified: 'Please be aware that Assigned, In Progress and Declined ' +
      'tasks cannot be moved to Verified state.',
  },
};
var viewModel;

define('GGRC.Components.bulkUpdateTargetState', function () {
  beforeAll(function () {
    viewModel = new (can.Map.extend(Component.prototype.viewModel));
  });
  define('warningMessage property', function () {
    it('should return appropriate warnings for objects', function () {
      var objectStatesMap = {
        CycleTaskGroupObjectTask: ['Assigned', 'InProgress', 'Finished',
          'Declined', 'Deprecated', 'Verified'],
      };

      _.forEach(objectStatesMap, function (states, obj) {
        viewModel.attr('modelName', obj);

        _.forEach(states, function (state) {
          var warning;
          var expected = objectStateToWarningMap[obj][state] || '';
          viewModel.attr('targetState', state);

          warning = viewModel.attr('warningMessage');

          expect(warning).toEqual(expected);
        });
      });
    });
  });
});
