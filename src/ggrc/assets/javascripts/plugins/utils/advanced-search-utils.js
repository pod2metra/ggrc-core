/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

(function (GGRC, can, _) {
  'use strict';

  GGRC.Utils.AdvancedSearch = (function () {
    /**
     * Factory allowing to create Advanced Search Filter Items.
     */
    var create = {
      /**
       * Creates Filter Attribute.
       * @param {object} value - Filter Attribute data.
       * @return {object} - Attribute model.
       */
      attribute: function (value) {
        return {
          type: 'attribute',
          value: value || { }
        };
      },
      /**
       * Creates Group.
       * @param {Array} value - Group data.
       * @return {object} - Group model.
       */
      group: function (value) {
        return {
          type: 'group',
          value: value || []
        };
      },
      /**
       * Creates Operator.
       * @param {string} value - Operator name.
       * @return {object} - Operator model.
       */
      operator: function (value) {
        return {
          type: 'operator',
          value: value || ''
        };
      },
      /**
       * Creates Filter State
       * @param {object} value - State data.
       * @return {object} - State model.
       */
      state: function (value) {
        return {
          type: 'state',
          value: value || { }
        };
      },
      /**
       * Creates Mapping Criteria
       * @param {object} value - Mapping Criteria data.
       * @return {object} - Mapping Criteria model.
       */
      mappingCriteria: function (value) {
        return {
          type: 'mappingCriteria',
          value: value || { }
        };
      }
    };

    /**
     * Contains rich Status Filter operators.
     */
    var richOperators = {
      /**
       * @param {Array} values - filter statements.
       * @param {String} modelName - model name
       * @return {string} - filter string.
       */
      ANY: function (values, modelName) {
        var statusField = GGRC.Utils.State.getStatusFieldName(
          modelName);
        return _.map(values, function (value) {
          return '"' + statusField + '"="' + value + '"';
        }).join(' OR ');
      },
      /**
       * @param {Array} values - filter statements.
       * @param {String} modelName - model name
       * @return {string} - filter string.
       */
      NONE: function (values, modelName) {
        var statusField = GGRC.Utils.State.getStatusFieldName(
          modelName);
        return _.map(values, function (value) {
          return '"' + statusField + '"!="' + value + '"';
        }).join(' AND ');
      },
    };

    /**
     * Contains QueryAPI filter builders.
     */
    var builders = {
      attribute: attributeToFilter,
      operator: operatorToFilter,
      state: stateToFilter,
      group: groupToFilter,
      mappingCriteria: mappingCriteriaToFilter
    };
    /**
     * Transforms Filter Attribute model to valid QueryAPI filter string.
     * @param {object} attribute - Filter Attribute model value.
     * @return {string} - Valid QueryAPI filter string.
     */
    function attributeToFilter(attribute) {
      return '"' + attribute.field +
             '" ' + attribute.operator +
             ' "' + attribute.value.trim() + '"';
    }
    /**
     * Transforms Operator model to valid QueryAPI filter string.
     * @param {object} operator - Operator model value.
     * @return {string} - Valid QueryAPI filter string.
     */
    function operatorToFilter(operator) {
      return ' ' + operator + ' ';
    }
    /**
     * Transforms State model to valid QueryAPI filter string.
     * @param {object} state - State model value.
     * @return {string} - Valid QueryAPI filter string.
     */
    function stateToFilter(state) {
      return '(' + GGRC.Utils.State.buildStatusFilter(
        state.items,
        richOperators[state.operator],
        state.modelName) + ')';
    }
    /**
     * Transforms Group model to valid QueryAPI filter string.
     * @param {array} items - Group model value.
     * @param {Array} request - Collection of QueryAPI sub-requests.
     * @return {string} - Valid QueryAPI filter string.
     */
    function groupToFilter(items, request) {
      return '(' + buildFilter(items, request) + ')';
    }
    /**
     * Transforms Mapping Criteria model to valid QueryAPI filter string.
     * @param {object} criteria - Mapping Criteria model value.
     * @param {Array} request - Collection of QueryAPI sub-requests.
     * @return {string} - Valid QueryAPI filter string.
     */
    function mappingCriteriaToFilter(criteria, request) {
      var criteriaId = addMappingCriteria(criteria, request);
      return previousToFilter(criteriaId);
    }
    /**
     * Creates filter based on reauest id.
     * @param {number} requestId - index of QueryApi request.
     * @return {string} - Valid QueryAPI filter string.
     */
    function previousToFilter(requestId) {
      return '#__previous__,' + requestId + '#';
    }
    /**
     * Adds Mapping Criteria as separate QueryAPI request.
     * @param {object} mapping - Mapping Criteria model value.
     * @param {Array} request - Collection of QueryAPI sub-requests.
     * @return {number} - QueryAPI request id.
     */
    function addMappingCriteria(mapping, request) {
      var filterObject = GGRC.query_parser
        .parse(attributeToFilter(mapping.filter.value));
      var relevantResult;
      if (mapping.mappedTo) {
        relevantResult =
          builders[mapping.mappedTo.type](mapping.mappedTo.value, request);
        filterObject = GGRC.query_parser.join_queries(
          filterObject,
          GGRC.query_parser.parse(relevantResult)
        );
      }
      request.push({
        object_name: mapping.objectName,
        type: 'ids',
        filters: filterObject
      });
      return request.length - 1;
    }
    /**
     * Builds QueryAPI valid filter based on Advanced Search models.
     * @param {Array} data - Collection of Advanced Search models.
     * @param {Array} request - Collection of QueryAPI sub-requests.
     * @return {string} - valid QueryAPI filter string.
     */
    function buildFilter(data, request) {
      var result = '';
      request = request || [];
      _.each(data, function (item) {
        result += builders[item.type](item.value, request);
      });
      return result;
    }

    return {
      buildFilter: buildFilter,
      create: create
    };
  })();
})(window.GGRC, window.can, window._);
