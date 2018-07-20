# Copyright (C) 2018 Google Inc.
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>

"""
pacrs

Create Date: 2018-07-20 09:14:37.002736
"""
# disable Invalid constant name pylint warning for mandatory Alembic variables.
# pylint: disable=invalid-name

import sqlalchemy as sa

from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'fe902e3803aa'
down_revision = 'efcce7bd20c9'


PACRS = {
    (u'AccessGroup', u'Admin'): [
        {
            'delete': False,
            'for_path': 'AccessGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'AccessGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'AccessGroup->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'AccessGroup', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'AccessGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'AccessGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'AccessGroup->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'AccessGroup', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'AccessGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'AccessGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'AccessGroup->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Assessment', u'Assignees'): [
        {
            'delete': False,
            'for_path': 'Assessment<-Audit->Evidence',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Assessment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment<-Audit',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Snapshot',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment<-Audit->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Assessment->Issue',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Snapshot->Snapshot',
            'read': True,
            'update': False
        }
    ],
    (u'Assessment', u'Creators'): [
        {
            'delete': False,
            'for_path': 'Assessment<-Audit->Evidence',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment<-Audit',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Snapshot',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment<-Audit->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Snapshot->Snapshot',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Assessment', u'Verifiers'): [
        {
            'delete': False,
            'for_path': 'Assessment<-Audit->Evidence',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment<-Audit',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Snapshot',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment<-Audit->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Assessment->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Snapshot->Snapshot',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Assessment->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Audit', u'Audit Captains'): [
        {
            'delete': True,
            'for_path': 'Audit->AssessmentTemplate',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Audit->Issue->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Audit->Assessment->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Audit->Issue',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Audit->Assessment',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Audit->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Assessment->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Audit->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Audit->Assessment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Snapshot',
            'read': True,
            'update': True
        }
    ],
    (u'Audit', u'Auditors'): [
        {
            'delete': False,
            'for_path': 'Audit->Assessment->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Issue->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Snapshot',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Audit->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Audit->AssessmentTemplate',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Assessment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Issue',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Audit->Assessment',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Audit->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Audit->Assessment->Evidence',
            'read': True,
            'update': True
        }
    ],
    (u'Clause', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Clause->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Clause->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Clause->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Clause', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Clause->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Clause->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Clause->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Clause', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Clause->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Clause->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Clause->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Contract', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Contract->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Contract->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Contract->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Contract', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Contract->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Contract->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Contract->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Contract', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Contract->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Contract->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Contract->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Control', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Control->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Control->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Control', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Control->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Control->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Control', u'Principal Assignees'): [
        {
            'delete': False,
            'for_path': 'Control->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Control->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Control', u'Secondary Assignees'): [
        {
            'delete': False,
            'for_path': 'Control->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Control->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Control', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Control->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Control->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Control->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'DataAsset', u'Admin'): [
        {
            'delete': False,
            'for_path': 'DataAsset->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'DataAsset->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'DataAsset->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'DataAsset', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'DataAsset->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'DataAsset->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'DataAsset->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'DataAsset', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'DataAsset->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'DataAsset->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'DataAsset->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Document', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Evidence', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Evidence->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Facility', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Facility->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Facility->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Facility->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Facility', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Facility->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Facility->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Facility->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Facility', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Facility->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Facility->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Facility->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Issue', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Issue->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Issue->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Issue', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Issue->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Issue->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Issue', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Issue->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Issue->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Market', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Market->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Market->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Market->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Market', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Market->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Market->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Market->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Market', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Market->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Market->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Market->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Metric', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Metric->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Metric->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Metric->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Metric', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Metric->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Metric->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Metric->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Metric', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Metric->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Metric->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Metric->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Objective', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Objective->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Objective->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Objective->Document',
            'read': True,
            'update': True
        }
    ],
    (u'Objective', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Objective->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Objective->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Objective->Document',
            'read': True,
            'update': True
        }
    ],
    (u'Objective', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Objective->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Objective->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Objective->Document',
            'read': True,
            'update': True
        }
    ],
    (u'OrgGroup', u'Admin'): [
        {
            'delete': False,
            'for_path': 'OrgGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'OrgGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'OrgGroup->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'OrgGroup', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'OrgGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'OrgGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'OrgGroup->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'OrgGroup', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'OrgGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'OrgGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'OrgGroup->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Policy', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Policy->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Policy->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Policy->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Policy', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Policy->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Policy->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Policy->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Policy', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Policy->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Policy->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Policy->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Process', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Process->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Process->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Process->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Process', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Process->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Process->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Process->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Process', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Process->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Process->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Process->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Product', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Product->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Product->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Product->Document',
            'read': True,
            'update': True
        }
    ],
    (u'Product', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Product->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Product->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Product->Document',
            'read': True,
            'update': True
        }
    ],
    (u'Product', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Product->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Product->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Product->Document',
            'read': True,
            'update': True
        }
    ],
    (u'ProductGroup', u'Admin'): [
        {
            'delete': False,
            'for_path': 'ProductGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'ProductGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'ProductGroup->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'ProductGroup', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'ProductGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'ProductGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'ProductGroup->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'ProductGroup', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'ProductGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'ProductGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'ProductGroup->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Program', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Program->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Document',
            'read': True,
            'update': False
        }
    ],
    (u'Program', u'Program Editors'): [
        {
            'delete': False,
            'for_path': 'Program->RiskAssessment->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Policy',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Standard',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Section',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Clause',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Contract->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Process',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->RiskAssessment->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Regulation->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Product->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Section->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Threat->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Process->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Issue',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Objective->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Control',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Standard->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Process->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Facility',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->DataAsset',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Issue->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->System->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Metric->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Control->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Market',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Metric->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Project->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Audit->Issue',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->OrgGroup',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Threat->Document',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->ProductGroup',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Facility->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Process->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Project->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Metric->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Standard->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Vendor->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Vendor->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Contract',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Regulation->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Facility->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Audit',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->System',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Control->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Product->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Threat->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Policy->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Policy->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Market->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Objective',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Metric',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Risk',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->AccessGroup',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Policy->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->RiskAssessment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Threat',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Contract->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->RiskAssessment',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Vendor',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Product',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Market->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Facility->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Objective->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Section->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->System->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Snapshot',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Regulation',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Objective->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Vendor->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->System->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Regulation->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Project->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Section->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Standard->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Contract->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Project',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Audit->AssessmentTemplate',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Control->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Product->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Market->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Control->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->TechnologyEnvironment',
            'read': True,
            'update': True
        }
    ],
    (u'Program', u'Program Managers'): [
        {
            'delete': False,
            'for_path': 'Program->RiskAssessment->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Policy',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Standard',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Section',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Clause',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Contract->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Process',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->RiskAssessment->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Regulation->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Product->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Section->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Threat->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Process->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Issue',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Objective->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Control',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Standard->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Process->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Facility',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->DataAsset',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Issue->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->System->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Metric->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Control->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Market',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Metric->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Project->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Audit->Issue',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->OrgGroup',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Threat->Document',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->ProductGroup',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Facility->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Process->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Project->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Metric->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Standard->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Vendor->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Vendor->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment->Evidence',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Contract',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Regulation->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Facility->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Audit',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->System',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Control->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Product->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Threat->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Policy->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Policy->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Market->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Objective',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Metric',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Risk',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->AccessGroup',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Policy->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->RiskAssessment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Threat',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Contract->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->RiskAssessment',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup->Document',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Vendor',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Product',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Market->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Facility->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Objective->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Section->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->System->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Snapshot',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Regulation',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Objective->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Vendor->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->System->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Regulation->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Project->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Section->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Standard->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Contract->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->Project',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Audit->AssessmentTemplate',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Control->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Product->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Market->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Control->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': True,
            'for_path': 'Program->TechnologyEnvironment',
            'read': True,
            'update': True
        }, {
            'delete': True,
            'for_path': 'Program->Audit->Assessment',
            'read': True,
            'update': True
        }
    ],
    (u'Program', u'Program Readers'): [
        {
            'delete': False,
            'for_path': 'Program->RiskAssessment->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Control',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Policy->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Issue->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Product->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Market',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Section->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Threat->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Process->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->AssessmentTemplate',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Objective->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Market->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Standard->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Process->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Standard',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Control->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Contract',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Issue->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Objective->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Metric->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Vendor->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Snapshot',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Contract->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Project->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Metric->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Project->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Facility',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Section->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Vendor->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Regulation->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Facility->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Product->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Objective',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->RiskAssessment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Control->Proposal',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->DataAsset->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Threat',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Product->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Threat->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Contract->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Vendor',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Product',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Policy->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->ProductGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Regulation->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->RiskAssessment->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Market->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Regulation',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->System',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Policy->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Evidence',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Metric',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Issue->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Contract->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->System->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Project',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Metric->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Market->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Facility->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Objective->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Section->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->AccessGroup->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->System->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Risk',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Threat->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Project->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Process->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Section',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Facility->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->System->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Vendor->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Regulation->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Standard->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Process',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment->Evidence->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->RiskAssessment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Standard->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Assessment->Evidence',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Clause->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Risk->Proposal',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Control->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Control->Document',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Audit->Issue',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->TechnologyEnvironment->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Issue',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->OrgGroup',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Policy',
            'read': True,
            'update': False
        }
    ],
    (u'Program', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Program->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Program->Document',
            'read': True,
            'update': False
        }
    ],
    (u'Project', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Project->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Project->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Project->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Project', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Project->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Project->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Project->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Project', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Project->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Project->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Project->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Regulation', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Regulation->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Regulation->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Regulation->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Regulation', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Regulation->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Regulation->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Regulation->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Regulation', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Regulation->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Regulation->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Regulation->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Risk', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Risk->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Risk->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Risk->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Risk->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Risk', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Risk->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Risk->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Risk->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Risk->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Risk', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Risk->Proposal',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Risk->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Risk->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Risk->Document->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Section', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Section->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Section->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Section->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Section', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Section->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Section->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Section->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Section', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Section->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Section->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Section->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Standard', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Standard->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Standard->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Standard->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Standard', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Standard->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Standard->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Standard->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Standard', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Standard->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Standard->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'Standard->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'System', u'Admin'): [
        {
            'delete': False,
            'for_path': 'System->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'System->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'System->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'System', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'System->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'System->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'System->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'System', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'System->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'System->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'System->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'TechnologyEnvironment', u'Admin'): [
        {
            'delete': False,
            'for_path': 'TechnologyEnvironment->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'TechnologyEnvironment->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'TechnologyEnvironment->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'TechnologyEnvironment', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'TechnologyEnvironment->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'TechnologyEnvironment->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'TechnologyEnvironment->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'TechnologyEnvironment', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'TechnologyEnvironment->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'TechnologyEnvironment->Document',
            'read': True,
            'update': True
        }, {
            'delete': False,
            'for_path': 'TechnologyEnvironment->Comment',
            'read': True,
            'update': False
        }
    ],
    (u'Threat', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Threat->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Threat->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Threat->Document',
            'read': True,
            'update': True
        }
    ],
    (u'Threat', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Threat->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Threat->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Threat->Document',
            'read': True,
            'update': True
        }
    ],
    (u'Threat', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Threat->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Threat->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Threat->Document',
            'read': True,
            'update': True
        }
    ],
    (u'Vendor', u'Admin'): [
        {
            'delete': False,
            'for_path': 'Vendor->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Vendor->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Vendor->Document',
            'read': True,
            'update': True
        }
    ],
    (u'Vendor', u'Primary Contacts'): [
        {
            'delete': False,
            'for_path': 'Vendor->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Vendor->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Vendor->Document',
            'read': True,
            'update': True
        }
    ],
    (u'Vendor', u'Secondary Contacts'): [
        {
            'delete': False,
            'for_path': 'Vendor->Document->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Vendor->Comment',
            'read': True,
            'update': False
        }, {
            'delete': False,
            'for_path': 'Vendor->Document',
            'read': True,
            'update': True
        }
    ]
}


def upgrade():
    """Upgrade database schema and/or data, creating a new revision."""
    connection = op.get_bind()
    meta = sa.MetaData(bind=connection)
    access_control_roles = sa.Table('access_control_roles', meta, autoload=True)
    propagated_access_control_roles = sa.Table(
        'propagated_access_control_roles',
        meta,
        autoload=True)
    ac_roles = sa.select([
        access_control_roles.c.object_type,
        access_control_roles.c.name,
        access_control_roles.c.id,
    ]).where(access_control_roles.c.parent_id.is_(None))
    ac_roles_dict = {(t, n): i for t, n, i in connection.execute(ac_roles)}
    for key, p_acrs in PACRS.iteritems():
      if key not in ac_roles_dict:
        continue
      res = []
      for p_acr in p_acrs:
        p_acr["parent_id"] = ac_roles_dict[key]
        res.append(p_acr)
      connection.execute(
        propagated_access_control_roles.insert(),
        res
      )


def downgrade():
    """Downgrade database schema and/or data back to the previous revision."""
    return
