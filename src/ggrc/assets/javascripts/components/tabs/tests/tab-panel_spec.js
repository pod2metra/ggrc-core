/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

describe('GGRC.Components.tabPanel', function () {
  'use strict';

  var viewModel;

  describe('.addPanel() method', function () {
    beforeEach(function () {
      viewModel = GGRC.Components.getViewModel('tabPanel');
    });

    it('should add viewModel reference to the Panels List', function () {
      viewModel.addPanel();
      expect(viewModel.attr('panels').indexOf(viewModel) > -1).toBe(true);
    });

    it('should add viewModel reference only once the Panels List', function () {
      viewModel.addPanel();
      viewModel.addPanel();
      expect(viewModel.attr('panels').indexOf(viewModel) > -1).toBe(true);
      expect(viewModel.attr('panels').length).toBe(1);
    });
  });

  describe('removePanel() method', function () {
    beforeEach(function () {
      viewModel = GGRC.Components.getViewModel('tabPanel');
    });

    it('should remove viewModel reference from the Panels List', function () {
      viewModel.addPanel();
      viewModel.removePanel();
      expect(viewModel.attr('panels').indexOf(viewModel) < 0).toBe(true);
    });

    it('should do nothing ' +
      'if this is no panel in the Panels List', function () {
      viewModel.addPanel();
      viewModel.removePanel();
      // Call the second remove
      viewModel.removePanel();
      expect(viewModel.attr('panels').indexOf(viewModel) < 0).toBe(true);
    });
  });
});
