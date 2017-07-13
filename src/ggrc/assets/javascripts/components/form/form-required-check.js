/*!
 Copyright (C) 2017 Google Inc., authors, and contributors
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

(function (can, GGRC) {
  'use strict';
  var tag = 'form-required-check';
  /**
   * Form Required Information Verification Component
   */
  GGRC.Components('formRequiredCheck', {
    tag: tag,
    viewModel: {
      define: {
        hasValidationErrors: {
          type: 'boolean',
          get: function () {
            return this.attr('fields')
              .filter(function (field) {
                var isEmpty = field.attr('validation.mandatory') &&
                  field.attr('validation.empty');
                var isNotValid = !field.attr('validation.valid');
                return isEmpty || isNotValid;
              }).length;
          }
        },
        evidenceAmount: {
          type: 'number',
          set: function (newValue, setValue) {
            setValue(newValue);
            this.updateEvidenceValidation();
          }
        },
        isEvidenceRequired: {
          get: function () {
            return this.hasMissingEvidence();
          }
        }
      },
      updateEvidenceValidation: function () {
        var isEvidenceRequired = this.attr('isEvidenceRequired');
        this.attr('fields')
          .filter(function (item) {
            return item.attr('type') === 'dropdown';
          })
          .each(function (item) {
            var isCommentRequired;
            if (item.attr('validationConfig') &&
              (item.attr('validationConfig')[item.attr('value')] === 2 ||
                item.attr('validationConfig')[item.attr('value')] === 3)) {
              isCommentRequired = item.attr('errorsMap.comment');
              item.attr('errorsMap.evidence', isEvidenceRequired);
              item.attr('validation.valid',
                !isEvidenceRequired && !isCommentRequired);
            }
          });
      },
      hasMissingEvidence: function () {
        var optionsWithEvidence = this.attr('fields')
              .filter(function (item) {
                return item.attr('type') === 'dropdown' &&
                  item.attr('validationConfig') &&
                  (item.attr('validationConfig')[item.attr('value')] === 2 ||
                item.attr('validationConfig')[item.attr('value')] === 3);
              }).length;
        return optionsWithEvidence > this.attr('evidenceAmount');
      },
      performValidation: function (field, value) {
        var isEvidenceRequired = this.attr('isEvidenceRequired');
        this.updateEvidenceValidation();
        field.attr('validation.empty', !(value));
        if (field.attr('type') === 'dropdown' &&
          field.attr('validationConfig')) {
          if (!field.attr('validationConfig')[value]) {
            field.attr('errorsMap.evidence', false);
            field.attr('errorsMap.comment', false);
            field.attr('validation.valid', true);
          }
          if (field.attr('validationConfig')[value] === 0) {
            field.attr('errorsMap.evidence', false);
            field.attr('errorsMap.comment', false);
            field.attr('validation.valid', true);
          }
          if (field.attr('validationConfig')[value] === 2) {
            field.attr('errorsMap.evidence', isEvidenceRequired);
            field.attr('errorsMap.comment', false);
            field.attr('validation.valid', !isEvidenceRequired);
            if (isEvidenceRequired) {
              this.dispatch({
                type: 'validationChanged',
                field: field
              });
            }
          }
          if (field.attr('validationConfig')[value] === 1) {
            field.attr('errorsMap.evidence', false);
            field.attr('errorsMap.comment', true);
            field.attr('validation.valid', false);
            this.dispatch({
              type: 'validationChanged',
              field: field
            });
          }
          if (field.attr('validationConfig')[value] === 3) {
            field.attr('errorsMap.evidence', isEvidenceRequired);
            field.attr('errorsMap.comment', true);
            field.attr('validation.valid', false);
            this.dispatch({
              type: 'validationChanged',
              field: field
            });
          }
        }
      }
    }
  });
})(window.can, window.GGRC);
