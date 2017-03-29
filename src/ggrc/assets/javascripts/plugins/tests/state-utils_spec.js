/*!
  Copyright (C) 2017 Google Inc.
  Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
*/

'use strict';

describe('GGRC.Utils.State', function () {
  describe('statusFilter() method', function () {
    it('statusFilter() should return filter with all statuses',
      function () {
        var statuses = [
          'Draft', 'Active', 'Deprecated'
        ];

        var statesFilter = GGRC.Utils.State
          .statusFilter(statuses, '');

        expect(statesFilter.indexOf('Status="Active"') > -1)
          .toBe(true);
        expect(statesFilter.indexOf('Status="Draft"') > -1)
          .toBe(true);
        expect(statesFilter.indexOf('Status="Deprecated"') > -1)
          .toBe(true);
      }
    );

    it('statesFilter should not update Assessmnet statuses',
      function () {
        var statuses = [
          'Not Started', 'In Progress', 'Ready for Review'
        ];

        var statesFilter = GGRC.Utils.State
          .statusFilter(statuses, '', 'Assessment');

        expect(statesFilter.indexOf('Status="Not Started"') > -1)
          .toBe(true);
        expect(statesFilter.indexOf('Status="In Progress"') > -1)
          .toBe(true);
        expect(statesFilter.indexOf('Status="Ready for Review"') > -1)
          .toBe(true);
        expect(statesFilter.indexOf('Status="verified="') > -1)
          .toBe(false);
      }
    );

    it('statesFilter should have "Completed" status and "verified=true"',
      function () {
        var statuses = [
          'Ready for Review', 'Completed and Verified'
        ];

        var statesFilter = GGRC.Utils.State
          .statusFilter(statuses, '', 'Assessment');

        expect(statesFilter.indexOf('Status="Ready for Review"') > -1)
          .toBe(true);
        expect(statesFilter.indexOf('Status="Completed"') > -1)
          .toBe(true);
        expect(statesFilter.indexOf('Status="Completed and Verified"') > -1)
          .toBe(false);

        expect(statesFilter.indexOf('verified=true') > -1)
          .toBe(true);
      }
    );

    it('statesFilter should have "Completed" status and "verified=false"',
      function () {
        var statuses = [
          'Ready for Review', 'Completed (no verification)'
        ];

        var statesFilter = GGRC.Utils.State
          .statusFilter(statuses, '', 'Assessment');

        expect(statesFilter.indexOf('Status="Ready for Review"') > -1)
          .toBe(true);
        expect(statesFilter.indexOf('Status="Completed"') > -1)
          .toBe(true);
        expect(statesFilter
          .indexOf('Status="Completed (no verification)"') > -1)
          .toBe(false);

        expect(statesFilter.indexOf('verified=false') > -1)
          .toBe(true);
      }
    );

    it('statesFilter should have "Completed" status',
      function () {
        var statuses = [
          'In Progress', 'Completed (no verification)',
          'Completed and Verified'
        ];

        var statesFilter = GGRC.Utils.State
          .statusFilter(statuses, '', 'Assessment');

        expect(statesFilter.indexOf('Status="In Progress"') > -1)
          .toBe(true);
        expect(statesFilter.indexOf('Status="Completed"') > -1)
          .toBe(true);

        expect(statesFilter
          .indexOf('Status="Completed (no verification)"') > -1)
          .toBe(false);
        expect(statesFilter
          .indexOf('Status="Completed and Verified"') > -1)
          .toBe(false);

        expect(statesFilter.indexOf('verified=') > -1)
          .toBe(false);
      }
    );
  });
});
