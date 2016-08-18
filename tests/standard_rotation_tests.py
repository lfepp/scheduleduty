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
    './expected_results/standard_rotation_expected.json'
)
input_filename = os.path.join(
    os.path.dirname(__file__),
    './input/standard_rotation_input.json'
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
standard_rotation = scheduleduty.StandardRotationLogic(
    config['start_date'],
    config['end_date']
)


class StandardRotationTests(unittest.TestCase):

    def get_restriction_type(self):
        expected_result = expected['get_restriction_type_daily']
        actual_result = standard_rotation.get_restriction_type(
            input['get_restriction_type_daily']['restriction_start_day'],
            input['get_restriction_type_daily']['restriction_end_day']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_restriction_type_weekly']
        actual_result = standard_rotation.get_restriction_type(
            input['get_restriction_type_weekly']['restriction_start_day'],
            input['get_restriction_type_weekly']['restriction_end_day']
        )
        self.assertEqual(expected_result, actual_result)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(StandardRotationTests('get_restriction_type'))
    return suite
