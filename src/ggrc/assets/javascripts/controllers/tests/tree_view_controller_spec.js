/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

describe('CMS.Controllers.TreeView', function () {
  'use strict';

  var Ctrl;  // the controller under test

  beforeAll(function () {
    Ctrl = CMS.Controllers.TreeView;
  });

  describe('init() method', function () {
    var ctrlInst;  // fake controller instance
    var dfdSingleton;
    var method;
    var options;
    var $element;

    beforeEach(function () {
      options = {};
      $element = $('<div></div>');

      ctrlInst = {
        element: $element,
        widget_hidden: jasmine.createSpy('widget_hidden'),
        widget_shown: jasmine.createSpy('widget_shown'),
        options: new can.Map(options)
      };

      method = Ctrl.prototype.init.bind(ctrlInst);

      dfdSingleton = new can.Deferred();
      spyOn(
        CMS.Models.DisplayPrefs, 'getSingleton'
      ).and.returnValue(dfdSingleton);
    });

    // test cases here...
  });

  describe('_verifyRelationship() method', function () {
    var ctrlInst;
    var method;
    var relationship;

    beforeEach(function () {
      ctrlInst = {
        options: new can.Map({
          model: {
            shortName: 'foo'
          }
        })
      };

      relationship = new CMS.Models.Relationship();

      method = Ctrl.prototype._verifyRelationship.bind(ctrlInst);
    });

    it('wrong relationship', function () {
      var result;

      relationship.source = {type: 'bar'};
      relationship.destination = {type: 'baz'};

      result = method(relationship, 'foo');

      expect(result).toBeFalsy();
    });

    it('right relationship', function () {
      var result;

      relationship.source = {type: 'bar'};
      relationship.destination = {type: 'foo'};

      result = method(relationship, 'foo');

      expect(result).toBeTruthy();
    });

    it('right relationship for Snapshot', function () {
      var result;

      relationship.source = {type: 'bar'};
      relationship.destination = {type: 'Snapshot'};

      result = method(relationship, 'foo');

      expect(result).toBeTruthy();
    });

    it('right relationship without source', function () {
      var result;

      relationship.destination = {type: 'foo'};

      result = method(relationship, 'foo');

      expect(result).toBeTruthy();
    });

    it('right relationship without destination', function () {
      var result;

      relationship.source = {type: 'foo'};

      result = method(relationship, 'foo');

      expect(result).toBeTruthy();
    });

    it('empty relationship', function () {
      var result;

      result = method(relationship, 'foo');

      expect(result).toBeFalsy();
    });
  });

  describe('update_header() method', function () {
    beforeEach(function () {
      Ctrl.prototype.options = new can.Map({
        model: {
          shortName: 'foo'
        },
        list: []
      });
      Ctrl.prototype.element = $('<div></div>');
      Ctrl.prototype.display_prefs = {
        setFilterHidden: function () {},
        save: function () {}
      };

      spyOn(Ctrl.prototype, 'update_header');
    });

    it('update_header() should be called after call of init_view()',
      function () {
        var initView = Ctrl.prototype.init_view.bind(Ctrl.prototype);

        initView();
        expect(Ctrl.prototype.update_header.calls.count()).toEqual(1);
      }
    );

    it('update_header() should be called after call of widget_shown()',
      function () {
        var widgetShown = Ctrl.prototype.widget_shown.bind(Ctrl.prototype);

        widgetShown();
        expect(Ctrl.prototype.update_header.calls.count()).toEqual(1);
      }
    );

    it('update_header() should be called after call of add_child_lists()',
      function () {
        var addChildLists = Ctrl.prototype.add_child_lists.bind(Ctrl.prototype);

        addChildLists([]);
        expect(Ctrl.prototype.update_header.calls.count()).toEqual(1);
      }
    );
  });

  describe('buildSubTreeCountMap() method', function () {
    var originalOrder = ['Control', 'Vendor', 'Assessment', 'Audit'];
    var relevant = {
      type: 'Audit',
      id: '555',
      operation: 'relevant'
    };
    var limit = 20;
    var method;

    beforeEach(function () {
      Ctrl.prototype.options = new can.Map({
        model: {shortName: 'foo'}
      });

      method = Ctrl.prototype.buildSubTreeCountMap.bind(Ctrl.prototype);
    });

    function setUpMakeRequestSpy(controls, vendors, assessments, audits) {
      var serverResponse = [
        {Control: {total: controls}},
        {Vendor: {total: vendors}},
        {Assessment: {total: assessments}},
        {Audit: {total: audits}}
      ];

      spyOn(GGRC.Utils.QueryAPI, 'makeRequest')
        .and.returnValue(new can.Deferred().resolve(serverResponse));
    }

    it('buildSubTreeCountMap should not shrink array of counts',
      function (done) {
        var dfd;

        setUpMakeRequestSpy(5, 3, 10, 2);

        dfd = method(originalOrder, relevant, limit);

        setTimeout(function () {
          dfd.then(function (countMap) {
            expect(countMap.length).toEqual(originalOrder.length);

            // check first
            expect(countMap[0].type).toEqual('Control');
            expect(countMap[0].count).toEqual(5);

            // check last
            expect(countMap[3].type).toEqual('Audit');
            expect(countMap[3].count).toEqual(2);
            done();
          });
        }, 1);
      }
    );

    it('buildSubTreeCountMap should not return types with 0 total',
      function (done) {
        var dfd;

        setUpMakeRequestSpy(5, 0, 10, 0);

        // Vendor and Audit don't contain elements.
        // Do not return Vendor and Audit.
        dfd = method(originalOrder, relevant, limit);

        setTimeout(function () {
          dfd.then(function (countMap) {
            expect(countMap.length).toEqual(2);

            // check first
            expect(countMap[0].type).toEqual('Control');
            expect(countMap[0].count).toEqual(5);

            // check last
            expect(countMap[1].type).toEqual('Assessment');
            expect(countMap[1].count).toEqual(10);
            done();
          });
        }, 1);
      }
    );

    it('buildSubTreeCountMap should shrink total of last element',
      function (done) {
        var dfd;

        setUpMakeRequestSpy(5, 4, 10, 33);

        // Shrink total of 'Audit'
        dfd = method(originalOrder, relevant, limit);

        setTimeout(function () {
          dfd.then(function (countMap) {
            expect(countMap.length).toEqual(originalOrder.length);

            // check first
            expect(countMap[0].type).toEqual('Control');
            expect(countMap[0].count).toEqual(5);

            // check last
            expect(countMap[3].type).toEqual('Audit');
            expect(countMap[3].count).toEqual(1);
            done();
          });
        }, 1);
      }
    );

    it('buildSubTreeCountMap should shrink "originalOrder" array',
      function (done) {
        var dfd;

        setUpMakeRequestSpy(5, 12, 10, 33);

        // First 3 types contain more than 20 element.
        // Do not save 'Audit' type.
        // Shrink total of 'Assessment'
        dfd = method(originalOrder, relevant, limit);

        setTimeout(function () {
          dfd.then(function (countMap) {
            expect(countMap.length).toEqual(3);

            // check first
            expect(countMap[0].type).toEqual('Control');
            expect(countMap[0].count).toEqual(5);

            // check last
            expect(countMap[2].type).toEqual('Assessment');
            expect(countMap[2].count).toEqual(3);
            done();
          });
        }, 1);
      }
    );
  });
});
