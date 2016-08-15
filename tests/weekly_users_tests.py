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
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
expected_filename = os.path.join(
    os.path.dirname(__file__),
    './expected_results/weekly_users_expected.json'
)
input_filename = os.path.join(
    os.path.dirname(__file__),
    './input/weekly_users_input.json'
)
config_filname = os.path.join(os.path.dirname(__file__), './config.json')

import import_schedules  # NOQA

with open(expected_filename) as expected_file:
    expected = json.load(expected_file)

with open(input_filename) as input_file:
    input = json.load(input_file)

with open(config_filname) as config_file:
    config = json.load(config_file)

pd_rest = import_schedules.PagerDutyREST(config['api_key'])
weekly_users = import_schedules.WeeklyUserLogic(
    config['base_name'],
    config['level_name'],
    config['multi_name'],
    config['start_date']
)


class WeeklyUserTests(unittest.TestCase):

    def create_days_of_week(self):
        expected_result = expected['create_days_of_week']
        actual_result = weekly_users.create_days_of_week(
         "tests/csv/weekly_users_test.csv"
        )
        self.assertEqual(expected_result, actual_result)

    def split_teams_into_users(self):
        expected_result = expected['split_teams_into_users']
        actual_result = weekly_users.split_teams_into_users(
         pd_rest,
         input['split_teams_into_users']
        )
        self.assertEqual(expected_result, actual_result)

    def get_user_ids(self):
        expected_result = expected['get_user_ids']
        actual_result = weekly_users.get_user_ids(
         pd_rest,
         input['get_user_ids']
        )
        self.assertEqual(expected_result, actual_result)

    def split_days_by_level(self):
        expected_result = expected['split_days_by_level']
        actual_result = weekly_users.split_days_by_level(
         input['split_days_by_level']
        )
        self.assertEqual(expected_result, actual_result)

    def get_time_periods(self):
        expected_result = expected['get_time_periods']
        actual_result = weekly_users.get_time_periods(
         expected['split_days_by_level']
        )
        self.assertEqual(expected_result, actual_result)

    def check_for_overlap(self):
        expected_result = expected['check_for_overlap']
        actual_result = weekly_users.check_for_overlap(
         expected['get_time_periods']
        )
        self.assertEqual(expected_result, actual_result)

    def concatenate_time_periods(self):
        expected_result = expected['concatenate_time_periods']
        actual_result = weekly_users.concatenate_time_periods(
         input['concatenate_time_periods']
        )
        self.assertEqual(expected_result, actual_result)

    def get_schedule_payload(self):
        expected_result = expected['get_schedule_payload']
        actual_result = weekly_users.get_schedule_payload(
         input['get_schedule_payload']
        )
        self.assertEqual(expected_result, actual_result)

    def get_escalation_policy_payload(self):
        expected_result = expected['get_escalation_policy_payload']
        actual_result = weekly_users.get_escalation_policy_payload(
         input['get_escalation_policy_payload']['ep_by_level']
        )
        self.assertEqual(expected_result, actual_result)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(WeeklyUserTests('create_days_of_week'))
    suite.addTest(WeeklyUserTests('split_teams_into_users'))
    suite.addTest(WeeklyUserTests('get_user_ids'))
    suite.addTest(WeeklyUserTests('split_days_by_level'))
    suite.addTest(WeeklyUserTests('get_time_periods'))
    suite.addTest(WeeklyUserTests('check_for_overlap'))
    suite.addTest(WeeklyUserTests('concatenate_time_periods'))
    suite.addTest(WeeklyUserTests('get_schedule_payload'))
    suite.addTest(WeeklyUserTests('get_escalation_policy_payload'))
    return suite
