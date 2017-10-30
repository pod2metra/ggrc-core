/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from
  '../../../mustache/components/bulk-update-button/bulk-update-button.mustache';
  import updateService from '../../plugins/utils/bulk-update-service';

export default can.Component.extend({
  tag: 'bulk-update-button',
  template: template,
  viewModel: {
    model: null,
  },
  events: {
    'a click': function (el) {
      var model = this.viewModel.attr('model');
      var type = model.model_singular;
      GGRC.Controllers.ObjectBulkUpdate.launch(el, {
        object: type,
        type: type,
        callback: this.updateObjects.bind(this),
      });
    },
    updateObjects: function (context, args) {
      var model = this.viewModel.attr('model');
      var modelShortName = model.title_singular;
      var modelShortNamePl = model.title_plural;
      var progressMessage = _.template(`${modelShortName} update is in progress.
        This may take several minutes`);
      var resultMessage = _.template('No ${modelShortNamePl} were updated.');

      context.closeModal();
      GGRC.Errors.notifier('progress', progressMessage);
      updateService.update(model, args.selected, args.options)
        .then(function (res) {
          var updated = _.filter(res, {status: 'updated'});
          var updatedCount = updated.length;
          if (updatedCount > 0) {
            resultMessage = _.template(`${updatedCount} ` + (updatedCount === 1 ?
              `${modelShortName} was ` :
              `${modelShortNamePl} were `) +
              `updated successfully`);
          }

          GGRC.Errors.notifier('info', resultMessage({
            modelShortName: modelShortName,
            modelShortNamePl: modelShortNamePl,
          }));

          can.trigger($('tree-widget-container'), 'refreshTree');
        });
    },
  },
});
