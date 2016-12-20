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

import csv
import glob
import requests
import json
from datetime import datetime, timedelta, date
import pytz
import time
import argparse
import os


# PD REST API FUNCTION #######################################################
class PagerDutyREST():
    """Class to house all PagerDuty REST API call methods"""

    def __init__(self, api_key):
        self.base_url = 'https://api.pagerduty.com'
        self.headers = {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Content-type': 'application/json',
            'Authorization': 'Token token={token}'.format(token=api_key)
        }

    def get_team_id(self, team_name):
        """GET the team ID from team name"""

        url = '{base_url}/teams'.format(base_url=self.base_url)
        payload = {
            'query': team_name
        }
        r = requests.get(url, params=payload, headers=self.headers)
        if r.status_code == 200:
            return r.json()['teams'][0]['id']
        else:
            raise ValueError('get_team_id returned status code {status_code}'
                             .format(status_code=r.status_code))

    def get_users_in_team(self, team_id):
        """GET a list of users from the team ID"""

        url = '{base_url}/users'.format(base_url=self.base_url)
        payload = {
            'team_ids[]': team_id,
            'limit': 26
        }
        r = requests.get(url, params=payload, headers=self.headers)
        if r.status_code == 200:
            return r.json()['users']
        else:
            raise ValueError(
                'get_team_id returned status code {status_code}\n{error_body}'
                .format(status_code=r.status_code, error_body=r.text)
            )

    def get_user_id(self, user_query):
        """GET the user ID from the user name or email"""

        url = '{base_url}/users'.format(base_url=self.base_url)
        payload = {
            'query': user_query
        }
        r = requests.get(url, params=payload, headers=self.headers)
        if r.status_code == 200:
            if len(r.json()['users']) > 1:
                raise ValueError(
                    'Found more than one user for {query}. \
                    Please use a unique identifier'.format(query=user_query)
                )
            else:
                return r.json()['users'][0]['id']
        else:
            raise ValueError(
                'get_user_id returned status code {status_code}\n{error_body}'
                .format(status_code=r.status_code, error_body=r.text)
            )

    def create_schedule(self, payload):
        """Create a schedule"""

        url = '{base_url}/schedules'.format(base_url=self.base_url)
        r = requests.post(url, data=json.dumps(payload), headers=self.headers)
        if r.status_code == 201:
            return r.json()
        else:
            raise ValueError(
                'create_schedule returned status code {status_code}\
                \n{error_body}'
                .format(status_code=r.status_code, error_body=r.text)
            )

    def delete_schedule(self, schedule_id):
        """Delete a schedule"""

        url = '{base_url}/schedules/{id}'.format(
            base_url=self.base_url,
            id=schedule_id
        )
        r = requests.delete(url, headers=self.headers)
        if r.status_code == 204:
            return r.status_code
        else:
            raise ValueError(
                'delete_schedule returned status code {status_code}\
                \n{error_body}'
                .format(status_code=r.status_code, error_body=r.text)
            )

    def create_escalation_policy(self, payload):
        """Create an escalation policy"""

        url = '{base_url}/escalation_policies'.format(base_url=self.base_url)
        r = requests.post(url, data=json.dumps(payload), headers=self.headers)
        if r.status_code == 201:
            return r.json()
        else:
            raise ValueError(
                'create_escalation_policy returned status code {status_code}\
                \n{error_body}'
                .format(status_code=r.status_code, error_body=r.text)
            )

    def delete_escalation_policy(self, escalation_policy_id):
        """Delete an escalation policy"""

        url = '{base_url}/escalation_policies/{id}'.format(
            base_url=self.base_url,
            id=escalation_policy_id
        )
        r = requests.delete(url, headers=self.headers)
        if r.status_code == 204:
            return r.status_code
        else:
            raise ValueError(
                'delete_escalation_policy returned status code {status_code}\
                \n{error_body}'
                .format(status_code=r.status_code, error_body=r.text)
            )


