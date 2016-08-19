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
        expected_result = expected['get_restriction_type']['daily']
        actual_result = standard_rotation.get_restriction_type(
            input['get_restriction_type']['daily']['restriction_start_day'],
            input['get_restriction_type']['daily']['restriction_end_day']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_restriction_type']['weekly']
        actual_result = standard_rotation.get_restriction_type(
            input['get_restriction_type']['weekly']['restriction_start_day'],
            input['get_restriction_type']['weekly']['restriction_end_day']
        )
        self.assertEqual(expected_result, actual_result)
        with self.assertRaises(ValueError):
            standard_rotation.get_restriction_type(
                input['get_restriction_type']['error']
                ['restriction_start_day'],
                input['get_restriction_type']['error']['restriction_end_day']
            )

    def get_rotation_turn_length(self):
        expected_result = expected['get_rotation_turn_length']['daily']
        actual_result = standard_rotation.get_rotation_turn_length(
            input['get_rotation_turn_length']['daily']['rotation_type'],
            input['get_rotation_turn_length']['daily']['shift_length'],
            input['get_rotation_turn_length']['daily']['shift_type']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_rotation_turn_length']['weekly']
        actual_result = standard_rotation.get_rotation_turn_length(
            input['get_rotation_turn_length']['weekly']['rotation_type'],
            input['get_rotation_turn_length']['weekly']['shift_length'],
            input['get_rotation_turn_length']['weekly']['shift_type']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_rotation_turn_length']['custom_hours']
        actual_result = standard_rotation.get_rotation_turn_length(
            input['get_rotation_turn_length']['custom_hours']['rotation_type'],
            input['get_rotation_turn_length']['custom_hours']['shift_length'],
            input['get_rotation_turn_length']['custom_hours']['shift_type']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_rotation_turn_length']['custom_days']
        actual_result = standard_rotation.get_rotation_turn_length(
            input['get_rotation_turn_length']['custom_days']['rotation_type'],
            input['get_rotation_turn_length']['custom_days']['shift_length'],
            input['get_rotation_turn_length']['custom_days']['shift_type']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_rotation_turn_length']['custom_weeks']
        actual_result = standard_rotation.get_rotation_turn_length(
            input['get_rotation_turn_length']['custom_weeks']['rotation_type'],
            input['get_rotation_turn_length']['custom_weeks']['shift_length'],
            input['get_rotation_turn_length']['custom_weeks']['shift_type']
        )
        self.assertEqual(expected_result, actual_result)
        with self.assertRaises(ValueError):
            standard_rotation.get_rotation_turn_length(
                input['get_rotation_turn_length']['error1']['rotation_type'],
                input['get_rotation_turn_length']['error1']['shift_length'],
                input['get_rotation_turn_length']['error1']['shift_type']
            )
        with self.assertRaises(ValueError):
            standard_rotation.get_rotation_turn_length(
                input['get_rotation_turn_length']['error2']['rotation_type'],
                input['get_rotation_turn_length']['error2']['shift_length'],
                input['get_rotation_turn_length']['error2']['shift_type']
            )

    def get_virtual_start(self):
        expected_result = expected['get_virtual_start']['daily']
        actual_result = standard_rotation.get_virtual_start(
            input['get_virtual_start']['daily']['rotation_type'],
            input['get_virtual_start']['daily']['handoff_day'],
            input['get_virtual_start']['daily']['handoff_time'],
            input['get_virtual_start']['daily']['start_date'],
            input['get_virtual_start']['daily']['time_zone']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_virtual_start']['weekly']
        actual_result = standard_rotation.get_virtual_start(
            input['get_virtual_start']['weekly']['rotation_type'],
            input['get_virtual_start']['weekly']['handoff_day'],
            input['get_virtual_start']['weekly']['handoff_time'],
            input['get_virtual_start']['weekly']['start_date'],
            input['get_virtual_start']['weekly']['time_zone']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_virtual_start']['custom1']
        actual_result = standard_rotation.get_virtual_start(
            input['get_virtual_start']['custom1']['rotation_type'],
            input['get_virtual_start']['custom1']['handoff_day'],
            input['get_virtual_start']['custom1']['handoff_time'],
            input['get_virtual_start']['custom1']['start_date'],
            input['get_virtual_start']['custom1']['time_zone']
        )
        self.assertEqual(expected_result, actual_result)
        expected_result = expected['get_virtual_start']['custom2']
        actual_result = standard_rotation.get_virtual_start(
            input['get_virtual_start']['custom2']['rotation_type'],
            input['get_virtual_start']['custom2']['handoff_day'],
            input['get_virtual_start']['custom2']['handoff_time'],
            input['get_virtual_start']['custom2']['start_date'],
            input['get_virtual_start']['custom2']['time_zone']
        )
        self.assertEqual(expected_result, actual_result)
        with self.assertRaises(ValueError):
            standard_rotation.get_virtual_start(
                input['get_virtual_start']['error1']['rotation_type'],
                input['get_virtual_start']['error1']['handoff_day'],
                input['get_virtual_start']['error1']['handoff_time'],
                input['get_virtual_start']['error1']['start_date'],
                input['get_virtual_start']['error1']['time_zone']
            )
        with self.assertRaises(ValueError):
            standard_rotation.get_virtual_start(
                input['get_virtual_start']['error2']['rotation_type'],
                input['get_virtual_start']['error2']['handoff_day'],
                input['get_virtual_start']['error2']['handoff_time'],
                input['get_virtual_start']['error2']['start_date'],
                input['get_virtual_start']['error2']['time_zone']
            )


def suite():
    suite = unittest.TestSuite()
    suite.addTest(StandardRotationTests('get_restriction_type'))
    suite.addTest(StandardRotationTests('get_rotation_turn_length'))
    suite.addTest(StandardRotationTests('get_virtual_start'))
    return suite
