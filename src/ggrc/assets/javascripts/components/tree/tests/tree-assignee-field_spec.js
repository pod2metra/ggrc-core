/*!
  Copyright (C) 2017 Google Inc., authors, and contributors <see AUTHORS file>
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

describe('GGRC.Components.treeAssigneeField', function () {
  'use strict';

  var viewModel;

  beforeEach(function () {
    var newViewModel;
    viewModel = GGRC.Components.get('treeAssigneeField').prototype
      .viewModel.prototype;
    //  avoiding of calling init() in creation of viewModel object
    newViewModel = Object.assign({}, viewModel);
    newViewModel.init = function () {};
    newViewModel.oldInit = viewModel.init;
    viewModel = can.Map.extend(newViewModel)();
    viewModel.init = viewModel.oldInit;
  });

  describe('init() method', function () {
    var instance;

    beforeEach(function () {
      spyOn(viewModel, 'sliceAssignees')
        .and.returnValue('mockString');
      viewModel.attr('instance', {});
      instance = viewModel.attr('instance');
      spyOn(instance, 'bind');
    });
    it('sets result of sliceAssignees to assigneeStr field', function () {
      viewModel.init();
      expect(viewModel.attr('assigneeStr')).toEqual('mockString');
      expect(viewModel.sliceAssignees).toHaveBeenCalled();
    });
    it('listens to instance changing', function () {
      viewModel.init();
      expect(instance.bind)
        .toHaveBeenCalledWith('change', jasmine.any(Function));
    });
  });

  describe('sliceAssignees() method', function () {
    var result;
    it('returns empty string if instance is falsy', function () {
      viewModel.attr('instance', false);
      result = viewModel.sliceAssignees();
      expect(result).toEqual('');
    });
    it('returns empty string if instance.assignees is falsy', function () {
      viewModel.attr('instance', {});
      result = viewModel.sliceAssignees();
      expect(result).toEqual('');
    });
    it('returns empty string if instance.assignees.type is falsy', function () {
      viewModel.attr('instance', {
        assignees: {}
      });
      viewModel.attr('type', 'Verifier');
      result = viewModel.sliceAssignees();
      expect(result).toEqual('');
    });
    it('returns string with sliced mails if instance.assignees.type is truly',
      function () {
        viewModel.attr('instance', {
          assignees: {
            Verifier: [
              {email: 'mock1@google.com'}, {email: 'mock2@google.com'}
            ]
          }
        });
        viewModel.attr('type', 'Verifier');
        result = viewModel.sliceAssignees();
        expect(result).toEqual('mock1 mock2');
      });
  });
});