# WEEKLY SHIFT FUNCTIONS ##################################################
class WeeklyShiftLogic():
    """Class to house the weekly shift import logic"""

    def __init__(self, base_name, level_name, multi_name, start_date,
                 end_date, time_zone, num_loops, escalation_delay):
        self.base_name = base_name
        self.level_name = level_name
        self.multi_name = multi_name
        self.start_date = start_date
        self.end_date = end_date
        self.time_zone = time_zone
        self.num_loops = num_loops
        self.escalation_delay = escalation_delay

    def create_days_of_week(self, file):
        """Parse CSV file into days of week"""

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
            if (row['day_of_week'] == 0 or
                    row['day_of_week'].lower() == 'sunday'):
                sunday_entries.append(entry)
            elif (row['day_of_week'] == 1 or
                    row['day_of_week'].lower() == 'monday'):
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
            elif (row['day_of_week'] == 5 or
                    row['day_of_week'].lower() == 'friday'):
                friday_entries.append(entry)
            elif (row['day_of_week'] == 6 or
                  row['day_of_week'].lower() == 'saturday'):
                saturday_entries.append(entry)
            elif (row['day_of_week'] == 'weekday' or
                  row['day_of_week'] == 'weekdays'):
                monday_entries.append(entry)
                tuesday_entries.append(entry)
                wednesday_entries.append(entry)
                thursday_entries.append(entry)
                friday_entries.append(entry)
            elif (row['day_of_week'] == 'weekend' or
                  row['day_of_week'] == 'weekends'):
                saturday_entries.append(entry)
                sunday_entries.append(entry)
            elif row['day_of_week'] == 'all':
                monday_entries.append(entry)
                tuesday_entries.append(entry)
                wednesday_entries.append(entry)
                thursday_entries.append(entry)
                friday_entries.append(entry)
                saturday_entries.append(entry)
                sunday_entries.append(entry)
            else:
                print (
                    'Error: Entry {name} has an unknown value for day_of_week: \
                    {day}'.format(
                        name=row['user_or_team'],
                        day=row['day_of_week']
                    )
                )
        # Create days with entries
        sunday = {'day_of_week': 0, 'entries': sunday_entries}
        monday = {'day_of_week': 1, 'entries': monday_entries}
        tuesday = {'day_of_week': 2, 'entries': tuesday_entries}
        wednesday = {'day_of_week': 3, 'entries': wednesday_entries}
        thursday = {'day_of_week': 4, 'entries': thursday_entries}
        friday = {'day_of_week': 5, 'entries': friday_entries}
        saturday = {'day_of_week': 6, 'entries': saturday_entries}
        return [sunday, monday, tuesday, wednesday, thursday, friday, saturday]

    def split_teams_into_users(self, pd_rest, days):
        """Split teams into multiple user entries"""

        output = []
        for i, day in enumerate(days):
            output.append({'day_of_week': i, 'entries': []})
            total_entries = 0
            for j, entry in enumerate(day['entries']):
                if entry['type'].lower() == 'team':
                    users = pd_rest.get_users_in_team(pd_rest.get_team_id(
                        entry['id'])
                    )
                    for user in users:
                        total_entries += 1
                        output[i]['entries'].append({
                            'escalation_level': entry['escalation_level'],
                            'id': user['email'],
                            'type': 'user',
                            'start_time': entry['start_time'],
                            'end_time': entry['end_time']
                        })
                elif entry['type'].lower() == 'user':
                    total_entries += 1
                    output[i]['entries'].append(entry)
                else:
                    raise ValueError('Type must be of user or team')
                if total_entries > 25:
                    raise ValueError(
                        'Can only have a maximum of 25 targets per \
                        escalation policy level'
                    )
        return output

    def get_user_ids(self, pd_rest, days):
        """Replace user names and emails with user IDs"""

        for i, day in enumerate(days):
            for j, entry in enumerate(day['entries']):
                days[i]['entries'][j]['id'] = pd_rest.get_user_id(entry['id'])
        return days

    def split_days_by_level(self, base_ep):
        """Split days in escalation policy by level"""

        levels = {}
        ep_by_level = []
        for day in base_ep[0]['schedules'][0]['days']:
            for entry in day['entries']:
                if str(entry['escalation_level']) in levels:
                    (levels[str(entry['escalation_level'])]['days']
                     [str(day['day_of_week'])].append(entry))
                else:
                    levels[str(entry['escalation_level'])] = (
                        {'days': {
                            '0': [],
                            '1': [],
                            '2': [],
                            '3': [],
                            '4': [],
                            '5': [],
                            '6': []
                        }}
                    )
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
            ep_by_level.insert(int(level), {
                'schedules': [{
                    'name': '{base_name} {level_name} {level}'
                    .format(
                        base_name=base_ep[0]['schedules'][0]['name'],
                        level_name=self.level_name,
                        level=level
                    ),
                    'days': days
                }]
            })
        return ep_by_level

    def get_time_periods(self, ep_by_level):
        """Breaks out each day by time period"""

        for level in ep_by_level:
            for i, day in enumerate(level['schedules'][0]['days']):
                time_periods = []
                for entry in day:
                    # Loop through current time_periods to check for overlaps
                    if len(time_periods) > 0:
                        overlap = False
                        for period in time_periods:
                            # TODO: Handle cases where times overlap but are not exactly the same start & end # NOQA
                            if (entry['start_time'] == period['start_time'] and
                               entry['end_time'] == period['end_time']):
                                period['entries'].append({
                                    'id': entry['id'],
                                    'type': entry['type']
                                })
                                overlap = True
                                break
                        if not overlap:
                            time_periods.append({
                                'start_time': entry['start_time'],
                                'end_time': entry['end_time'],
                                'entries': [{
                                    'id': entry['id'],
                                    'type': entry['type']
                                }]
                            })
                    else:
                        time_periods.append({
                            'start_time': entry['start_time'],
                            'end_time': entry['end_time'],
                            'entries': [{
                                'id': entry['id'],
                                'type': entry['type']
                            }]
                        })
                level['schedules'][0]['days'][i] = {
                    "time_periods": time_periods
                }
        return ep_by_level

    def check_for_overlap(self, ep_by_level):
        """Checks time periods for multiple entries and breaks the entries into \
        multiple schedules
        """

        output = []
        for i, level in enumerate(ep_by_level):
            output.append({
                'schedules': [
                    {
                        'name': level['schedules'][0]['name'],
                        'days': []
                    }
                ]
            })
            new_base_name = level['schedules'][0]['name']
            for j, day in enumerate(level['schedules'][0]['days']):
                output[i]['schedules'][0]['days'].append({'time_periods': []})
                if len(day['time_periods']) == 0:
                    continue
                for k, period in enumerate(day['time_periods']):
                    if len(period['entries']) > 1:
                        for l, entry in enumerate(period['entries']):
                            try:
                                output[i]['schedules'][l]['name'] = (
                                    '{base_name} {multi_name} {multiple}'
                                    .format(
                                        base_name=new_base_name,
                                        multi_name=self.multi_name,
                                        multiple=l + 1
                                    )
                                )
                                (output[i]['schedules'][l]['days'][j]
                                    ['time_periods']).append({
                                        'start_time': period['start_time'],
                                        'end_time': period['end_time'],
                                        'id': entry['id'],
                                        'type': entry['type']
                                    })
                            except IndexError:
                                output[i]['schedules'].insert(
                                    l,
                                    {
                                        'name': '{base_name} {multi_name} \
                                        {multiple}'.format(
                                            base_name=new_base_name,
                                            multi_name=self.multi_name,
                                            multiple=l + 1
                                        ),
                                        'days': [
                                            {'time_periods': []},
                                            {'time_periods': []},
                                            {'time_periods': []},
                                            {'time_periods': []},
                                            {'time_periods': []},
                                            {'time_periods': []},
                                            {'time_periods': []}
                                        ]
                                    }
                                )
                                (output[i]['schedules'][l]['days'][j]
                                    ['time_periods']).append({
                                        'start_time': period['start_time'],
                                        'end_time': period['end_time'],
                                        'id': entry['id'],
                                        'type': entry['type']
                                    })
                    else:
                        (output[i]['schedules'][0]['days'][j]
                            ['time_periods']).append({
                                'start_time': period['start_time'],
                                'end_time': period['end_time'],
                                'id': period['entries'][0]['id'],
                                'type': period['entries'][0]['type']
                            })
        return output

    def concat_time_periods(self, schedule):
        """Concatenate any time periods that cross multiple days together"""

        output = {'name': schedule['name'], 'time_periods': []}
        for i, day in enumerate(schedule['days']):
            for period in day['time_periods']:
                foundMatch = False
                for j, tp in enumerate(output['time_periods']):
                    if (period['start_time'] == tp['start_time'] and
                            period['end_time'] == tp['end_time'] and
                            period['id'] == tp['id']):
                        output['time_periods'][j]['days'].append(i)
                        foundMatch = True
                        break
                if not foundMatch:
                    output['time_periods'].append({
                        'start_time': period['start_time'],
                        'end_time': period['end_time'],
                        'id': period['id'],
                        'days': [i]
                    })
        return output

    def get_schedule_payload(self, schedule):
        # TODO: Handle rotations and rotation lengths or at least don't hard code a random value # NOQA
        # TODO: Handle different date formats
        start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        tz = pytz.timezone(self.time_zone)
        output = {
            'schedule': {
                'name': schedule['name'],
                'type': 'schedule',
                'time_zone': self.time_zone,
                'schedule_layers': []
            }
        }
        if not self.end_date:
            for i, period in enumerate(schedule['time_periods']):
                output['schedule']['schedule_layers'].append({
                    'start': tz.localize(start_date).isoformat(),
                    'rotation_virtual_start': tz.localize(start_date)
                    .isoformat(),
                    'rotation_turn_length_seconds': 3600,
                    'users': [{
                        'user': {
                            'id': period['id'],
                            'type': 'user_reference'
                        }
                    }],
                    'restrictions': []
                })
                # Set to daily_restriction if the period exists for all days
                if len(period['days']) == 7:
                    (output
                     ['schedule']['schedule_layers'][i]['restrictions']
                     ).append({
                        'type': 'daily_restriction',
                        'start_time_of_day': time.strftime(
                            '%H:%M:%S',
                            time.gmtime(self.get_seconds(period['start_time']))
                        ),
                        'duration_seconds': (
                            self.get_seconds(period['end_time']) -
                            self.get_seconds(period['start_time'])
                        )
                     })
                else:
                    for day in period['days']:
                        if day == 0:
                            day = 7
                        (output
                         ['schedule']['schedule_layers'][i]['restrictions']
                         ).append({
                            'type': 'weekly_restriction',
                            'start_time_of_day': time.strftime(
                                '%H:%M:%S',
                                time.gmtime(self.get_seconds(
                                    period['start_time']
                                ))
                            ),
                            'duration_seconds': (self.get_seconds(
                                period['end_time']
                            ) - self.get_seconds(
                                period['start_time']
                            )),
                            'start_day_of_week': day
                         })
        else:
            for i, period in enumerate(schedule['time_periods']):
                output['schedule']['schedule_layers'].append({
                    'start': tz.localize(start_date).isoformat(),
                    'end': tz.localize(datetime
                                       .strptime(self.end_date, '%Y-%m-%d')
                                       ).isoformat(),
                    'rotation_virtual_start': tz.localize(start_date)
                    .isoformat(),
                    'rotation_turn_length_seconds': 3600,
                    'users': [{
                        'user': {
                            'id': period['id'],
                            'type': 'user_reference'
                        }
                    }],
                    'restrictions': []
                })
                # Set to daily_restriction if the period exists for all days
                if len(period['days']) == 7:
                    (output
                     ['schedule']['schedule_layers'][i]['restrictions']
                     ).append({
                        'type': 'daily_restriction',
                        'start_time_of_day': time.strftime(
                            '%H:%M:%S',
                            time.gmtime(self.get_seconds(period['start_time']))
                        ),
                        'duration_seconds': (
                            self.get_seconds(period['end_time']) -
                            self.get_seconds(period['start_time'])
                        )
                     })
                else:
                    for day in period['days']:
                        if day == 0:
                            day = 7
                        (output
                         ['schedule']['schedule_layers'][i]['restrictions']
                         ).append({
                            'type': 'weekly_restriction',
                            'start_time_of_day': time.strftime(
                                '%H:%M:%S',
                                time.gmtime(
                                    self.get_seconds(period['start_time'])
                                )
                            ),
                            'duration_seconds': (self.get_seconds(
                                period['end_time']
                            ) - self.get_seconds(
                                period['start_time']
                            )),
                            'start_day_of_week': day
                         })
        return output

    def get_escalation_policy_payload(self, ep_by_level):
        if self.num_loops == 0:
            output = {
                'escalation_policy': {
                    'name': self.base_name,
                    'type': 'escalation_policy',
                    'escalation_rules': [],
                    'repeat_enabled': False
                }
            }
        else:
            output = {
                'escalation_policy': {
                    'name': self.base_name,
                    'type': 'escalation_policy',
                    'escalation_rules': [],
                    'repeat_enabled': True,
                    'num_loops': self.num_loops
                }
            }
        for i, level in enumerate(ep_by_level):
            output['escalation_policy']['escalation_rules'].append({
                'escalation_delay_in_minutes': self.escalation_delay,
                'targets': []
            })
            for schedule in level['schedules']:
                (output
                 ['escalation_policy']['escalation_rules'][i]['targets']
                 ).append({
                    'id': schedule,
                    'type': 'schedule_reference'
                 })
        return output

    # HELPER FUNCTIONS ########################################################
    def get_seconds(self, time):
        """Helper function to get the seconds since 00:00:00"""

        time_list = time.split(':')
        if len(time_list) == 3:
            return (int(time_list[0]) * 3600 + int(time_list[1]) * 60 +
                    int(time_list[2]))
        elif len(time_list) == 2:
            return int(time_list[0]) * 3600 + int(time_list[1]) * 60
        else:
            raise ValueError(
                'Invalid input. Time must be of format HH:MM:SS or HH:MM. \
                You input: {time}'.format(time=time)
            )


