/*!
    Copyright (C) 2017 Google Inc.
    Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

can.Model('GGRC.Models.Search', {

  findOne: 'GET /search',
  init: function () {
    var _findOne;
    if (this._super) {
      this._super.apply(this, arguments);
    }
    _findOne = this.findOne;

    this.findOne = function () {
      return _findOne.apply(this, arguments).then(function (data) {
        if (data.results.entries) {
          data.attr('entries', data.results.entries);
        }
        if (data.results.counts) {
          data.attr('counts', data.results.counts);
        }
        data.removeAttr('results');
        return data;
      });
    };
  },
  search: function (str, params) {
    return this.findOne($.extend({
      q: this._escapeBackslash(str)
    }, params));
  },
  search_for_types: function (str, types, params) {
    var result;
    if ((!str || str.trim().length === 0) && (!params || params.length === 0)) {
      // Empty search, so actually hit normal endpoints instead of search
      // This returns a search instance which will search across all given types.
      result = this.load_via_model_endpoints(types);
    } else {
      // This returns a Search instance, NOT a model instance.
      result = this.findOne($.extend({
        q: this._escapeBackslash(str),
        types: types.join(',')
      }, params));
    }
    return result;
  },
  counts: function (str, params) {
    return this.findOne($.extend({
      q: this._escapeBackslash(str),
      counts_only: true
    }, params));
  },
  counts_for_types: function (str, types, params, extra_columns) {
    return this.findOne(
      $.extend({
        q: this._escapeBackslash(str),
        types: types.join(','),
        counts_only: true,
        extra_columns: extra_columns && extra_columns.join(',')
      }, params));
  },
  load_via_model_endpoints: function (types) {
    var dfds;

    dfds = can.map(types, function (model_name) {
      // FIXME: This should use __stubs_only=true when paging is used
      return CMS.Models[model_name].findAll({
        __stubs_only: true,
        __sort: 'title,email'
      });
    });

    return $.when.apply($, dfds).then(function () {
      var model_results = can.makeArray(arguments);
      var search_response = {
        entries: {},
        selfLink: 'Fake'
      };
      // Mock the search resource format
      can.each(types, function (model_name, index) {
        search_response.entries[model_name] = model_results[index];
      });

      return new GGRC.Models.Search(search_response);
    });
  },
  _escapeBackslash: function (str) {
    return str.replace(/\\/g, '\\\\');
  }
}, {
  getResultsFor: function (type) {
    var _class = type.shortName ? type :
      (can.getObject('CMS.Models.' + type) ||
        can.getObject('GGRC.Models.' + type));

    type = _class.shortName;
    return can.map(this.entries, function (v) {
      var inst;
      if (v.type === type) {
        inst = new _class({id: v.id});
        return inst;
      }
    });
  },
  getResultsForType: function (model_name) {
    var model = CMS.Models[model_name];
    var entries;

    if (!(this.entries instanceof Array ||
      this.entries instanceof can.Observe.List)) {
      entries = this.entries[model_name] || [];
    } else {
      entries = can.map(this.entries, function (v) {
        if (v.type === model_name) {
          return v;
        }
      });
    }

    return can.map(entries, function (stub) {
      return CMS.Models.get_instance(model.shortName, stub.id);
    });
  },
  getCountFor: function (type) {
    var result;

    if (type && type.shortName) {
      type = type.shortName;
    }
    if (!this.counts[type]) {
      result = 0;
    } else {
      result = this.counts[type];
    }
    return result;
  }
});
