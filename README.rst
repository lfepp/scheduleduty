ScheduleDuty
============

Import schedules from a CSV file. Currently only supports weekly
shift-based schedules.

Usage
-----

1. Create a CSV file with the following format for each schedule:

   ::

       escalation_level,user_or_team,type,day_of_week,start_time,end_time

   **escalation\_level** (int): Level to place user/team on the
   escalation policy

   **user\_or\_team** (str): The name/email of the user/team

   **type** (str): Must be one of user, team

   **day\_of\_week** (str or int): Must be one of 0, 1, 2, 3, 4, 5, 6,
   sunday, monday, tuesday, wednesday, thursday, friday, saturday,
   weekday, weekdays, weekend, weekends, all

   **start\_time** (str): Start time of the shift for that day
   (i.e. 13:00)

   **end\_time** (str): End time of the shift for that day (i.e. 21:00)

2. Save all CSV files into one directory

3. Run the ``import_schedules.py`` script:

   ::

       ./scheduleduty/scheduleduty.py --csv-dir examples/weekly_shifts --api-key EXAMPLE_KEY --base-name "Weekly Shifts" --level-name Level --multiple-name Multi --start-date 2017-01-01 --end-date 2017-02-01 --time-zone UTC --num-loops 1 --escalation-delay 30

Command Line Arguments
----------------------

``--csv-dir``: Path to the directory housing all CSVs to import into PagerDuty

``--api-key``: PagerDuty v2 API token

``--base-name``: The base name for the escalation policy and schedules

``--level-name``: The base name for each new escalation policy level to
be appended by the integer value of the level number

``--multiple-name``: The base name for each schedule on the same
escalation policy level to be appended by the integer value of the
schedule number

``--start-date``: The start date for the schedule to begin in the format
YYYY-MM-DD

``--end-date`` *(optional)*: The end date for the schedule to end in the
format YYYY-MM-DD

``--time-zone``: The time zone for the schedule in the format of an
option from the `IANA time zone database`_

``--num-loops``: The number of times the escalation policy will repeat
after reaching the end of escalation

``--escalation-delay``: The number of minutes to wait before escalating
the incident to the next level

Testing
-------

1. Create a file ``config.json`` that includes your command-line
   arguments for testing:

   ::

       {
         "api_key": "EXAMPLE_KEY",
         "base_name": "Weekly Shifts",
         "level_name": "Level",
         "multi_name": "Multi",
         "start_date": "2017-01-01",
         "end_date": null,
         "time_zone": "UTC",
         "num_loops": 1,
         "escalation_delay": 30
       }

2. Save ``config.json`` within the ``tests`` directory

3. Run the test suite in ``test_suite.py``:

   ::

       python tests/test_suite.py

Author
------

Luke Epp lucas@pagerduty.com

.. _IANA time zone database: https://www.iana.org/time-zones
