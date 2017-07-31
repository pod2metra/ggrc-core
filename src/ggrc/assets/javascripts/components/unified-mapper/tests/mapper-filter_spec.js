/*!
  Copyright (C) 2017 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

describe('GGRC.Components.mapperFilter', function () {
  'use strict';
  var viewModel;

  beforeAll(function () {
    viewModel = GGRC.Components.getViewModel('mapperFilter');
  });

  describe('text set()', function () {
    beforeEach(function () {
      spyOn(viewModel, 'checkExpression');
    });

    it('sets viewModel.filter', function () {
      viewModel.attr('filter', '');
      viewModel.attr('text', 'program');
      expect(viewModel.attr('filter')).toEqual('program');
    });

    it('calls checkExpression()', function () {
      viewModel.attr('text', 'program');
      expect(viewModel.checkExpression)
        .toHaveBeenCalledWith('program');
    });
  });

  describe('checkExpression() method', function () {
    it('sets true to viewModel.isExpression if filter is expression',
      function () {
        viewModel.checkExpression('title != program');
        expect(viewModel.attr('isExpression')).toEqual(true);
      });
    it('sets false to viewModel.isExpression if input is empty',
      function () {
        viewModel.checkExpression('');
        expect(viewModel.attr('isExpression')).toEqual(false);
      });
    it('sets false to viewModel.isExpression if input is text for search',
      function () {
        viewModel.checkExpression('program');
        expect(viewModel.attr('isExpression')).toEqual(false);
      });
    it('sets false to viewModel.isExpression if input is excluded text',
      function () {
        viewModel.checkExpression('!~ program');
        expect(viewModel.attr('isExpression')).toEqual(false);
      });
  });

  describe('onSubmit() method', function () {
    beforeEach(function () {
      spyOn(viewModel, 'dispatch');
    });

    it('dispatches submit event', function () {
      viewModel.onSubmit();
      expect(viewModel.dispatch).toHaveBeenCalledWith('submit');
    });
  });

  describe('reset() method', function () {
    it('updates viewModel.text', function () {
      viewModel.attr('text', 'stub');
      viewModel.reset();
      expect(viewModel.attr('text')).toEqual('');
    });
  });
});
