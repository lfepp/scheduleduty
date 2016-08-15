# Import Schedules

Import schedules from a CSV file. Currently only supports weekly shift-based schedules.

## Usage

1. Create a CSV file with the following format for each schedule:

    ```
    escalation_level,user_or_team,type,day_of_week,start_time,end_time
    ```

    **escalation_level** (int): Level to place user/team on the escalation policy

    **user_or_team** (str): The name/email of the user/team

    **type** (str): Must be one of user, team

    **day_of_week** (str or int): Must be one of 0, 1, 2, 3, 4, 5, 6, sunday, monday, tuesday, wednesday, thursday, friday, saturday, weekday, weekdays, weekend, weekends

    **start_time** (str): Start time of the shift for that day (i.e. 13:00)

    **end_time** (str): End time of the shift for that day (i.e. 21:00)

1. Save the CSV files into the `src/csv` directory

1. Run the `import_schedules.py` script:

    ```
    ./src/import_schedules.py --api-key EXAMPLE_KEY --base-name "Weekly Shifts" --level-name Level --multiple-name Multi
    ```

## Command Line Arguments

`--api-key`: PagerDuty v2 API token

`--base-name`: The base name for the escalation policy and schedules

`--layer-name`: The base name for each new escalation policy level to be appended by the integer value of the level number

`--multiple-name`: The base name for each schedule on the same escalation policy level to be appended by the integer value of the schedule number

## Testing

1. Create a file `config.json` that includes your command-line arguments for testing:

    ```
    {
      "api_key": "EXAMPLE_KEY",
      "base_name": "Weekly Shifts",
      "level_name": "Level",
      "multi_name": "Multi"
    }
    ```

1. Save `config.json` within the `tests` directory

1. Run the test suite in `test_suite.py`:

    ```
    python tests/test_suite.py
    ```

## Author

Luke Epp <lucasfepp@gmail.com>