# STANDARD ROTATION FUNCTIONS #################################################
class StandardRotationLogic():
    """Class to house the standard rotation import logic"""

    def __init__(self, start_date, end_date, name, time_zone):
        self.start_date = start_date,
        self.end_date = end_date,
        self.name = name,
        self.time_zone = time_zone

    def get_restriction_type(self, start_day, end_day):
        acceptable_days = [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday'
        ]
        if not start_day and not end_day:
            return "daily_restriction"
        elif (start_day in acceptable_days and end_day in acceptable_days):
            if start_day == end_day:
                return "daily_restriction"
            else:
                return "weekly_restriction"
        elif (start_day.lower() in acceptable_days
              and end_day.lower() in acceptable_days):
            if start_day.lower() == end_day.lower():
                return "daily_restriction"
            else:
                return "weekly_restriction"
        else:
            raise ValueError(
                'Invalid restrict start or end date provided. Dates must be in \
                null, 0, 1, 2, 3, 4, 5, 6, monday, tuesday, wednesday, \
                thursday, friday, saturday, sunday.'
            )

    def get_rotation_turn_length(self, rotation_type, shift_length,
                                 shift_type):
        """Get the rotation turn length for the layer"""

        if rotation_type == 'daily':
            return 86400
        elif rotation_type == 'weekly':
            return 604800
        elif rotation_type == 'custom':
            if shift_type == 'hours':
                return int(shift_length) * 3600
            elif shift_type == 'days':
                return int(shift_length) * 86400
            elif shift_type == 'weeks':
                return int(shift_length) * 604800
            else:
                raise ValueError(
                    'Invalid shift_type provided. Must be one of hours, days, \
                    weeks.'
                )
        else:
            raise ValueError(
                'Invalid rotation_type provided. Must be one of daily, weekly, \
                custom.'
            )

    def get_virtual_start(self, rotation_type, handoff_day, handoff_time,
                          start_date, time_zone):
        """Get the start datetime for the layer"""

        tz = pytz.timezone(time_zone)
        start_date = self.get_datetime(start_date, handoff_time)
        if rotation_type == 'daily':
            return tz.localize(start_date).isoformat()
        elif rotation_type == 'weekly':
            weekday = tz.localize(start_date).weekday()
            handoff_weekday = self.get_weekday(handoff_day)
            return self.start_date_timedelta(
                handoff_weekday,
                weekday,
                start_date,
                tz
            )
        elif rotation_type == 'custom':
            if not handoff_day:
                return tz.localize(start_date).isoformat()
            else:
                # TODO: Write tests for handoff_day in incorrect format
                if datetime.strptime(handoff_day, '%Y-%m-%d') < start_date:
                    raise ValueError('handoff_day must come after start_date.')
                else:
                    return tz.localize(self.get_datetime(
                        handoff_day,
                        handoff_time
                    )).isoformat()
        else:
            raise ValueError(
                'Invalid rotation_type provided. Must be one of daily, \
                weekly, custom.'
            )

    def get_restriction_duration(self, type, start_day, start_time,
                                 end_day, end_time):
        """Get the restriction duration in seconds"""

        if type == 'daily_restriction':
            start_datetime = self.get_datetime(
                date(
                    datetime.now().year,
                    datetime.now().month,
                    datetime.now().day
                ),
                start_time
            )
            end_datetime = self.get_datetime(
                date(
                    datetime.now().year,
                    datetime.now().month,
                    datetime.now().day
                ),
                end_time
            )
            if start_datetime < end_datetime:
                return int((end_datetime - start_datetime).total_seconds())
            elif start_datetime > end_datetime:
                end_datetime += timedelta(days=1)
                return int((end_datetime - start_datetime).total_seconds())
            else:
                raise ValueError(
                    'Invalid input provided. The restriction start and end \
                    datetimes are equal.'
                )
        else:
            start_weekday = self.get_weekday(start_day)
            end_weekday = self.get_weekday(end_day)
            if start_weekday < end_weekday:
                start_datetime = self.get_datetime(
                    date(
                        datetime.now().year,
                        datetime.now().month,
                        datetime.now().day
                    ),
                    start_time
                )
                end_datetime = self.get_datetime(
                    date(
                        datetime.now().year,
                        datetime.now().month,
                        datetime.now().day
                    ) + timedelta(
                        days=end_weekday - start_weekday
                    ),
                    end_time
                )
                return int((end_datetime - start_datetime).total_seconds())
            elif start_weekday > end_weekday:
                start_datetime = self.get_datetime(
                    date(
                        datetime.now().year,
                        datetime.now().month,
                        datetime.now().day
                    ),
                    start_time
                )
                end_datetime = self.get_datetime(
                    date(
                        datetime.now().year,
                        datetime.now().month,
                        datetime.now().day
                    ) + timedelta(
                        days=7 - start_weekday + end_weekday
                    ),
                    end_time
                )
                return int((end_datetime - start_datetime).total_seconds())
            else:
                raise ValueError(
                    'Invalid input provided. The restriction start and end \
                    datetimes are equal'
                )

    def parse_csv(self, file):
        """Parse CSV file into layer-by-user based dictionary"""

        reader = csv.DictReader(open(file), fieldnames=(
            'user',
            'layer',
            'layer_name',
            'rotation_type',
            'shift_length',
            'shift_type',
            'handoff_day',
            'handoff_time',
            'restriction_start_day',
            'restriction_start_time',
            'restriction_end_day',
            'restriction_end_time'
        ))
        reader.next()
        layers = {}
        levels = []
        for row in reader:
            # TODO: Allow users to enter layer name
            shift_length = self.nullify(row['shift_length'])
            shift_type = self.nullify(row['shift_type'])
            handoff_day = self.nullify(row['handoff_day'])
            restriction_start_day = self.nullify(row['restriction_start_day'])
            restriction_start_time = self.nullify(
                row['restriction_start_time']
            )
            restriction_end_day = self.nullify(row['restriction_end_day'])
            restriction_end_time = self.nullify(row['restriction_end_time'])
            if row['layer'] not in levels:
                levels.append(row['layer'])
                layers[row['layer']] = [{
                    'user': row['user'],
                    'layer_name': row['layer_name'],
                    'rotation_type': row['rotation_type'],
                    'shift_length': shift_length,
                    'shift_type': shift_type,
                    'handoff_day': handoff_day,
                    'handoff_time': row['handoff_time'],
                    'restriction_start_day': restriction_start_day,
                    'restriction_start_time': restriction_start_time,
                    'restriction_end_day': restriction_end_day,
                    'restriction_end_time': restriction_end_time,
                    'restriction_type': self.get_restriction_type(
                        row['restriction_start_day'],
                        row['restriction_end_day']
                    )
                }]
            else:
                layers[row['layer']].append({
                    'user': row['user'],
                    'layer_name': row['layer_name'],
                    'rotation_type': row['rotation_type'],
                    'shift_length': shift_length,
                    'shift_type': shift_type,
                    'handoff_day': handoff_day,
                    'handoff_time': row['handoff_time'],
                    'restriction_start_day': restriction_start_day,
                    'restriction_start_time': restriction_start_time,
                    'restriction_end_day': restriction_end_day,
                    'restriction_end_time': restriction_end_time
                })
        return layers

    def check_layers(self, layers):
        """Checks layers to ensure the CSV was entered correctly and all
        layer data is the same for each user
        """

        for i in layers:
            master_user = {
                'layer_name': layers[i][0]['layer_name'],
                'rotation_type': layers[i][0]['rotation_type'],
                'shift_length': layers[i][0]['shift_length'],
                'shift_type': layers[i][0]['shift_type'],
                'handoff_day': layers[i][0]['handoff_day'],
                'handoff_time': layers[i][0]['handoff_time'],
                'restriction_start_day': layers[i][0]['restriction_start_day'],
                'restriction_start_time': layers[i][0]
                ['restriction_start_time'],
                'restriction_end_day': layers[i][0]['restriction_end_day'],
                'restriction_end_time': layers[i][0]['restriction_end_time']
            }
            for user in layers[i]:
                if (master_user['layer_name'] != user['layer_name'] or
                   master_user['rotation_type'] != user['rotation_type'] or
                   master_user['shift_length'] != user['shift_length'] or
                   master_user['shift_type'] != user['shift_type'] or
                   master_user['handoff_day'] != user['handoff_day'] or
                   master_user['handoff_time'] != user['handoff_time'] or
                   master_user['restriction_start_day'] !=
                   user['restriction_start_day'] or
                   master_user['restriction_start_time'] !=
                   user['restriction_start_time'] or
                   master_user['restriction_end_day'] !=
                   user['restriction_end_day'] or
                   master_user['restriction_end_time'] !=
                   user['restriction_end_time']):
                    return False
                else:
                    pass
        return True

    def parse_layers(self, start_date, end_date, time_zone, layers, pd_rest):
        """Parses layers by user into the format for schedule layers on the
        PagerDuty v2 REST API
        """

        output = []
        tz = pytz.timezone(time_zone)
        # TODO: Allow for start/end times, handoff_time?
        start_datetime = self.get_datetime(start_date, "00:00:00")
        layer_index = 0
        for i, level in enumerate(layers):
            output.append({
                'name': layers[str(layer_index + 1)][0]['layer_name'],
                'start': tz.localize(start_datetime).isoformat(),
                'rotation_virtual_start': self.get_virtual_start(
                    layers[str(layer_index + 1)][0]['rotation_type'],
                    layers[str(layer_index + 1)][0]['handoff_day'],
                    layers[str(layer_index + 1)][0]['handoff_time'],
                    start_date,
                    time_zone
                ),
                'rotation_turn_length_seconds': self.get_rotation_turn_length(
                    layers[str(layer_index + 1)][0]['rotation_type'],
                    layers[str(layer_index + 1)][0]['shift_length'],
                    layers[str(layer_index + 1)][0]['shift_type']
                ),
                'users': [],
                'restrictions': [
                    {
                        'type': layers[str(layer_index + 1)][0]
                        ['restriction_type'],
                        'start_time_of_day': layers[str(layer_index + 1)][0]
                        ['restriction_start_time'],
                        'start_day_of_week': self.get_weekday(
                            layers[str(layer_index + 1)][0]
                            ['restriction_start_day']
                        ) + 1,
                        'duration_seconds': self.get_restriction_duration(
                            layers[str(layer_index + 1)][0]
                            ['restriction_type'],
                            layers[str(layer_index + 1)][0]
                            ['restriction_start_day'],
                            layers[str(layer_index + 1)][0]
                            ['restriction_start_time'],
                            layers[str(layer_index + 1)][0]
                            ['restriction_end_day'],
                            layers[str(layer_index + 1)][0]
                            ['restriction_end_time']
                        )
                    }
                ]
            })
            # Add end_date if applicable
            if end_date:
                end_datetime = self.get_datetime(end_date, "00:00:00")
                output[i]['end'] = tz.localize(end_datetime).isoformat()
            for user in layers[str(layer_index + 1)]:
                output[layer_index]['users'].append({
                    'user': {
                        'id': pd_rest.get_user_id(user['user']),
                        'type': 'user'
                    }
                })
            layer_index += 1
        return output

    def parse_schedules(self, time_zone, layers):
        """Returns a dictrionary in the format required to create a PagerDuty
        schedule on the v2 REST API
        """

        return {
            'name': self.name[0],
            'type': 'schedule',
            'time_zone': time_zone,
            'schedule_layers': layers
        }

    # HELPER FUNCTIONS
    def get_datetime(self, date, time):
        """Helper function to parse multiple datetime formats"""

        date_time = "{date}T{time}".format(
            date=date,
            time=time
        )
        # Handle different time formats
        if len(time.split(':')) == 3:
            output = datetime.strptime(
                date_time,
                '%Y-%m-%dT%H:%M:%S'
            )
        elif len(time.split(':')) == 2:
            output = datetime.strptime(
                date_time,
                '%Y-%m-%dT%H:%M'
            )
        else:
            raise ValueError(
                'Invalid handoff_time. Format must be in HH:MM or \
                HH:MM:SS.'
            )
        return output

    def start_date_timedelta(self, handoff_day, weekday, start_date, tz):
        """Helper function to add timedelta to virtual start date"""

        if weekday < handoff_day:
            start_date += timedelta(days=(handoff_day - weekday))
            return tz.localize(start_date).isoformat()
        elif weekday == handoff_day:
            return tz.localize(start_date).isoformat()
        else:
            start_date += timedelta(days=(7 + handoff_day - weekday))
            return tz.localize(start_date).isoformat()

    def get_weekday(self, weekday):
        """Helper function to convert CSV day into Python datetime weekday"""

        if type(weekday) is int:
            if weekday == 1:
                return 0
            elif weekday == 2:
                return 1
            elif weekday == 3:
                return 2
            elif weekday == 4:
                return 3
            elif weekday == 5:
                return 4
            elif weekday == 6:
                return 5
            elif weekday == 0:
                return 6
            else:
                raise ValueError(
                    'Invalid handoff_day provided. Must be one of 0, 1, 2, 3, \
                    4, 5, 6, monday, tuesday, wednesday, thursday, friday, \
                    saturday, sunday'
                )
        else:
            if weekday.lower() == 'monday':
                return 0
            elif weekday.lower() == 'tuesday':
                return 1
            elif weekday.lower() == 'wednesday':
                return 2
            elif weekday.lower() == 'thursday':
                return 3
            elif weekday.lower() == 'friday':
                return 4
            elif weekday.lower() == 'saturday':
                return 5
            elif weekday.lower() == 'sunday':
                return 6
            else:
                raise ValueError(
                    'Invalid handoff_day provided. Must be one of 0, 1, 2, 3, \
                    4, 5, 6, monday, tuesday, wednesday, thursday, friday, \
                    saturday, sunday'
                )

    def nullify(self, val):
        """Helper function to nullify empty strings"""

        if val == "":
            return None
        else:
            return val


