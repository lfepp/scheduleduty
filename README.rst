ScheduleDuty
============

Import schedules from a CSV file. Currently supports weekly shift-based
schedules and standard rotation-based schedules.

Usage
-----

1. Create a CSV file with the following format depending upon your schedule
type:

   Weekly Shifts::

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

   Standard Rotation::

       user,layer,layer_name,rotation_type,shift_length,shift_type,handoff_day,handoff_time,restriction_start_day,restriction_start_time,restriction_end_date,restriction_end_time

   **user** (str): The name/email of the user

   **layer** (int): The schedule layer

   **layer_name** (str): The name of the layer

   **rotation_type** (str): The type of rotation. Can be one of daily, weekly,
   custom.

   **shift_length** (int): Length of the on-call shift in a ``custom`` rotation

   **shift_type** (str): The unit of measure for the ``shift_length``. Can be
   one of hours, days, weeks.

   **handoff_day** (str or int): The day of the week to handoff the on-call
   shift. Can be one of 0, 1, 2, 3, 4, 5, 6, monday, tuesday, wednesday,
   thursday, friday, saturday, sunday

   **handoff_time** (str):The time of day to handoff the shift (i.e. 08:00)

   **restriction_start_day** (str): Day of the week to start the restriction.
   Can be one of 0, 1, 2, 3, 4, 5, 6, monday, tuesday, wednesday, thursday,
   friday, saturday, sunday

   **restriction_start_time** (str): Time of day to start the restriction
   (i.e. 08:00)

   **restriction_end_date** (str): Day of the week to end the restriction. Can
   be one of 0, 1, 2, 3, 4, 5, 6, monday, tuesday, wednesday, thursday, friday,
   saturday, sunday

   **restriction_end_time** (str): Time of day to end the restriction
   (i.e. 17:00)

\2. Save all CSV files into one directory

3. If running from the command line, execute the ``import_schedules.py`` script with the command line arguments for
your schedule type:

   Weekly Shifts::

       ./scheduleduty/scheduleduty.py --schedule-type weekly_shifts --csv-dir examples/weekly_shifts --api-key EXAMPLE_TOKEN --base-name "Weekly Shifts" --level-name Level --multiple-name Multi --start-date 2017-01-01 --end-date 2017-02-01 --time-zone UTC --num-loops 1 --escalation-delay 30

   Standard Rotation::

       ./scheduleduty/scheduleduty.py --schedule-type standard_rotation --csv-dir examples/standard_rotation --api-key EXAMPLE_TOKEN --base-name "Standard Rotation" --start-date 2017-01-01 --end-date 2017-02-01 --time-zone UTC

\4. If importing into a script, use the ``execute`` function within the ``Import`` class to import your schedules:

    Weekly Shifts::

        from scheduleduty import scheduleduty
        importer = scheduleduty.Import("weekly_shifts","./examples/weekly_shifts","EXAMPLE_TOKEN","Weekly Shifts","Level","Multi","2017-01-01","2017-02-01","UTC",1,30)
        importer.execute()

    Standard Rotation::

        from scheduleduty import scheduleduty
        importer = scheduleduty.Import("standard_rotation","./examples/standard_rotation","EXAMPLE_TOKEN","Standard Rotation",None,None,"2017-01-01","2017-02-01","UTC",None,None)
        importer.execute()

Arguments
----------------------

``--schedule-type``: Type of schedule(s) being uploaded. Must be one of ``weekly_shifts``, ``standard_rotation``.

``--csv-dir``: Path to the directory housing all CSVs to import into PagerDuty. Required for all schedule types.

``--api-key``: PagerDuty v2 REST API token. Required for all schedule types.

``--base-name``: Name of the escalation policy or schedule being added as well as the base name for each schedule added to the escalation policy. Required for all schedule types.

``--level-name``: The base name for each new escalation policy level to be appended by the integer value of the level number. Required for ``weekly_shifts`` schedule type.

``--multiple-name``: The base name for each schedule on the same escalation policy level to be appended by the integer value of the schedule number. Required for ``weekly_shifts`` schedule type.

``--start-date``: ISO 8601 formatted start date for the schedule. Currently only support dates in YYYY-MM-DD format. Required for all schedule types.

``--end-date``: ISO 8601 formatted end date for the schedule. Currently only supports dates in YYYY-MM-DD format. Optional for all schedule types.

``--time-zone``: Time zone for this schedule. Must be one of the time zones from the IANA time zone database. Required for all schedule types.

``--num-loops``: The number of times to loop through the escalation policy. Required for ``weekly_shifts`` schedule type.

``--escalation-delay``: The number of minutes to wait before escalating the incident to the next level. Required for ``weekly_shifts`` schedule type.

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
