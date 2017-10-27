/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from './templates/tree-item-actions.mustache';

(function (can, GGRC) {
  'use strict';

  var forbiddenEditList = ['Cycle', 'CycleTaskGroup'];
  var forbiddenMapList = ['Workflow'];

  var viewModel = can.Map.extend({
    define: {
      deepLimit: {
        type: 'number',
        value: 0
      },
      canExpand: {
        type: 'boolean',
        value: false
      },
      expandIcon: {
        type: 'string',
        get: function () {
          return this.attr('expanded') ? 'compress' : 'expand';
        }
      },
      expanderTitle: {
        type: 'string',
        get: function () {
          return this.attr('expanded') ? 'Collapse tree' : 'Expand tree';
        }
      },
      isSnapshot: {
        type: 'boolean',
        get: function () {
          return GGRC.Utils.Snapshots.isSnapshot(this.attr('instance'));
        }
      },
      isAllowedToEdit: {
        type: 'boolean',
        get: function () {
          var type = this.attr('instance.type');
          var isSnapshot = this.attr('isSnapshot');
          var isArchived = this.attr('instance.archived');
          var isInForbiddenList = forbiddenEditList.indexOf(type) > -1;
          return !(isSnapshot || isInForbiddenList || isArchived);
        }
      },
      isAllowedToMap: {
        type: 'boolean',
        get: function () {
          var type = this.attr('instance.type');
          var isAllowedToEdit = this.attr('isAllowedToEdit');
          var isInForbiddenList = forbiddenMapList.indexOf(type) > -1;

          return isAllowedToEdit && !isInForbiddenList;
        }
      }
    },
    maximizeObject: function (scope, el, ev) {
      ev.preventDefault();
      ev.stopPropagation();

      this.dispatch({
        type: 'preview',
        element: el
      });
    },
    $el: null,
    openObject: function (scope, el, ev) {
      ev.stopPropagation();
    },
    expand: function (scope, el, ev) {
      this.dispatch('expand');
      ev.stopPropagation();
    },
    subTreeTypes: function () {
      can.trigger(this.attr('$el'), 'childTreeTypes');
    },
    instance: null,
    childOptions: null,
    addItem: null,
    allowMapping: null,
    isAllowToExpand: null,
    childModelsList: null,
    expanded: false,
    activated: false,
    showReducedIcon: function () {
      var pages = ['Workflow'];
      var instanceTypes = [
        'Cycle',
        'CycleTaskGroup',
        'CycleTaskGroupObjectTask'
      ];
      return _.contains(pages, GGRC.Utils.CurrentPage.getPageType()) &&
        _.contains(instanceTypes, this.attr('instance').type);
    },
    showReducedOptions: function () {
      var pages = ['Workflow'];
      var instanceTypes = [
        'Cycle',
        'CycleTaskGroup',
      ];
      return _.contains(pages, GGRC.Utils.CurrentPage.getPageType()) &&
        _.contains(instanceTypes, this.attr('instance').type);
    }
  });

  GGRC.Components('treeItemActions', {
    tag: 'tree-item-actions',
    template: template,
    viewModel: viewModel,
    events: {
      inserted: function () {
        var parents = this.element.parents('sub-tree-wrapper').length;
        var canExpand = parents < this.viewModel.attr('deepLimit');
        this.viewModel.attr('canExpand', canExpand);
        this.viewModel.attr('$el', this.element);
      },
      '.tree-item-actions__content mouseenter': function (el, ev) {
        var vm = this.viewModel;

        if (!vm.attr('activated')) {
          vm.attr('activated', true);
        }
        // event not needed after render of content
        el.off(ev);
      }
    }
  });
})(window.can, window.GGRC);
