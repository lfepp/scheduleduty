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
import requests
import json
from datetime import datetime
import pytz
import time


# PD REST API FUNCTION #######################################################
class PagerDutyREST():
    """Class to house all PagerDuty REST API call methods"""

    def __init__(self, api_key):
        self.base_url = 'https://api.pagerduty.com'
        self.headers = {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Content-type': 'application/json',
            'Authorization': 'Token token={0}'.format(api_key)
        }

    def get_team_id(self, team_name):
        """GET the team ID from team name"""

        url = '{0}/teams'.format(self.base_url)
        payload = {
            'query': team_name
        }
        r = requests.get(url, params=payload, headers=self.headers)
        if r.status_code == 200:
            return r.json()['teams'][0]['id']
        else:
            raise ValueError('get_team_id returned status code {0}'.format(
                r.status_code
            ))

    # TODO: Handle limit & pagination when >25 users
    def get_users_in_team(self, team_id):
        """GET a list of users from the team ID"""

        url = '{0}/users'.format(self.base_url)
        payload = {
            'team_ids[]': team_id
        }
        r = requests.get(url, params=payload, headers=self.headers)
        if r.status_code == 200:
            return r.json()['users']
        else:
            raise ValueError('get_team_id returned status code {0}\n{1}'.format(
                r.status_code,
                r.text
            ))

    def get_user_id(self, user_query):
        """GET the user ID from the user name or email"""

        url = '{0}/users'.format(self.base_url)
        payload = {
            'query': user_query
        }
        r = requests.get(url, params=payload, headers=self.headers)
        if r.status_code == 200:
            if len(r.json()['users']) > 1:
                raise ValueError('Found more than one user for {0}. Please use a unique identifier'.format(user_query))
            else:
                return r.json()['users'][0]['id']
        else:
            raise ValueError('get_user_id returned status code {0}\n{1}'.format(
                r.status_code,
                r.text
            ))

    def create_schedule(self, payload):
        """Create a schedule"""

        url = '{0}/schedules'.format(self.base_url)
        r = requests.post(url, data=json.dumps(payload), headers=self.headers)
        if r.status_code == 201:
            return r.json()
        else:
            raise ValueError('create_schedule returned status code {0}\n{1}'.format(
                r.status_code,
                r.text
            ))

    def delete_schedule(self, schedule_id):
        """Delete a schedule"""

        url = '{0}/schedules/{1}'.format(self.base_url, schedule_id)
        r = requests.delete(url, headers=self.headers)
        if r.status_code == 204:
            return r.status_code
        else:
            raise ValueError('delete_schedule returned status code {0}\n{1}'.format(
                r.status_code,
                r.text
            ))

    def create_escalation_policy(self, payload):
        """Create an escalation policy"""

        url = '{0}/escalation_policies'.format(self.base_url)
        r = requests.post(url, data=json.dumps(payload), headers=self.headers)
        if r.status_code == 201:
            return r.json()
        else:
            raise ValueError('create_escalation_policy returned status code {0}\n{1}'.format(
                r.status_code,
                r.text
            ))

    def delete_escalation_policy(self, escalation_policy_id):
        """Delete an escalation policy"""

        url = '{0}/escalation_policies/{1}'.format(self.base_url, escalation_policy_id)
        r = requests.delete(url, headers=self.headers)
        if r.status_code == 204:
            return r.status_code
        else:
            raise ValueError('delete_escalation_policy returned status code {0}\n{1}'.format(
                r.status_code,
                r.text
            ))


