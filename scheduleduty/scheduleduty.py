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
from datetime import datetime
import pytz
import time
import argparse


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


# WEEKLY IMPORT FUNCTIONS ##################################################
class WeeklyUserLogic():
    """Class to house the weekly user import logic"""

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

    def concatenate_time_periods(self, schedule):
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
                            ))
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
                            ))
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


def main(api_key, base_name, level_name, multi_name, start_date,
         end_date, time_zone, num_loops, escalation_delay):
    # Declare an instance of PagerDutyREST
    pd_rest = PagerDutyREST(api_key)
    # Loop through all CSV files
    files = glob.glob('scheduleduty/csv/*.csv')
    for file in files:
        weekly_users = WeeklyUserLogic(
            base_name,
            level_name,
            multi_name,
            start_date,
            end_date,
            time_zone,
            num_loops,
            escalation_delay
        )
        days = weekly_users.create_days_of_week(file)
        # Split teams into their particular users
        days = weekly_users.split_teams_into_users(pd_rest, days)
        # Update user names/emails to user IDs
        days = weekly_users.get_user_ids(pd_rest, days)
        # Create list of escalation policies by level
        base_ep = [{
            'schedules': [{
                'name': weekly_users.base_name,
                'days': days
            }]
        }]
        ep_by_level = weekly_users.split_days_by_level(base_ep)
        # TODO: Handle cominbing cases where one on-call starts at 0:00 and another ends at 24:00 # NOQA
        ep_by_level = weekly_users.get_time_periods(ep_by_level)
        ep_by_level = weekly_users.check_for_overlap(ep_by_level)
        # Create schedules in PagerDuty
        for i, level in enumerate(ep_by_level):
            for j, schedule in enumerate(level['schedules']):
                schedule_by_periods = weekly_users.concatenate_time_periods(
                    schedule
                )
                schedule_payload = weekly_users.get_schedule_payload(
                    schedule_by_periods
                )
                schedule_id = pd_rest.create_schedule(
                    schedule_payload
                )['schedule']['id']
                ep_by_level[i]['schedules'][j] = schedule_id
        # Create escalation policy in PagerDuty
        escalation_policy_payload = weekly_users.get_escalation_policy_payload(
            ep_by_level
        )
        res = pd_rest.create_escalation_policy(escalation_policy_payload)
        print "Successfully create escalation policy: {id}".format(
            id=res['escalation_policy']['id']
        )

# TODO: Handle standard rotation formatted shcedules
# TODO: Write tests for various arguments
# TODO: Use list comprehension where applicable
# TODO: Use keywords for formats or joins on lists where applicable
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Import weekly schedules')
    parser.add_argument(
        '--api-key',
        help='PagerDuty v2 REST API Key',
        dest='api_key'
    )
    parser.add_argument(
        '--base-name',
        help='Name of the escalation policy and base name for each schedule',
        dest='base_name'
    )
    parser.add_argument(
        '--level-name',
        help='Base name for each new level to be appended by the level number',
        dest='level_name'
    )
    parser.add_argument(
        '--multiple-name',
        help='Base name for each schedule on the same layer to be appended by \
        the multiple number',
        dest='multi_name'
    )
    parser.add_argument(
        '--start-date',
        help='ISO 8601 formatted start date for the schedules',
        dest='start_date'
    )
    parser.add_argument(
        '--end-date',
        help='ISO 8601 formatted end date for the schedules',
        dest='end_date')
    parser.add_argument(
        '--time-zone',
        help='Time zone for this schedule in the format of the IANA time zone \
        database',
        dest='time_zone'
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
