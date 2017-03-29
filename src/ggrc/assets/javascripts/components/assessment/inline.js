/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

(function (can, GGRC) {
  'use strict';

  var tpl = can.view(GGRC.mustache_path +
    '/components/assessment/inline/inline.mustache');
  var innerTplFolder = GGRC.mustache_path + '/components/assessment/inline';

  function getTemplateByType(type) {
    type = can.Mustache.resolve(type);
    return innerTplFolder + '/' + type + '.mustache';
  }

  GGRC.Components('assessmentInlineEdit', {
    tag: 'assessment-inline-edit',
    template: tpl,
    viewModel: {
      define: {
        readonly: {
          type: 'htmlbool',
          value: false
        },
        isEditable: {
          get: function () {
            return !(this.attr('readonly'));
          }
        }
      },
      titleText: '',
      type: '',
      value: null,
      options: [],
      isSaving: false,
      isEdit: false,
      context: {
        value: null,
        options: null
      },

      _EV_BEFORE_EDIT: 'before-edit',  // before entering the edit mode

      setPerson: function (scope, el, ev) {
        this.attr('context.value', ev.selectedItem.serialize());
      },
      unsetPerson: function (scope, el, ev) {
        ev.preventDefault();
        this.attr('context.value', undefined);
      },

      /**
       * Enter the edit mode if editing is allowed (i.e. the readonly option is
       * not set).
       *
       * If the readonly option is enabled, do not do anything. The same if the
       * beforeEdit handler is not defined, or if the promise it returns is not
       * resolved.
       *
       * @param {can.Map} scope - the scope object itself (this)
       * @param {jQuery.Element} $el - the DOM element that triggered the event
       * @param {jQuery.Event} event - the event object
       */
      enableEdit: function (scope, $el, event) {
        var confirmation;
        var onBeforeEdit = this.$rootEl.attr('can-' + scope._EV_BEFORE_EDIT);

        event.preventDefault();
        event.stopPropagation();

        if (this.attr('readonly')) {
          return;
        }

        if (!onBeforeEdit) {
          this.attr('isEdit', true);
          return;
        }

        confirmation = this.$rootEl.triggerHandler({
          type: this._EV_BEFORE_EDIT
        });

        confirmation.done(function () {
          this.attr('isEdit', true);
        }.bind(this));   // and do nothing if no confirmation by the user
      },
      onCancel: function (scope) {
        var value = scope.attr('value');
        scope.attr('isEdit', false);
        scope.attr('context.value', value);
      },
      onSave: function () {
        var oldValue = this.attr('value');
        var value = this.attr('context.value');

        this.attr('isEdit', false);
        // In case value is String and consists only of spaces - do nothing
        if (typeof value === 'string' && !value.trim()) {
          this.attr('context.value', '');
          value = null;
        }

        if (oldValue === value) {
          return;
        } else if (this.attr('type') === 'person') {
          if (value && oldValue && oldValue.id === value.id) {
            // check instances of value and oldValue.
            // return if instances are exist and ids are equal.
            return;
          }
        }

        this.attr('value', value);
        this.attr('isSaving', true);
      }
    },
    init: function () {
      var viewModel = this.viewModel;
      var value = viewModel.attr('value');

      viewModel.attr('context.value', value);
    },
    events: {
      inserted: function (el) {
        this.viewModel.attr('$rootEl', $(el));
      },
      '{window} mousedown': function (el, ev) {
        var viewModel = this.viewModel;
        var isInside = GGRC.Utils.events.isInnerClick(this.element, ev.target);

        if (!isInside && viewModel.attr('isEdit')) {
          viewModel.onCancel(viewModel);
        }
      }
    },
    helpers: {
      renderInnerTemplateByType: function (type, options) {
        return can.view.render(getTemplateByType(type), options.context);
      }
    }
  });
})(window.can, window.GGRC);
