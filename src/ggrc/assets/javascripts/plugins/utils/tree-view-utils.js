/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

(function (GGRC) {
  'use strict';

  /**
   * TreeView-specific utils.
   */
  GGRC.Utils.TreeView = (function () {

    var baseWidgets = GGRC.tree_view.attr('base_widgets_by_type');
    var defaultOrderTypes = GGRC.tree_view.attr('defaultOrderTypes');
    var allTypes = Object.keys(baseWidgets.serialize());
    var orderedModelsForSubTier = {};

    allTypes.forEach(function (type) {
      var related = baseWidgets[type].slice(0);

      orderedModelsForSubTier[type] = _.chain(related)
        .map(function (type) {
          return {
            name: type,
            order: defaultOrderTypes[type]
          };
        })
        .sortByAll(['order', 'name'])
        .map('name')
        .value();
    });

    // Define specific rules for Workflow models
    orderedModelsForSubTier.Cycle = ['CycleTaskGroup'];
    orderedModelsForSubTier.CycleTaskGroup = ['CycleTaskGroupObjectTask'];

    /**
     * Get available and selected columns for Model type
     * @param {String} modelType - Model type.
     * @param {Object} displayPrefs - Display preferences.
     * @return {Object} Table columns configuration.
     */
    function getColumnsForModel(modelType, displayPrefs) {
      var Cacheable = can.Model.Cacheable;
      var Model = CMS.Models[modelType];
      var modelDefinition = Model().class.root_object;
      var modelName = Model.model_singular;
      var mandatoryAttrNames =
        Model.tree_view_options.mandatory_attr_names ||
        Cacheable.tree_view_options.mandatory_attr_names;
      var savedAttrList = displayPrefs ?
        displayPrefs.getTreeViewHeaders(modelName) : [];
      var displayAttrNames =
        savedAttrList.length ? savedAttrList :
          (Model.tree_view_options.display_attr_names ||
          Cacheable.tree_view_options.display_attr_names);
      var disableConfiguration =
        !!Model.tree_view_options.disable_columns_configuration;
      var mandatoryColumns;
      var displayColumns;

      var attrs =
        can.makeArray(
          Model.tree_view_options.mapper_attr_list ||
          Model.tree_view_options.attr_list ||
          Cacheable.attr_list
        ).map(function (attr) {
          attr = Object.assign({}, attr);
          if (!attr.attr_sort_field) {
            attr.attr_sort_field = attr.attr_name;
          }
          return attr;
        }).sort(function (a, b) {
          if (a.order && !b.order) {
            return -1;
          } else if (!a.order && b.order) {
            return 1;
          }
          return a.order - b.order;
        });

      var customAttrs = disableConfiguration ?
        [] :
        GGRC.custom_attr_defs
          .filter(function (def) {
            return def.definition_type === modelDefinition &&
              def.attribute_type !== 'Rich Text';
          }).map(function (def) {
            return {
              attr_title: def.title,
              attr_name: def.title,
              attr_sort_field: def.title,
              display_status: false,
              attr_type: 'custom'
            };
          });

      var allAttrs = attrs.concat(customAttrs);

      if (disableConfiguration) {
        return {
          available: allAttrs,
          selected: allAttrs,
          disableConfiguration: true
        };
      }

      displayAttrNames = displayAttrNames.concat(mandatoryAttrNames);

      allAttrs.forEach(function (attr) {
        attr.display_status = displayAttrNames.indexOf(attr.attr_name) !== -1;
        attr.mandatory = mandatoryAttrNames.indexOf(attr.attr_name) !== -1;
      });

      mandatoryColumns = allAttrs.filter(function (attr) {
        return attr.mandatory;
      });

      displayColumns = allAttrs.filter(function (attr) {
        return attr.display_status && !attr.mandatory;
      });

      return {
        available: allAttrs,
        selected: mandatoryColumns.concat(displayColumns),
        disableConfiguration: false
      };
    }

    /**
     * Set selected columns for Model type
     * @param {String} modelType - Model type.
     * @param {Array} columnNames - Array of column names.
     * @param {Object} displayPrefs - Display preferences.
     * @return {Object} Table columns configuration.
     */
    function setColumnsForModel(modelType, columnNames, displayPrefs) {
      var availableColumns =
        getColumnsForModel(modelType, displayPrefs).available;
      var selectedColumns = [];
      var selectedNames = [];

      availableColumns.forEach(function (attr) {
        if (columnNames.indexOf(attr.attr_name) !== -1) {
          attr.display_status = true;
          selectedColumns.push(attr);
          if (!attr.mandatory) {
            selectedNames.push(attr.attr_name);
          }
        } else {
          attr.display_status = false;
        }
      });

      if (displayPrefs) {
        displayPrefs.setTreeViewHeaders(
          CMS.Models[modelType].model_singular,
          selectedNames
        );
        displayPrefs.save();
      }

      return {
        available: availableColumns,
        selected: selectedColumns
      };
    }

    function displayTreeSubpath(el, path, attemptCounter) {
      var rest = path.split('/');
      var type = rest.shift();
      var id = rest.shift();
      var selector = '[data-object-type=\'' + type +
        '\'][data-object-id=' + id + ']';
      var $node;
      var nodeController;
      var controller;

      if (!attemptCounter) {
        attemptCounter = 0;
      }

      rest = rest.join('/');

      if (type || id) {
        $node = el.find(selector);

        // sometimes nodes haven't loaded yet, wait for them
        if (!$node.size() && attemptCounter < 5) {
          setTimeout(function () {
            displayTreeSubpath(el, path, attemptCounter + 1);
          }, 100);
          return undefined;
        }

        if (!rest.length) {
          controller = $node
            .closest('.cms_controllers_tree_view_node')
            .control();

          if (controller) {
            controller.select();
          }
        } else {
          nodeController = $node.control();
          if (nodeController && nodeController.display_path) {
            return nodeController.display_path(rest);
          }
        }
      }
      return can.Deferred().resolve();
    }

    function getModelsForSubTier(model) {
      return orderedModelsForSubTier[model] || [];
    }

    return {
      getColumnsForModel: getColumnsForModel,
      setColumnsForModel: setColumnsForModel,
      displayTreeSubpath: displayTreeSubpath,
      getModelsForSubTier: getModelsForSubTier
    };
  })();
})(window.GGRC);
