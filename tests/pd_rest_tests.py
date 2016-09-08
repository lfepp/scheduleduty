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
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from scheduleduty import scheduleduty  # NOQA

expected_filename = os.path.join(
    os.path.dirname(__file__),
    './expected_results/pd_rest_expected.json'
)
input_filename = os.path.join(
    os.path.dirname(__file__),
    './input/pd_rest_input.json'
)
config_filname = os.path.join(os.path.dirname(__file__), './config.json')

with open(expected_filename) as expected_file:
    expected = json.load(expected_file)

with open(input_filename) as input_file:
    input = json.load(input_file)

with open(config_filname) as config_file:
    config = json.load(config_file)

pd_rest = scheduleduty.PagerDutyREST(config['api_key'])


class PagerDutyRESTTests(unittest.TestCase):

    def get_team_id(self):
        expected_result = 'P9NY9DM'
        actual_result = pd_rest.get_team_id('Import Team')
        self.assertEqual(expected_result, actual_result)

    def get_users_in_team(self):
        expected_result = expected['get_users_in_team']
        actual_result = pd_rest.get_users_in_team('P9NY9DM')
        self.assertEqual(expected_result, actual_result)

    def get_user_id(self):
        expected_result = 'PNBLWIT'
        actual_result = pd_rest.get_user_id('Import User 4')
        self.assertEqual(expected_result, actual_result)

    # TODO: Improve these tests - http://docs.python-guide.org/en/latest/writing/tests/  # NOQA
    def schedules(self):
        # create_schedule test
        expected_result = {}
        actual_result = pd_rest.create_schedule(input['create_schedule'])
        self.assertEqual(type(expected_result), type(actual_result))
        # delete_schedule test
        expected_result = 204
        actual_result = pd_rest.delete_schedule(
            actual_result['schedule']['id']
        )
        self.assertEqual(expected_result, actual_result)

    # TODO: Improve these tests - http://docs.python-guide.org/en/latest/writing/tests/  # NOQA
    def escalation_policies(self):
        # create_escalation_policy test
        expected_result = {}
        actual_result = pd_rest.create_escalation_policy(
            input['create_escalation_policy']
        )
        self.assertEqual(type(expected_result), type(actual_result))
        # delete_escalation_policy test
        expected_result = 204
        actual_result = pd_rest.delete_escalation_policy(
            actual_result['escalation_policy']['id']
        )
        self.assertEqual(expected_result, actual_result)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(PagerDutyRESTTests('get_team_id'))
    suite.addTest(PagerDutyRESTTests('get_users_in_team'))
    suite.addTest(PagerDutyRESTTests('get_user_id'))
    suite.addTest(PagerDutyRESTTests('schedules'))
    suite.addTest(PagerDutyRESTTests('escalation_policies'))
    return suite
