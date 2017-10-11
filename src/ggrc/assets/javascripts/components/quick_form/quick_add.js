/*!
    Copyright (C) 2017 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

(function (can, $) {
  'use strict';
  /*
    Below this line we're defining a few can.Components, which are in this file
    because they work similarly to the quick form controller (in fact, you should
    expect the quick form controller to be refactored into a component in the
    future) but they share no code with the quick form controller.

    the first component is quick add.  It is meant to have one or more form elements
    and a data-toggle="submit" link which will create a new join object between
    the parent instance and some selected option instance (likely picked through an
    autocomplete dropdown).

    Technically you can choose your instance however you want, as long as you find
    some way of getting its value into the component scope.  Extending this component
    with other methods to do that is fine.  You can also just pass it in when
    instantiating the component.
  */
  GGRC.Components('quickAdd', {
    tag: 'ggrc-quick-add',
    viewModel: {
      parent_instance: null,
      source_mapping: null,
      join_model: '@',
      model: null,
      delay: '@',
      quick_create: "@",
      type: '@',
      verify_event: "@",
      modal_description: "@",
      modal_title: "@",
      modal_button: "@",
      attributes: {},
      define: {
        deferred: {
          type: 'boolean',
          'default': false
        }
      },
      create_url: function () {
        var value = $.trim(this.element.find("input[type='text']").val());
        var dfd;
        var context = this.viewModel.attr('parent_instance.context') ||
            new CMS.Models.Context({id: null});
        var attrs = {
          link: value,
          title: value,
          context: context,
          document_type: this.viewModel.attr('type'),
          created_at: new Date(),
          isDraft: true,
          _stamp: Date.now()
        };
        this.viewModel.dispatch({type: 'beforeCreate', items: [attrs]});
        // We are not validating the URL because application can locally we can
        // have URL's that are valid, but they wouldn't pass validation i.e.
        // - hi/there
        // - hi.something
        // - http://something.com etc
        // and thus we decided to validate just string existence
        if (!value || _.isEmpty(value)) {
          dfd = can.Deferred();
          dfd.reject({
            message: 'Please enter a URL'
          });
          return dfd.promise();
        }
        dfd = new CMS.Models.Document(attrs);
        return dfd.save();
      }
    },
    events: {
      init: function () {
        this.scope.attr('controller', this);
      },
      // The inserted event fires when the component content is added to the DOM.
      //  At this time, live bound rendering should be resolved, which is not the
      //  case during init.
      inserted: function (el) {
        this.element.find('input:not([data-mapping], [data-lookup])')
          .each(function (i, el) {
            this.viewModel.attributes.attr($(el).attr('name'), $(el).val());
          }.bind(this));
      },
      'a[data-toggle=submit]:not(.disabled):not([disabled]) click': function (el, ev) {
        var scope = this.viewModel;
        var join_model_class;
        var join_object;
        var quick_create;
        var created_dfd;
        var verify_dfd = can.Deferred();
        scope.attr('disabled', true);
        scope.attr('verify_event',
          !!this.element.context.attributes.verify_event);

        // Update modal description only if verification is needed
        if (this.element.context.attributes.modal_description) {
          scope.attr('modal_description',
            this.element.context.attributes.modal_description.value);
        }

        if (scope.attr("verify_event")) {
          GGRC.Controllers.Modals.confirm({
            modal_description: scope.attr("modal_description"),
            modal_confirm: scope.attr("modal_button"),
            modal_title: scope.attr("modal_title"),
            button_view: GGRC.mustache_path + "/quick_form/confirm_buttons.mustache"
          }, verify_dfd.resolve, verify_dfd.reject);
        } else {
          verify_dfd.resolve();
        }

        verify_dfd.done(function () {
          if (this.scope.quick_create && this.scope.quick_create !== "@") {
            quick_create = this.scope[this.scope.quick_create].bind(this);
            if (quick_create) {
              created_dfd = quick_create();
              if (!this.scope.deferred) {
                created_dfd
                  .fail(function (error) {
                    $(document.body).trigger('ajax:flash', {
                      error: error.message
                    });
                  })
                  .done(function (data) {
                    this.scope.attr('instance', data);
                  }.bind(this))
                  .always(function () {
                    scope.attr('disabled', false);
                  });
              }
            }
          }
          if (!created_dfd) {
            created_dfd = can.Deferred().resolve();
          }

          if (created_dfd.state() === 'rejected') {
            created_dfd.fail(function (error) {
              var instance = scope.attr('instance');
              scope.dispatch({
                type: 'afterCreate',
                items: [instance],
                success: false
              });
              $(document.body).trigger('ajax:flash', {
                error: error.message
              });
            });
            return;
          }

          if (this.scope.deferred) {
            created_dfd.done(function (instance) {
              this.scope.parent_instance
                .mark_for_addition('related_objects_as_source', instance);
              el.trigger('modal:success', instance);
            }.bind(this));
            return;
          }

          created_dfd.then(function() {
            if (this.scope.join_model && this.scope.join_model !== "@") {
              join_model_class = CMS.Models[this.scope.join_model] || CMS.ModelHelpers[this.scope.join_model];
              join_object = {};
              if (this.scope.join_model === "Relationship") {
                join_object["source"] = this.scope.parent_instance;
                join_object["destination"] = this.scope.instance;
              } else {
                join_object[this.scope.instance.constructor.table_singular] = this.scope.instance;
              }
              join_object = new join_model_class($.extend(
                join_object,
                {
                  context: this.scope.parent_instance.context
                              || new CMS.Models.Context({id : null})
                },
                this.scope.attributes.serialize()
              ));
            } else {
              join_object = GGRC.Mappings.make_join_object(
                this.scope.parent_instance,
                this.scope.instance || this.scope.attributes.instance,
                $.extend({
                  context: this.scope.parent_instance.context
                            || new CMS.Models.Context({id : null})
                          },
                          this.scope.attributes.serialize())
              );
            }
            this.bindXHRToButton(
              join_object.save()
                .done(function () {
                  var instance = scope.attr('instance');
                  el.trigger('modal:success', join_object);

                  scope.dispatch({
                    type: 'afterCreate',
                    items: [instance],
                    success: true
                  });
                })
                .fail(function () {
                  var instance = scope.attr('instance');

                  scope.dispatch({
                    type: 'afterCreate',
                    items: [instance],
                    success: false
                  });
                }));
          }.bind(this))
          .always(function () {
            scope.attr('disabled', false);
          });
        }.bind(this))
        .fail(function () {
          scope.attr('disabled', false);
        });
      },
      // this works like autocomplete_select on all modal forms and
      //  descendant class objects.
      autocomplete_select: function(el, event, ui) {
        var that = this;
        setTimeout(function() {
          that.scope.attr('instance', ui.item);
        });
      },
      "input[null-if-empty] change" : function(el) {
        if (!el.val()) {
          this.scope.attributes.attr(el.attr("name"), null);
        }
      },
      "input:not([data-mapping], [data-lookup]) change" : function(el) {
        this.scope.attributes.attr(el.attr("name"), el.val());
      },
      ".ui-autocomplete-input modal:success" : function(el, ev, data, options) {
        var that = this,
          multi_map = data.multi_map,
          join_model_class,
          join_object;

        if(multi_map){
          var length = data.arr.length,
              my_data;

          if (length == 1){
            my_data = data.arr[0];

            GGRC.Mappings.make_join_object(
              this.scope.parent_instance,
              my_data,
              $.extend({
                context : this.scope.parent_instance.context
                        || new CMS.Models.Context({id : null})
                        },
                        this.scope.attributes.serialize())
            ).save().done(function() {
              that.element.find("a[data-toggle=submit]").trigger("modal:success");
            });
          }

          else{
            for(var i = 0; i < length-1; i++){
              my_data = data.arr[i];

              GGRC.Mappings.make_join_object(
                this.scope.parent_instance,
                my_data,
                $.extend({
                  context : this.scope.parent_instance.context
                          || new CMS.Models.Context({id : null})
                          },
                          this.scope.attributes.serialize())
              ).save().done(function(){});
            }
            my_data = data.arr[length-1];
            GGRC.Mappings.make_join_object(
              this.scope.parent_instance,
              my_data,
              $.extend({
                context : this.scope.parent_instance.context
                        || new CMS.Models.Context({id : null})
                        },
                        this.scope.attributes.serialize())
            ).save().done(function() {
              that.element.find("a[data-toggle=submit]").trigger("modal:success");
            });
          }
          //end multi-map
        } else {

          if (this.scope.join_model && this.scope.join_model !== "@") {
            join_model_class = CMS.Models[this.scope.join_model] || CMS.ModelHelpers[this.scope.join_model];
            join_object = new join_model_class(this.scope.attributes.serialize());
          } else {
            join_object = GGRC.Mappings.make_join_object(
              this.scope.parent_instance,
              data,
              $.extend({
                context : this.scope.parent_instance.context
                          || new CMS.Models.Context({id : null})
                        },
                        this.scope.attributes.serialize())
            );
          }
          join_object.save().done(function() {
             that.element.find("a[data-toggle=submit]").trigger("modal:success");
          });
        }
      }
    },
    helpers: {
      // Mapping-based autocomplete selectors use this helper to
      //  attach the mapping autocomplete ui widget.  These elements should
      //  be decorated with data-mapping attributes.
      mapping_autocomplete : function(options) {
        return function(el) {
          var $el = $(el);
          $el.ggrc_mapping_autocomplete({
            controller : options.contexts.attr("controller"),
            model : $el.data("model"),
            mapping : false
          });
        };
      }
    }
  }, true);
})(window.can, window.can.$);
