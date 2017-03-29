/*!
  Copyright (C) 2017 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

describe('CMS.Models.Assessment', function () {
  'use strict';

  describe('before_create() method', function () {
    var assessment;
    var audit;
    var auditWithoutContext;
    var context;
    var program;

    beforeEach(function () {
      assessment = new CMS.Models.Assessment();
      context = new CMS.Models.Context({id: 42});
      program = new CMS.Models.Program({id: 54});
      audit = new CMS.Models.Audit({context: context, program: program});
      auditWithoutContext = new CMS.Models.Audit({program: program});
    });

    it('sets the program and context properties', function () {
      assessment.attr('audit', audit);
      assessment.before_create();
      expect(assessment.context.id).toEqual(context.id);
    });

    it('throws an error if audit is not defined', function () {
      expect(function () {
        assessment.before_create();
      }).toThrow(new Error('Cannot save assessment, audit not set.'));
    });

    it('throws an error if audit program/context are not defined', function () {
      assessment.attr('audit', auditWithoutContext);
      expect(function () {
        assessment.before_create();
      }).toThrow(new Error(
        'Cannot save assessment, audit context not set.'));
    });
  });

  describe('get_related_objects_as_source() method', function () {
    var assessment;
    var relatedObjectsAsSource;
    var responseSnapshotTitle = 'SnapshotTitle';
    var responseSnapshotUrl = '/someTypeS/123';

    beforeEach(function () {
      var snapshotResponse = [
        {
          Snapshot: {
            values: [
              {
                type: 'Snapshot',
                child_id: 123
              }
            ]
          }
        }
      ];

      assessment = new CMS.Models.Assessment();

      relatedObjectsAsSource = new can.List([
        {
          instance: {
            type: 'Audit',
            id: 5
          }
        },
        {
          instance: {
            type: 'Snapshot',
            id: 123
          }
        }
      ]);

      // stubs
      assessment.get_binding = function () {
        return assessment;
      };

      assessment.refresh_instances = function () {
        return can.Deferred().resolve(relatedObjectsAsSource);
      };

      // spyon
      spyOn(GGRC.Utils.QueryAPI, 'makeRequest').and.returnValue(
        can.Deferred().resolve(snapshotResponse)
      );

      spyOn(GGRC.Utils.Snapshots, 'toObject').and.returnValue(
        {
          title: responseSnapshotTitle,
          originalLink: responseSnapshotUrl
        }
      );
    });

    it('get_related_objects_as_source() should update snapshot objcets',
      function (done) {
        var dfd = assessment.get_related_objects_as_source();
        var snapshotItem = relatedObjectsAsSource[1].instance;

        dfd.done(function () {
          // should be called only once because list has only one snapshot
          expect(GGRC.Utils.QueryAPI.makeRequest.calls.count()).toEqual(1);
          expect(GGRC.Utils.Snapshots.toObject.calls.count()).toEqual(1);

          expect(snapshotItem.attr('title')).toEqual(responseSnapshotTitle);
          expect(snapshotItem.attr('viewLink')).toEqual(responseSnapshotUrl);
          done();
        });
      }
    );
  });
});
