/*!
  Copyright (C) 2017 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

describe('CMS.Models.Cacheable', function () {
  'use strict';

  describe('setup_custom_attributes() method', function () {
    var instance;

    function customAttrFactory(id, type, title) {
      return new can.Map({
        id: id,
        attribute_type: type,
        title: title
      });
    }

    beforeEach(function () {
      instance = new can.Model.Cacheable({
        custom_attribute_definitions: new can.List(),
        custom_attribute_values: new can.List()
      });
    });

    it('sorts custom attribute definitions by ascending IDs', function () {
      var expectedIdOrder;
      var definitions = new can.List([
        customAttrFactory(3, 'Text', 'CA three'),
        customAttrFactory(5, 'Text', 'CA five'),
        customAttrFactory(2, 'Text', 'CA two'),
        customAttrFactory(4, 'Text', 'CA four'),
        customAttrFactory(1, 'Text', 'CA one')
      ]);
      instance.custom_attribute_definitions.replace(definitions);

      instance.setup_custom_attributes();

      expectedIdOrder = _.map(instance.custom_attribute_definitions, 'id');
      expect(expectedIdOrder).toEqual([1, 2, 3, 4, 5]);
    });

    it('skips sorting if no custom attribute definitions', function () {
      var actualOrder;
      instance.attr('custom_attribute_definitions', undefined);
      instance.setup_custom_attributes();
      actualOrder = _.map(instance.custom_attribute_definitions, 'id');
      expect(actualOrder).toEqual([]);
    });
  });

  describe('mark_for_addition() method', function () {
    var instance;
    var obj;
    var extraAttrs;
    var options;
    var joinAttr;

    beforeEach(function () {
      instance = new can.Model.Cacheable({
        related_sources: new can.Map()
      });
      spyOn(instance, 'remove_duplicate_pending_joins');
      obj = {};
      extraAttrs = {field: 'not empty'};
      options = 'options';
      joinAttr = 'related_sources';
    });

    it('calls remove_duplicate_pending_joins() method', function () {
      instance.mark_for_addition(joinAttr, obj, extraAttrs, options);
      expect(instance.remove_duplicate_pending_joins)
        .toHaveBeenCalledWith(obj);
    });

    it('pushes specified object to _pending_joins', function () {
      instance.mark_for_addition(joinAttr, obj, extraAttrs, options);
      obj = jasmine.objectContaining(obj);
      extraAttrs = jasmine.objectContaining(extraAttrs);

      expect(instance._pending_joins[0].how).toEqual('add');
      expect(instance._pending_joins[0].what).toEqual(obj);
      expect(instance._pending_joins[0].through).toEqual(joinAttr);
      expect(instance._pending_joins[0].extra).toEqual(extraAttrs);
      expect(instance._pending_joins[0].opts).toEqual(options);
    });
  });

  describe('remove_duplicate_pending_joins() method', function () {
    var instance;
    var obj;
    var extraAttrs;

    beforeEach(function () {
      instance = new can.Model.Cacheable({
        related_sources: new can.Map()
      });
      obj = new can.Map({});
      extraAttrs = new can.Map({field: 'not empty'});
    });

    it('sets empty array to _pending_joins if it is undefined', function () {
      instance.attr('_pending_joins', undefined);
      instance.remove_duplicate_pending_joins(obj);
      expect(instance._pending_joins.length).toEqual(0);
    });

    it('removes elemnts from _pending_joins' +
      'if elements fields "what" equals to parametr',
      function () {
        instance._pending_joins.push({
          what: obj
        });
        instance.remove_duplicate_pending_joins(obj);
        expect(instance._pending_joins.length).toEqual(0);
      });

    it('does not remove elemnts from _pending_joins ' +
      'if elements field "what" does not equal to parametr',
      function () {
        instance._pending_joins.push({
          what: obj,
          extra: extraAttrs
        });
        obj = new can.Map({});
        instance.remove_duplicate_pending_joins(obj, extraAttrs);
        expect(instance._pending_joins.length).toEqual(1);
      });
  });
});