class Import():
    """Class to import schedules using the PyPi module"""

    def __init__(self, schedule_type, csv_dir, api_key, base_name, level_name,
                 multi_name, start_date, end_date, time_zone, num_loops,
                 escalation_delay):
        self.schedule_type = schedule_type
        self.csv_dir = csv_dir
        self.api_key = api_key
        self.base_name = base_name
        self.level_name = level_name
        self.multi_name = multi_name
        self.start_date = start_date
        self.end_date = end_date
        self.time_zone = time_zone
        self.num_loops = num_loops
        self.escalation_delay = escalation_delay

    def execute(self):
        """Function to execute the main import logic"""

        main(self.schedule_type, self.csv_dir, self.api_key, self.base_name,
             self.level_name, self.multi_name, self.start_date, self.end_date,
             self.time_zone, self.num_loops, self.escalation_delay)


def main(schedule_type, csv_dir, api_key, base_name, level_name, multi_name,
         start_date, end_date, time_zone, num_loops, escalation_delay):
    """Function to import schedules using the command line"""

    # Declare an instance of PagerDutyREST
    pd_rest = PagerDutyREST(api_key)
    # Handle trailing slash on CSV directory
    if csv_dir[-1:] == '/':
        csv_dir = csv_dir[:-1]
    # Get all CSV files
    files = glob.glob(os.path.join(os.getcwd(), csv_dir, '*.csv'))
    if len(files) > 1:
        for i in range(len(files)):
            files[i] = {
                'filename': files[i],
                'base_name': '{name} #{number}'.format(
                    name=base_name,
                    number=i + 1
                )
            }
    elif len(files) == 1:
        files[0] = {
            'filename': files[0],
            'base_name': base_name
        }
    else:
        raise Exception('No CSV files found.')
    # Check on the schedule type
    if schedule_type == 'standard_rotation':
        # Loop through all CSV files
        for file in files:
            standard_rotation = StandardRotationLogic(
                start_date,
                end_date,
                file['base_name'],
                time_zone
            )
            layers = standard_rotation.parse_csv(file['filename'])
            if not standard_rotation.check_layers(layers):
                raise ValueError(
                    'There is an issue with the {filename} CSV. All layers \
                    must match on layer_name, rotation_type, shift_length, \
                    shift_type, handoff_day, handoff_time, \
                    restriction_start_day, restriction_start_time, \
                    restriction_end_day, and restriction_end_time.'
                )
            # TODO: Use the variables in __init__ instead of these
            layers = standard_rotation.parse_layers(start_date, end_date,
                                                    time_zone, layers, pd_rest)
            schedule = standard_rotation.parse_schedules(time_zone,
                                                         layers)
            res = pd_rest.create_schedule(schedule)
            print "Successfully created schedule with ID {schedule_id}".format(
                schedule_id=res['schedule']['id']
            )
    elif schedule_type == 'weekly_shifts':
        if (not level_name or not multi_name or not num_loops
           or not escalation_delay):
            raise ValueError(
                'Invalid command line arguments. To import weekly shift \
                schedules you must pass --base-name, --level-name, \
                --multi-name, --start-date, --time-zone, --num-loops, and \
                --escalation-delay.'
            )
        # Loop through all CSV files
        for file in files:
            weekly_shifts = WeeklyShiftLogic(
                file['base_name'],
                level_name,
                multi_name,
                start_date,
                end_date,
                time_zone,
                num_loops,
                escalation_delay
            )
            days = weekly_shifts.create_days_of_week(file['filename'])
            # Split teams into their particular users
            days = weekly_shifts.split_teams_into_users(pd_rest, days)
            # Update user names/emails to user IDs
            days = weekly_shifts.get_user_ids(pd_rest, days)
            # Create list of escalation policies by level
            base_ep = [{
                'schedules': [{
                    'name': weekly_shifts.base_name,
                    'days': days
                }]
            }]
            ep_by_level = weekly_shifts.split_days_by_level(base_ep)
            # TODO: Handle cominbing cases where one on-call starts at 0:00 and another ends at 24:00 # NOQA
            ep_by_level = weekly_shifts.get_time_periods(ep_by_level)
            ep_by_level = weekly_shifts.check_for_overlap(ep_by_level)
            # Create schedules in PagerDuty
            for i, level in enumerate(ep_by_level):
                for j, schedule in enumerate(level['schedules']):
                    schedule_by_periods = weekly_shifts.concat_time_periods(
                        schedule
                    )
                    schedule_payload = weekly_shifts.get_schedule_payload(
                        schedule_by_periods
                    )
                    schedule_id = pd_rest.create_schedule(
                        schedule_payload
                    )['schedule']['id']
                    ep_by_level[i]['schedules'][j] = schedule_id
            # Create escalation policy in PagerDuty
            escalation_policy_payload = (weekly_shifts
                                         .get_escalation_policy_payload(
                                            ep_by_level
                                         ))
            res = pd_rest.create_escalation_policy(escalation_policy_payload)
            print "Successfully created escalation policy: {id}".format(
                id=res['escalation_policy']['id']
            )
    else:
        raise ValueError(
            'Invalid command line arguments. --schedule-type must one of \
            standard_rotation, weekly_shifts.'
        )

