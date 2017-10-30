/*
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */
import template from
  '../../../mustache/components/object-bulk-update/object-bulk-update.mustache';

export default can.Component.extend({
  tag: 'object-bulk-update',
  template: template,
  viewModel: function (attrs, parentViewModel) {
    return GGRC.VM.ObjectOperationsBaseVM.extend({
      type: attrs.type,
      object: attrs.object,
      availableTypes: function () {
        var object = this.attr('object');
        var type = GGRC.Mappings.getMappingType(object);
        return type;
      },
      reduceToOwnedItems: true,
    });
  },
});
