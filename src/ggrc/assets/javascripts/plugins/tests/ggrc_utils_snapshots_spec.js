/*!
 Copyright (C) 2017 Google Inc.
 Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
 */

describe('GGRC Utils Snapshots', function () {
  describe('isSnapshotType() method', function () {
    var instance;

    beforeEach(function () {
      instance = {
        type: 'Snapshot',
        viewLink: '/snapshots/123'
      };
    });

    it('isSnapshotType() should return true', function () {
      expect(GGRC.Utils.Snapshots.isSnapshotType(instance))
        .toBe(true);
    });

    it('isSnapshotType() should return false', function () {
      instance.type = 'Assessment';
      expect(GGRC.Utils.Snapshots.isSnapshotType(instance))
        .toBe(false);
    });

    it('isSnapshotType() should return false. Pass empty object', function () {
      expect(GGRC.Utils.Snapshots.isSnapshotType({}))
        .toBe(false);
    });
  });

  describe('getSnapshotItemQuery() method', function () {
    it('getSnapshotItemQuery() should return correct expression',
      function () {
        var relevantInstance = {
          type: 'Assessment',
          viewLink: '/assessments/123'
        };
        var childId = 10;
        var childType = 'Control';

        var query = GGRC.Utils.Snapshots
          .getSnapshotItemQuery(relevantInstance, childId, childType);

        var queryData = query.data[0];
        var queryExpression = queryData.filters.expression;
        var objectName = queryData.object_name;
        var rightNodes = queryExpression.right;

        expect(objectName).toEqual('Snapshot');
        expect(queryExpression.left.object_name).toEqual('Assessment');
        expect(rightNodes.left.left).toEqual('child_type');
        expect(rightNodes.left.right).toEqual(childType);
        expect(rightNodes.right.left).toEqual('child_id');
        expect(rightNodes.right.right).toEqual(childId);
      }
    );
  });

  describe('toObject() method', function () {
    var snapshot;
    var toObject;

    beforeAll(function () {
      toObject = GGRC.Utils.Snapshots.toObject;
    });

    beforeEach(function () {
      new CMS.Models.Audit({id: 1});
      snapshot = {
        id: 12345,
        type: 'Snapshot',
        child_id: 42,
        child_type: 'Control',
        parent: {
          id: 1,
          type: 'Audit'
        },
        revision: {
          content: {
            access_control_list: [
              {ac_role_id: 10, person_id: 4},
              {ac_role_id: 17, person_id: 2},
              {ac_role_id: 12, person_id: 4}
            ]
          }
        }
      };
    });

    it('adds person stubs to access control list items', function () {
      var result = toObject(snapshot);

      expect(result.access_control_list).toBeDefined();

      result.access_control_list.forEach(function (item) {
        expect(item.person).toBeDefined();
        expect(item.person.type).toEqual('Person');
        expect(item.person.id).toEqual(item.person_id);
      });
    });

    it('sets original link to snapshot object', function () {
      var result = toObject(snapshot);

      expect(result.attr('originalLink')).toEqual('/controls/42');
    });
  });
});
