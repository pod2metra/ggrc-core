/*!
 Copyright (C) 2017 Google Inc., authors, and contributors
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

(function (can, GGRC) {
  'use strict';

  GGRC.Components('tabContainer', {
    tag: 'tab-container',
    template: can.view(GGRC.mustache_path +
      '/components/tabs/tab-container.mustache'),
    viewModel: {
      selectedTabIndex: 0,
      panels: [],
      /**
       * Activate currently selected panel
       *
       * @param {Object} scope - current item value from `viewModel.panels`
       * @param {jQuery.Element} el - clicked element
       * @param {Object} ev - click event handler
       */
      setActive: function (scope, el, ev) {
        ev.preventDefault();
        this.setActivePanel(scope.attr('tabIndex'));
      },
      /**
       * Update Panels List setting all panels except selected to inactive state
       * @param {Number} tabIndex - id of activated panel
       */
      setActivePanel: function (tabIndex) {
        this.attr('selectedTabIndex', tabIndex);
        this.attr('panels').forEach(function (panel) {
          var isActive = (panel.attr('tabIndex') === tabIndex);
          panel.attr('active', isActive);
        });
      },
      /**
       * Update selected item and set it to the fist item if no previous selection is available
       */
      setDefaultActivePanel: function () {
        var tabIndex = this.attr('selectedTabIndex');
        var panels = this.attr('panels');
        // Select the first panel if tabIndex is not defined
        if (!tabIndex && panels.length) {
          tabIndex = panels[0].attr('tabIndex');
        }
        this.setActivePanel(tabIndex);
      }
    },
    events: {
      /**
       * Update Currently selected Tab on each add/remove of Panels
       */
      '{viewModel.panels} length': function () {
        this.viewModel.setDefaultActivePanel();
      }
    }
  });
})(window.can, window.GGRC);
