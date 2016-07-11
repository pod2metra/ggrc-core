/*!
    Copyright (C) 2016 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

(function (can, $) {
  'use strict';

  GGRC.Components('datepicker', {
    tag: 'datepicker',
    template: can.view(
      GGRC.mustache_path +
      '/components/datepicker/datepicker.mustache'
    ),
    scope: {
      date: null,
      format: '@',
      label: '@',
      helptext: '@',
      isShown: false,
      pattern: 'MM/DD/YYYY',
      setMinDate: null,
      setMaxDate: null,
      persistent: false,
      required: false,
      _date: null,
      onSelect: function (val, ev) {
        this.attr('_date', val);
        this.attr('date', val);
      },
      onFocus: function (el, ev) {
        this.attr('isShown', true);
      }
    },
    init: function (el, options) {
      var $el = $(el);
      var attrVal = $el.attr('persistent');
      var persistent;
      var scope = this.scope;

      if (attrVal === '' || attrVal === 'false') {
        persistent = false;
      } else if (attrVal === 'true') {
        persistent = true;
      } else {
        persistent = Boolean(scope.attr('persistent'));
      }

      scope.attr('persistent', persistent);
    },
    events: {
      inserted: function () {
        var element = this.element.find('.datepicker__calendar');
        var date = this.getDate(this.scope.date);
        var datepicker = element.datepicker({
          altField: this.element.find('.datepicker__input'),
          onSelect: this.scope.onSelect.bind(this.scope)
        }).data('datepicker');

        element.datepicker('setDate', date);
        this.scope.attr('_date', date);
        this.scope.attr('picker', element);
        this.scope.attr('datepicker', datepicker);
      },
      getDate: function (date) {
        if (date instanceof Date) {
          date = moment(date).format(this.scope.pattern);
        } else if (!this.isValidDate(date)) {
          date = null;
        }
        return date;
      },
      isValidDate: function (date) {
        return moment(date, this.scope.pattern, true).isValid();
      },
      '{scope} setMinDate': function (scope, ev, date) {
        date = this.isValidDate(date) ? date : null;
        this.scope.picker.datepicker('option', 'minDate', date);
      },
      '{scope} setMaxDate': function (scope, ev, date) {
        date = this.isValidDate(date) ? date : null;
        this.scope.picker.datepicker('option', 'maxDate', date);
      },
      '{window} mousedown': function (el, ev) {
        var isInside;

        if (this.scope.attr('persistent')) {
          return;
        }
        isInside = this.element.has(ev.target).length ||
                   this.element.is(ev.target);

        if (this.scope.isShown && !isInside) {
          this.scope.attr('isShown', false);
        }
      }
    },
    helpers: {
      isHidden: function (opts) {
        if (this.attr('isShown') || this.attr('persistent')) {
          return opts.inverse();
        }
        return opts.fn();
      }
    }
  });
})(window.can, window.can.$);
