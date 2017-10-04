/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import './external-data-provider';
import './autocomplete-results';
import '../spinner/spinner';
import template from './external-data-autocomplete.mustache';

/**
 * The autocomplete component used to load data from external sources.
 * When user picks an external item, system will create corresponding item in database.
 */
export default GGRC.Components('externalDataAutocomplete', {
  tag: 'external-data-autocomplete',
  template: template,
  viewModel: {
    define: {
      /**
       * The flag indicating that results will be rendered.
       * @type {Boolean}
       */
      renderResults: {
        value: false,
        get() {
          let showResults = this.attr('showResults');
          let minLength = this.attr('minLength');
          let searchCriteria = this.attr('searchCriteria');

          let result = showResults && searchCriteria.length >= minLength;

          return result;
        },
      },
    },
    /**
     * The type of model.
     * @type {String}
     */
    type: null,
    /**
     * The search criteria read from input.
     * @type {String}
     */
    searchCriteria: '',
    /**
     * The minimal length of search criteria that run search.
     * @type {Number}
     */
    minLength: 0,
    /**
     * The placeholder that should be displayed in input.
     * @type {String}
     */
    placeholder: '',
    /**
     * Additional CSS classes which should be applid to input element.
     * @type {String}
     */
    extraCssClass: '',
    /**
     * The flag indicating that results should be shown.
     * @type {Boolean}
     */
    showResults: false,
    /**
     * The flag indicating that search criteria should be cleaned after user picks an item.
     * @type {Boolean}
     */
    autoClean: true,
    /**
     * The flag indicating that system is creating corresponding model for external item.
     */
    saving: false,
    /**
     * Opens results list section.
     */
    openResults() {
      this.attr('showResults', true);
    },
    /**
     * Closes results list section.
     */
    closeResults() {
      this.attr('showResults', false);
    },
    /**
     * Updates search criteria and dispatches corresponding event.
     * @param {Object} - input html element.
     */
    setSearchCriteria: _.debounce(function (element) {
      let newCriteria = element.val();
      this.attr('searchCriteria', newCriteria);
      this.dispatch({
        type: 'criteriaChanged',
        value: newCriteria,
      });
    }, 500),
    /**
     * Creates model in system and dispatches corresponding event.
     * @param {Object} item - an item picked by user.
     * @return {can.Model} - corresponding system model.
     */
    onItemPicked(item) {
      let type = this.attr('type');
      let model = new CMS.Models[type](item);
      model.attr('context', null);
      model.attr('external', true);

      this.attr('saving', true);
      model.save().then(()=> {
        if (this.attr('autoClean')) {
          this.attr('searchCriteria', '');
        }

        this.dispatch({
          type: 'itemSelected',
          selectedItem: model,
        });
      }).always(()=> {
        this.attr('saving', false);
      });

      return model;
    },
  },
});
