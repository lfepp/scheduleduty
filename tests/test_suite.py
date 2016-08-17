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

import glob
import unittest
import argparse


def test_suite(include_rest):
    suite = unittest.TestSuite()
    files = glob.glob('tests/*_tests.py')
    if include_rest:
        for file in files:
            # Load suite() function from module
            module = __import__(file[6:-3])
            suite.addTest(module.suite())
    else:
        for file in files:
            # Load suite() function from module except for PagerDutyREST tests
            if file[6:-3] != 'pd_rest_tests':
                module = __import__(file[6:-3])
                suite.addTest(module.suite())

    unittest.TextTestRunner().run(suite)

# Add command line argument to include REST API tests
parser = argparse.ArgumentParser(description='ScheduleDuty Tests')
parser.add_argument(
    '--include-rest',
    help='Flag to include the PagerDutyREST tests in the test suite',
    dest='include_rest',
    action='store_true'
)
parser.set_defaults(include_rest=False)
args = parser.parse_args()

# Load test suite with arguments
test_suite(args.include_rest)