# TODO: Write tests for various arguments
# TODO: Use list comprehension where applicable
# TODO: Allow users to set schedule description
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import schedules')
    parser.add_argument(
        '--schedule-type',
        help='Type of schedule(s) being uploaded. Must be one of weekly_shifts,\
         standard_rotation.',
        dest='schedule_type',
        required=True
    )
    parser.add_argument(
        '--csv-dir',
        help='Path to the directory housing all CSVs to import into PagerDuty',
        dest='csv_dir',
        required=True
    )
    parser.add_argument(
        '--api-key',
        help='PagerDuty v2 REST API token',
        dest='api_key',
        required=True
    )
    parser.add_argument(
        '--base-name',
        help='Name of the escalation policy or schedule being added as well as \
        the base name for each schedule added to the escalation policy',
        dest='base_name',
        required=True
    )
    parser.add_argument(
        '--level-name',
        help='Base name for each new escalation policy level to be appended by \
        the level number',
        dest='level_name'
    )
    parser.add_argument(
        '--multiple-name',
        help='Base name for each schedule on the same escalation policy level \
        to be appended by the schedule number',
        dest='multi_name'
    )
    parser.add_argument(
        '--start-date',
        help='ISO 8601 formatted start date for the schedule. Currently only \
        support dates in YYYY-MM-DD format.',
        dest='start_date',
        required=True
    )
    parser.add_argument(
        '--end-date',
        help='ISO 8601 formatted end date for the schedule. Currently only \
        supports dates in YYYY-MM-DD format.',
        dest='end_date'
    )
    parser.add_argument(
        '--time-zone',
        help='Time zone for this schedule. Must be one of the time zones from \
        the IANA time zone database',
        dest='time_zone',
        required=True
    )
    parser.add_argument(
        '--num-loops',
        help='The number of times to loop through the escalation policy',
        dest='num_loops'
    )
    parser.add_argument(
        '--escalation-delay',
        help='The number of minutes to wait before escalating the incident to \
        the next level',
        dest='escalation_delay'
    )
    args = parser.parse_args()
    main(
        args.schedule_type,
        args.csv_dir,
        args.api_key,
        args.base_name,
        args.level_name,
        args.multi_name,
        args.start_date,
        args.end_date,
        args.time_zone,
        args.num_loops,
        args.escalation_delay
    )
