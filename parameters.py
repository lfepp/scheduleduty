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


class Target():
    """ Create a Target object to be added to an escalation level

    Attributes:
        id (str): UID of target within PagerDuty
        type (str): Type of target within PagerDuty. Can be one of \
        user_reference, schedule_referece
    """

    def __init__(self, id, type):
        self.id = id
        self.type = type


class EscalationRule():
    """ Creates a new Escalation Rule object

    Attributes:
        delay (int): The number of minutes to stay on this escalation level \
        before escalating to the next
        targets (list): List of all targets to be added to this escalation \
        level
    """

    def __init__(self, delay, targets):
        self.escalation_delay_in_minutes = delay
        self.targets = targets


class Service():
    """ Creates a new Service object

    Attributes:
        id (str): UID of the service within PagerDuty
    """

    def __init__(self, id):
        self.id = id
        self.type = "service_reference"


class EscalationPolicy():
    """ Creates a new Escalation Policy object

    Attributes:
        name (str): Name of the escalation policy
        description (str): Description of the escalation policy
        repeat (bool): Whether or not to repeat the escalation policy if the \
        event remains unacknowledged
        num_loops (int): The number of times to loop through the escalation \
        policy
        escalation_rules (list): List of all escalation rules to be added to \
        this policy
        services (list): List of all services to tie to this escalation policy
    """

    def __init__(self, name, description, repeat, num_loops, escalation_rules,
                 services):
        self.name = name
        self.description = description
        self.repeat_enabled = repeat
        self.num_loops = num_loops
        self.escalation_rules = escalation_rules
        self.services = services
        self.type = "escalation_policy"


class User():
    """ Creates a new User object

    Attributes:
        id (str): UID of the user within PagerDuty
    """

    def __init__(self, id):
        self.id = id
        self.type = "user_reference"


class Restriction():
    """ Creates a new Restriction object

    Attributes:
        type (str): Type of restriction. Can be one of daily_restriction, \
        weekly_restriction
        start_time (str): Time of day the restriction begins
        duration (int): The number of seconds the restriction should last
        start_day (int): The day of the week to start the restriction if \
        using weekly_restriction. Leave blank for daily_restriction
    """

    def __init__(self, type, start_time, duration, start_day=None):
        self.type = type
        self.start_time_of_day = start_time
        self.duration_seconds = duration
        if start_day is not None:
            self.start_day_of_week = start_day


class ScheduleLayer():
    """ Creates a new Schedule Layer object

    Attributes:
        users (list): List of all users to be added to this layer
        rotation_start (str): Date and time that the schedule rotation takes \
        effect
        rotation_turn_length (int): The number of seconds between user \
        rotations
        restrictions (list): List of all on-call shift restrictions for this \
        layer
        start_time (str): Date and time that the schedule takes effect. \
        Defaults to rotation_start
        end_time (str): Date and time that the schedule ends. Defaults to null
    """

    def __init__(self, users, rotation_start, rotation_turn_length,
                 restrictions, start_time=rotation_start, end_time=None,
                 name=None):
        self.start = start_time
        self.end = end_time
        self.users = users
        self.rotation_virtual_start = rotation_start
        self.rotation_turn_length_seconds = rotation_turn_length
        self.restrictions = restrictions
        if name is not None:
            self.name = name


class Schedule():
    """ Creates a new Schedule object

    Attributes:
        name (str): Name of the schedule
        description (str): Description of the schedule
        layers (list): List of all layers to be added to this schedule
        time_zone (str): Time zone for the schedule. Default is UTC
    """

    def __init__(self, name, description, layers, time_zone="UTC"):
        self.name = name
        self.description = description
        self.schedule_layers = layers
        self.time_zone = time_zone
