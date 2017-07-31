/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */
(function (can, GGRC) {
  'use strict';

  GGRC.Components('mapperFilter', {
    tag: 'mapper-filter',
    template: can.view(
      GGRC.mustache_path +
      '/components/unified-mapper/mapper-filter.mustache'
    ),
    viewModel: {
      define: {
        text: {
          type: 'string',
          set: function (newValue) {
            this.attr('filter', newValue.replace(/\\/g, '\\\\'));
            this.checkExpression(newValue);
            return newValue;
          }
        }
      },
      isExpression: false,
      checkExpression: function (filter) {
        var currentFilter = GGRC.query_parser.parse(filter);
        var isExpression =
          !!currentFilter && !!currentFilter.expression.op &&
          currentFilter.expression.op.name !== 'text_search' &&
          currentFilter.expression.op.name !== 'exclude_text_search';
        this.attr('isExpression', isExpression);
      },
      onSubmit: function () {
        this.dispatch('submit');
      },
      reset: function () {
        this.attr('text', '');
      }
    },
    events: {
      '#mapper-filter input': function (el) {
        this.viewModel.attr('text', el.val());
      }
    }
  });
})(window.can, window.GGRC);
