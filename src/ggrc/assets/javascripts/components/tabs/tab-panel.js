/*!
 Copyright (C) 2017 Google Inc., authors, and contributors
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

(function (can, GGRC) {
  'use strict';

  GGRC.Components('tabPanel', {
    tag: 'tab-panel',
    template: can.view(
      GGRC.mustache_path + '/components/tabs/tab-panel.mustache'
    ),
    viewModel: {
      active: false,
      titleText: '@',
      panels: [],
      tabIndex: null,
      addPanel: function () {
        var panels = this.attr('panels');
        var isAlreadyAdded = panels.indexOf(this) > -1;
        if (isAlreadyAdded) {
          return;
        }
        this.attr('tabIndex', Date.now());
        panels.push(this);
      },
      removePanel: function () {
        var itemTabIndex = this.attr('tabIndex');
        var panels = this.attr('panels');
        var indexToRemove;

        panels.each(function (panel, index) {
          if (panel.attr('tabIndex') === itemTabIndex) {
            indexToRemove = index;
            return false;
          }
        });
        if (indexToRemove > -1) {
          panels.splice(indexToRemove, 1);
        }
      }
    },
    events: {
      /**
       * On Components rendering finished add this viewModel to `panels` list
       */
      inserted: function () {
        this.viewModel.addPanel();
      },
      removed: function () {
        this.viewModel.removePanel();
      }
    }
  });
})(window.can, window.GGRC);
