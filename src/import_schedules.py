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

import sys
import csv
import glob


# TODO: Create a WeeklyUserLogic class for extensibility
def create_days_of_week(file):
    """ Parse CSV file into days of week
    """

    sunday_entries = []
    monday_entries = []
    tuesday_entries = []
    wednesday_entries = []
    thursday_entries = []
    friday_entries = []
    saturday_entries = []
    reader = csv.DictReader(open(file), fieldnames=('escalation_level',
                                                    'user_or_team',
                                                    'type',
                                                    'day_of_week',
                                                    'start_time',
                                                    'end_time'))
    reader.next()
    for row in reader:
        entry = {
            'escalation_level': int(row['escalation_level']),
            'id': row['user_or_team'],
            'type': row['type'],
            'start_time': row['start_time'],
            'end_time': row['end_time']
        }
        if row['day_of_week'] == 0 or row['day_of_week'].lower() == 'sunday':
            sunday_entries.append(entry)
        elif row['day_of_week'] == 1 or row['day_of_week'].lower() == 'monday':
            monday_entries.append(entry)
        elif (row['day_of_week'] == 2 or
              row['day_of_week'].lower() == 'tuesday'):
            tuesday_entries.append(entry)
        elif (row['day_of_week'] == 3 or
              row['day_of_week'].lower() == 'wednesday'):
            wednesday_entries.append(entry)
        elif (row['day_of_week'] == 4 or
              row['day_of_week'].lower() == 'thursday'):
            thursday_entries.append(entry)
        elif row['day_of_week'] == 5 or row['day_of_week'].lower() == 'friday':
            friday_entries.append(entry)
        elif (row['day_of_week'] == 6 or
              row['day_of_week'].lower() == 'saturday'):
            saturday_entries.append(entry)
        else:
            print ("Error: Entry {0} does not have a valid day_of_week: {1}"
                   .format(row['user_or_team'], row['day_of_week']))
    # Create days with entries
    sunday = {'day_of_week': 0, 'entries': sunday_entries}
    monday = {'day_of_week': 1, 'entries': monday_entries}
    tuesday = {'day_of_week': 2, 'entries': tuesday_entries}
    wednesday = {'day_of_week': 3, 'entries': wednesday_entries}
    thursday = {'day_of_week': 4, 'entries': thursday_entries}
    friday = {'day_of_week': 5, 'entries': friday_entries}
    saturday = {'day_of_week': 6, 'entries': saturday_entries}
    return [sunday, monday, tuesday, wednesday, thursday, friday, saturday]


def split_days_by_level(base_ep):
    """ Split days in escalation policy by level
    """

    levels = {}
    new_ep = []
    for day in base_ep[0]['schedules'][0]['days']:
        for entry in day['entries']:
            if str(entry['escalation_level']) in levels:
                (levels[str(entry['escalation_level'])]['days']
                 [str(day['day_of_week'])].append(entry))
            else:
                levels[str(entry['escalation_level'])] = ({'days': {'0': [],
                                                          '1': [], '2': [],
                                                          '3': [], '4': [],
                                                          '5': [], '6': []}})
                (levels[str(entry['escalation_level'])]['days']
                 [str(day['day_of_week'])].append(entry))
    for level in levels.keys():
        days = []
        i = 0
        while i <= 6:
            for day in levels[level]['days']:
                if int(day) == i:
                    days.append(levels[level]['days'][day])
                    i += 1
        new_ep.insert(int(level), {
            'schedules': [{
                'name': ("{0}_level_{1}".format(base_ep[0]['schedules'][0]
                         ['name'], level)),
                'days': days
            }]
        })
    return new_ep


def main():
    # Loop through all CSV files
    files = glob.glob('src/csv/*.csv')
    for file in files:
        # TODO: Add logic to handle non-weekly schedules
        days = create_days_of_week(file)
        # Create list of escalation policies by level
        base_ep = [{
            'schedules': [{
                # TODO: Use regex to parse filename
                'name': file[8:len(file) - 4],
                'days': days
            }]
        }]
        ep_by_level = split_days_by_level(base_ep)
    # 3) Check each day for time period overlaps
    # 4) If overlaps, break into new possible schedules on same level
    # 5) Break each day down by time period
    # 6) Loop through consecutive days for patterns
    # 7) Each batch of user/time period/consecutive days becomes a new layer
    # 8) Each possible schedule on each EP level becomes a schedule based on layers in 7
    # 9) EP is created

if __name__ == '__main__':
    sys.exit(main())
