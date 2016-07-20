#!/usr/bin/env python
#
# Copyright (c) 2016, PagerDuty, Inc. <info@pagerduty.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of PagerDuty Inc nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL PAGERDUTY INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

import import_schedules

create_days_of_week_expected = [
    {
        'day_of_week': 0,
        'entries': [
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 2',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 3',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '18:30',
                'end_time': '24:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '18:30',
                'end_time': '24:00'
            }
        ]
    },
    {
        'day_of_week': 1,
        'entries': [
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 2',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 3',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '18:30',
                'end_time': '24:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '18:30',
                'end_time': '24:00'
            }
        ]
    },
    {
        'day_of_week': 2,
        'entries': [
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 2',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 3',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '18:30',
                'end_time': '24:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '18:30',
                'end_time': '24:00'
            }
        ]
    },
    {
        'day_of_week': 3,
        'entries': [
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 2',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 3',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '18:30',
                'end_time': '24:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '18:30',
                'end_time': '24:00'
            }
        ]
    },
    {
        'day_of_week': 4,
        'entries': [
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 2',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 3',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '18:30',
                'end_time': '24:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '18:30',
                'end_time': '24:00'
            }
        ]
    },
    {
        'day_of_week': 5,
        'entries': [
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 2',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 3',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '18:30',
                'end_time': '24:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '18:30',
                'end_time': '24:00'
            }
        ]
    },
    {
        'day_of_week': 6,
        'entries': [
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '0:00',
                'end_time': '9:00'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 2',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
              'escalation_level': 1,
              'id': 'Import User 3',
              'type': 'User',
              'start_time': '9:00',
              'end_time': '18:30'
            },
            {
                'escalation_level': 1,
                'id': 'Import Team',
                'type': 'Team',
                'start_time': '18:30',
                'end_time': '24:00'
            },
            {
                'escalation_level': 2,
                'id': 'Import User 1',
                'type': 'User',
                'start_time': '18:30',
                'end_time': '24:00'
            }
        ]
    }
]

split_days_by_level_input = [{
    'schedules': [{
        'name': 'weekly_users_test',
        'days': create_days_of_week_expected
    }]
}]

split_days_by_level_expected = [
  {
    "schedules": [
      {
        "name": "weekly_users_test_level_1",
        "days": [
          [
            {
              "type": "Team",
              "start_time": "0:00",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 2",
              "end_time": "18:30"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 3",
              "end_time": "18:30"
            },
            {
              "type": "Team",
              "start_time": "18:30",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "Team",
              "start_time": "0:00",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 2",
              "end_time": "18:30"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 3",
              "end_time": "18:30"
            },
            {
              "type": "Team",
              "start_time": "18:30",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "Team",
              "start_time": "0:00",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 2",
              "end_time": "18:30"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 3",
              "end_time": "18:30"
            },
            {
              "type": "Team",
              "start_time": "18:30",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "Team",
              "start_time": "0:00",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 2",
              "end_time": "18:30"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 3",
              "end_time": "18:30"
            },
            {
              "type": "Team",
              "start_time": "18:30",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "Team",
              "start_time": "0:00",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 2",
              "end_time": "18:30"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 3",
              "end_time": "18:30"
            },
            {
              "type": "Team",
              "start_time": "18:30",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "Team",
              "start_time": "0:00",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 2",
              "end_time": "18:30"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 3",
              "end_time": "18:30"
            },
            {
              "type": "Team",
              "start_time": "18:30",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "Team",
              "start_time": "0:00",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 2",
              "end_time": "18:30"
            },
            {
              "type": "User",
              "start_time": "9:00",
              "escalation_level": 1,
              "id": "Import User 3",
              "end_time": "18:30"
            },
            {
              "type": "Team",
              "start_time": "18:30",
              "escalation_level": 1,
              "id": "Import Team",
              "end_time": "24:00"
            }
          ]
        ]
      }
    ]
  },
  {
    "schedules": [
      {
        "name": "weekly_users_test_level_2",
        "days": [
          [
            {
              "type": "User",
              "start_time": "0:00",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "18:30",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "User",
              "start_time": "0:00",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "18:30",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "User",
              "start_time": "0:00",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "18:30",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "User",
              "start_time": "0:00",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "18:30",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "User",
              "start_time": "0:00",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "18:30",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "User",
              "start_time": "0:00",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "18:30",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "24:00"
            }
          ],
          [
            {
              "type": "User",
              "start_time": "0:00",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "9:00"
            },
            {
              "type": "User",
              "start_time": "18:30",
              "escalation_level": 2,
              "id": "Import User 1",
              "end_time": "24:00"
            }
          ]
        ]
      }
    ]
  }
]


class WeeklyUserTests(unittest.TestCase):

    def create_days_of_week(self):
        expected_result = create_days_of_week_expected
        actual_result = import_schedules.create_days_of_week(
         "tests/csv/weekly_users_test.csv")
        self.assertEqual(expected_result, actual_result)

    def split_days_by_level(self):
        expected_result = split_days_by_level_expected
        actual_result = import_schedules.split_days_by_level(
         split_days_by_level_input)
        self.assertEqual(expected_result, actual_result)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(WeeklyUserTests('create_days_of_week'))
    suite.addTest(WeeklyUserTests('split_days_by_level'))
    return suite
