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
import json
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../scheduleduty'))
expected_filename = os.path.join(
    os.path.dirname(__file__),
    './expected_results/weekly_shifts_expected.json'
)
input_filename = os.path.join(
    os.path.dirname(__file__),
    './input/weekly_shifts_input.json'
)
config_filname = os.path.join(os.path.dirname(__file__), './config.json')

import scheduleduty  # NOQA

with open(expected_filename) as expected_file:
    expected = json.load(expected_file)

with open(input_filename) as input_file:
    input = json.load(input_file)

with open(config_filname) as config_file:
    config = json.load(config_file)

pd_rest = scheduleduty.PagerDutyREST(config['api_key'])
weekly_shifts = scheduleduty.WeeklyShiftLogic(
    config['base_name'],
    config['level_name'],
    config['multi_name'],
    config['start_date'],
    config['end_date'],
    config['time_zone'],
    config['num_loops'],
    config['escalation_delay']
)


class WeeklyShiftsTests(unittest.TestCase):

    def create_days_of_week(self):
        expected_result = expected['create_days_of_week']
        actual_result = weekly_shifts.create_days_of_week(
         'tests/csv/weekly_shifts_test.csv'
        )
        self.assertEqual(expected_result, actual_result)

    def split_teams_into_users(self):
        expected_result = expected['split_teams_into_users']
        actual_result = weekly_shifts.split_teams_into_users(
         pd_rest,
         input['split_teams_into_users']
        )
        self.assertEqual(expected_result, actual_result)

    def get_user_ids(self):
        expected_result = expected['get_user_ids']
        actual_result = weekly_shifts.get_user_ids(
         pd_rest,
         input['get_user_ids']
        )
        self.assertEqual(expected_result, actual_result)

    def split_days_by_level(self):
        expected_result = expected['split_days_by_level']
        actual_result = weekly_shifts.split_days_by_level(
         input['split_days_by_level']
        )
        self.assertEqual(expected_result, actual_result)

    def get_time_periods(self):
        expected_result = expected['get_time_periods']
        actual_result = weekly_shifts.get_time_periods(
         expected['split_days_by_level']
        )
        self.assertEqual(expected_result, actual_result)

    def check_for_overlap(self):
        expected_result = expected['check_for_overlap']
        actual_result = weekly_shifts.check_for_overlap(
         expected['get_time_periods']
        )
        self.assertEqual(expected_result, actual_result)

    def concatenate_time_periods(self):
        expected_result = expected['concatenate_time_periods']
        actual_result = weekly_shifts.concatenate_time_periods(
         input['concatenate_time_periods']
        )
        self.assertEqual(expected_result, actual_result)

    def get_schedule_payload(self):
        expected_result = expected['get_schedule_payload']
        actual_result = weekly_shifts.get_schedule_payload(
         input['get_schedule_payload']
        )
        self.assertEqual(expected_result, actual_result)

    def get_escalation_policy_payload(self):
        expected_result = expected['get_escalation_policy_payload']
        actual_result = weekly_shifts.get_escalation_policy_payload(
         input['get_escalation_policy_payload']['ep_by_level']
        )
        self.assertEqual(expected_result, actual_result)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(WeeklyShiftsTests('create_days_of_week'))
    suite.addTest(WeeklyShiftsTests('split_teams_into_users'))
    suite.addTest(WeeklyShiftsTests('get_user_ids'))
    suite.addTest(WeeklyShiftsTests('split_days_by_level'))
    suite.addTest(WeeklyShiftsTests('get_time_periods'))
    suite.addTest(WeeklyShiftsTests('check_for_overlap'))
    suite.addTest(WeeklyShiftsTests('concatenate_time_periods'))
    suite.addTest(WeeklyShiftsTests('get_schedule_payload'))
    suite.addTest(WeeklyShiftsTests('get_escalation_policy_payload'))
    return suite