# TODO: Create a WeeklyUserLogic class for extensibility
# WEEKLY IMPORT FUNCTIONS ##################################################
def create_days_of_week(file):
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
        else:
            print ('Error: Entry {0} has an unknown value for day_of_week: {1}'
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


def split_teams_into_users(pd_rest, days):
    """Split teams into multiple user entries"""

    output = []
    for i, day in enumerate(days):
        output.append({'day_of_week': i, 'entries': []})
        for j, entry in enumerate(day['entries']):
            if entry['type'].lower() == 'team':
                users = pd_rest.get_users_in_team(pd_rest.get_team_id(entry['id']))
                for user in users:
                    output[i]['entries'].append({
                        'escalation_level': entry['escalation_level'],
                        'id': user['email'],
                        'type': 'user',
                        'start_time': entry['start_time'],
                        'end_time': entry['end_time']
                    })
            elif entry['type'].lower() == 'user':
                output[i]['entries'].append(entry)
            else:
                raise ValueError('Type must be of user or team')
    return output


def get_user_ids(pd_rest, days):
    """Replace user names and emails with user IDs"""

    for i, day in enumerate(days):
        for j, entry in enumerate(day['entries']):
            days[i]['entries'][j]['id'] = pd_rest.get_user_id(entry['id'])
    return days


def split_days_by_level(base_ep):
    """Split days in escalation policy by level"""

    levels = {}
    ep_by_level = []
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
        ep_by_level.insert(int(level), {
            'schedules': [{
                'name': ('{0}_level_{1}'.format(base_ep[0]['schedules'][0]
                         ['name'], level)),
                'days': days
            }]
        })
    return ep_by_level


def get_time_periods(ep_by_level):
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
            level['schedules'][0]['days'][i] = {"time_periods": time_periods}
    return ep_by_level


def check_for_overlap(ep_by_level):
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
        base_name = level['schedules'][0]['name']
        for j, day in enumerate(level['schedules'][0]['days']):
            output[i]['schedules'][0]['days'].append({'time_periods': []})
            if len(day['time_periods']) == 0:
                continue
            for k, period in enumerate(day['time_periods']):
                if len(period['entries']) > 1:
                    for l, entry in enumerate(period['entries']):
                        try:
                            output[i]['schedules'][l]['name'] = (
                                '{0}_multi_{1}'.format(base_name, l + 1)
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
                                    'name': '{0}_multi_{1}'.format(
                                        base_name, l + 1
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


def concatenate_time_periods(schedule):
    """Concatenate any time periods that cross multiple days together"""

    output = {'name': schedule['name'], 'time_periods': []}
    for i, day in enumerate(schedule['days']):
        for period in day['time_periods']:
            foundMatch = False
            for j, tp in enumerate(output['time_periods']):
                if period['start_time'] == tp['start_time'] and period['end_time'] == tp['end_time'] and period['id'] == tp['id']:
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


def get_schedule_payload(schedule, start_date=None):
    # TODO: Allow users to set time zone to something other than UTC
    # TODO: Allow users to set start date
    # TODO: Allow users to set end date
    # TODO: Handle rotations and rotation lengths or at least don't hard code a random value
    if start_date is None:
        start_date = datetime.now()
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    tz = pytz.timezone('UTC')
    output = {
        'schedule': {
            'name': schedule['name'],
            'type': 'schedule',
            'time_zone': 'UTC',
            'schedule_layers': []
        }
    }
    for i, period in enumerate(schedule['time_periods']):
        output['schedule']['schedule_layers'].append({
            'start': tz.localize(start_date).isoformat(),
            'rotation_virtual_start': tz.localize(start_date).isoformat(),
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
            output['schedule']['schedule_layers'][i]['restrictions'].append({
                'type': 'daily_restriction',
                'start_time_of_day': time.strftime('%H:%M:%S', time.gmtime(get_seconds(period['start_time']))),
                'duration_seconds': get_seconds(period['end_time']) - get_seconds(period['start_time'])
            })
        else:
            for day in period['days']:
                output['schedule']['schedule_layers'][i]['restrictions'].append({
                    'type': 'weekly_restriction',
                    'start_time_of_day': time.strftime('%H:%M:%S', time.gmtime(get_seconds(period['start_time']))),
                    'duration_seconds': get_seconds(period['end_time']) - get_seconds(period['start_time'])
                })
    return output


def get_seconds(time):
    """Helper function to get the seconds since 00:00:00"""

    time_list = time.split(':')
    if len(time_list) == 3:
        return int(time_list[0]) * 3600 + int(time_list[1]) * 60 + int(time_list[2])
    elif len(time_list) == 2:
        return int(time_list[0]) * 3600 + int(time_list[1]) * 60
    else:
        raise ValueError('Invalid input. Time must be of format HH:MM:SS or HH:MM: {0}'.format(time))


def main():
    # Loop through all CSV files
    files = glob.glob('src/csv/*.csv')
    for file in files:
        # TODO: Add logic to handle non-weekly schedules
        days = create_days_of_week(file)
        # Split teams into their particular users
        days = split_teams_into_users(days)
        # Create list of escalation policies by level
        base_ep = [{
            'schedules': [{
                # TODO: Use regex to parse filename
                'name': file[8:len(file) - 4],
                'days': days
            }]
        }]
        ep_by_level = split_days_by_level(base_ep)
        # TODO: Handle cominbing cases where one on-call starts at 0:00 and another ends at 24:00 # NOQA
        ep_by_level = get_time_periods(ep_by_level)
        ep_by_level = check_for_overlap(ep_by_level)
        print ep_by_level
    # 5) Remove entries list from the ep_by_level object
    # 6) Break each day down by time period
    # 7) Loop through consecutive days for patterns
    # 8) Each batch of user/time period/consecutive days becomes a new layer
    # 9) When a batch has a team, get the users on that team instead
    # 10) Each possible schedule on each EP level becomes a schedule based on layers in 7 # NOQA
    # 11) EP is created

if __name__ == '__main__':
    sys.exit(main())
