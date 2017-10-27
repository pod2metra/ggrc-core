/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

import template from
  '../../../mustache/components/bulk-update-button/bulk-update-button.mustache';

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
      });
    },
  },
});
