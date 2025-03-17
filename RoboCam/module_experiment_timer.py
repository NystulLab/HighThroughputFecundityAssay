"""
Module for setting how long to run experiment

TODO:
-Create sample loop like Arduino?
-Create sample loop using time.sleep?
- Display time left until next run and time left until experiment is done.

Changelog:
7-19-2022: Added in functions to create layout, check for digits, and to collect time values.
"""

import FreeSimpleGUI as sg
import time

DEFAULT_TOTAL_HOURS = "0"
DEFAULT_TOTAL_MIN = "3"
DEFAULT_RUN_MIN = "1"

TOTAL_HOURS_KEY = "-HOURS-"
TOTAL_MIN_KEY = "-MIN-"
RUN_MIN_KEY = "-RUN_MIN-"

TIME_KEY_LIST = [TOTAL_HOURS_KEY, TOTAL_MIN_KEY, RUN_MIN_KEY]


# Define function to check an InputText key for digits only
def check_for_digits_in_key(key_str, window, event, values):
    
    # TODO: Add in character check in all of number string.
    if event == key_str and len(values[key_str]) and values[key_str][-1] not in ('0123456789'):
            # delete last char from input
            # print("Found a letter instead of a number")
            window[key_str].update(values[key_str][:-1])


def get_time_layout():
    time_size = (3, 1)
    
    time_layout = [
                    [sg.Text("How long will I collect pictures?")],
                    [sg.Text("Hour(s):"), sg.InputText(DEFAULT_TOTAL_HOURS, size=time_size, enable_events=True, key=TOTAL_HOURS_KEY)],
                    [sg.Text("Min(s) : "), sg.InputText(DEFAULT_TOTAL_MIN, size=time_size, enable_events=True, key=TOTAL_MIN_KEY)],
                    [sg.Text("How long will I wait between each run?")],
                    [sg.Text("Min(s) : "), sg.InputText(DEFAULT_RUN_MIN, size=time_size, enable_events=True, key=RUN_MIN_KEY)]
                  ]
    return time_layout


def get_hour_min(event, values, window):
    # Assumes values found in the InputText are integers.
    # Demonstrates that the time values are collected.

    total_hours = int(values[TOTAL_HOURS_KEY])
    total_minutes = int(values[TOTAL_MIN_KEY])
    print(f"Experiment will run for {total_hours} hours and {total_minutes} minutes")
    
    # Convert to seconds for time.sleep()
    total_seconds = total_hours*60*60 + total_minutes*60
    print(f"or experiment will run for {total_seconds} seconds")

    run_minutes = int(values[RUN_MIN_KEY])
    run_seconds = run_minutes * 60
    print(f"After collecting data from wells, will wait {run_minutes} minutes (or {run_seconds} seconds) before collecting data again")

    # Dummy values for fasting code testing
    # total_seconds = 61
    # run_seconds = 10
    # demo_start_experiment_1(total_seconds, run_seconds)
    demo_start_experiment_2(total_seconds, run_seconds)


def demo_start_experiment_1(total_seconds, run_seconds):
    print("demo_start_experiment_1")
    # Practice function to practice
    # While loop using time.sleep to pause the script

    # demo location list init
    location_list = [1, 2, 3, 4]

    # Init start time variable
    start = time.monotonic()

    # Init location index to zero
    location_index = 0

    elapsed_seconds = -1

    counter = 0

    # While elapsed time is less than total time
    while elapsed_seconds < total_seconds:
        #  Go to location (print it out)
        print(f"Run #{counter}")
        for loc in location_list:
            print(loc)
            time.sleep(1)

        #  Get current time
        current_time = time.monotonic()

        #  Calculate elapsed time (current - start)
        elapsed_seconds = current_time - start

        print(f"elapsed_seconds: {elapsed_seconds:.2f}")

        # Display time left until end of experiment
        print(f"Time left until end of experiment: {(total_seconds - elapsed_seconds):.1f} sec")

        # if location_index >= len(location_list):
        #     location_index = 0
            # break  # temp

        #  time.sleep and wait run_seconds

        # Note: Caused GUI to pause and you can't interact with it!
        #       May need threading, which is what my GUI does.

        # TODO: Figure out how to avoid putting this if statement here.
        # Check if sleeping will go over the time limit
        #   If it doesn't, sleep until next run
        #   If it does, time to break the loop
        if elapsed_seconds + run_seconds < total_seconds:
            print(f"Will wait {run_seconds} seconds until collecting data again")
            time.sleep(run_seconds)
        elif elapsed_seconds + run_seconds > total_seconds:
            print(f"Doing another run will go over set time limit, stopping experiment.")
            break

        counter += 1

    print("Done running experiment")

    #  iterate location index by one or reset to zero if hit end of list.


def demo_start_experiment_2(total_seconds, run_seconds):
    # While loop using time.monotonic to activate certain conditions the script

    # TODO: Display time left until end of experiment and time left until next run.
    print("demo_start_experiment_2")
    # Practice function to practice
    # While loop using time.sleep to pause the script

    # demo location list init
    location_list = [1, 2, 3, 4]

    # Init start time variable
    start = time.monotonic()
    run_start = time.monotonic()

    # Init location index to zero
    location_index = 0

    elapsed_seconds = -1
    run_time_left = 0
    run_elapsed = -1
    counter = 0

    # While elapsed time is less than total time
    while elapsed_seconds < total_seconds:

        # For testing, break after 3 runs
        # if counter >= 3:
        #     break

        if run_time_left <= 0:
            # Run experiment
            if counter > 0:
                print(f"Done Waiting {run_seconds} sec")

            print(f"Run #{counter}")
            for loc in location_list:
                print(loc)
                time.sleep(1)
            counter += 1

            # Reset run_time_left
            run_time_left = run_seconds

            # Reset run_start
            run_start = time.monotonic()

            print(f"Will wait {run_seconds} sec before doing next run.")

            # Display time left until end of experiment
            print(f"Time left until end of experiment: {(total_seconds - elapsed_seconds):.1f} sec")

        #  Get current time
        current_time = time.monotonic()

        #  Calculate elapsed time (current - start)
        elapsed_seconds = current_time - start
        run_elapsed = current_time - run_start
        run_time_left = run_seconds - run_elapsed

        # print(f"run_elapsed: {run_elapsed}")
        # print(f"run_time_left: {run_time_left}")

        # print(f"elapsed_seconds: {elapsed_seconds:.2f}")

    print("Done running experiment")


def demo_time_left():
    # Temp function for displaying time left every x seconds

    # Init start time
    start_time = time.monotonic()

    elapsed_time = 0

    total_seconds = 61  # sec
    # total_seconds = 3661  # sec

    when_to_display_time_left = 5   # sec

    # While loop that lasts for 30 seconds
    while elapsed_time < total_seconds:
        #  Get current time
        current_time = time.monotonic()

        #  Calculate elapsed time
        elapsed_time = current_time - start_time

        #  Calc time left
        time_left = total_seconds - elapsed_time
        # print(f"elapsed_time: {elapsed_time}")

        #  Convert time left to int, if mod 5 is 0, display time
        time_left_sec_int = int(time_left)
        time_left_min = time_left/60
        time_left_min_int = int(time_left_min)
        time_left_hours = time_left/(60*60)

        if (time_left_sec_int % when_to_display_time_left) == 0:
            #  every 5 seconds, display time left

            # TODO: Display hours and minutes left if minutes > 60
            if time_left_sec_int >= 60*60:
                # print(f"Hours left: {time_left_hours}")
                hours_left = int(time_left_hours)
                minutes_left = (time_left_hours % hours_left) * 60
                minutes_left_int = int(minutes_left)
                if minutes_left_int != 0:
                    seconds_left = int((minutes_left % minutes_left_int) * 60)
                    print(f"time left: {hours_left} hour(s), {minutes_left_int} minute(s), and {seconds_left} second(s).")
                else:
                    seconds_left = int(minutes_left * 60)
                    print(f"time left: {hours_left} hour(s), {seconds_left} second(s).")
                    # print(f"minutes_left: {minutes_left}")
                # print(f"After decimal: {time_left_min % time_left_min_int}")
                # print(f"time_left: {time_left_min} minutes")
                # print(f"time_left: {minutes_left} minutes and {seconds_left} seconds")
                # print(f"time left: {hours_left} hour(s) and {minutes_left_int} minute(s).")

            # TODO: Display minutes left if seconds > 60.
            elif time_left_sec_int > 60:
                minutes_left = int(time_left_min)
                seconds_left = int((time_left_min % time_left_min_int) * 60)
                # print(f"After decimal: {time_left_min % time_left_min_int}")
                # print(f"time_left: {time_left_min} minutes")
                print(f"time_left: {minutes_left} minutes and {seconds_left} seconds")

            # Display seconds left if 60 seconds are left
            elif time_left_sec_int <= 60:
                print(f"time_left: {time_left_sec_int} second(s)")

            # print(f"time_left: {time_left_sec_int} seconds")
            # Figure out way to remove sleep
            time.sleep(1)

            # Since sleeping for 1 second, update current and elapsed time.
            current_time = time.monotonic()
            elapsed_time = current_time - start_time
            # print(f"elapsed_time: {elapsed_time:.2f} sec")
    print("Out of while loop")





    pass


def main2():
    demo_time_left()


def main():
    print("main")
    
    # Set up theme
    sg.theme("LightGreen")
    
    time_size = (3, 1)
    
    # Set up layout
    layout = [
                get_time_layout(),
                [sg.Button("Start")]
             ]
    
    # Set up window
    window = sg.Window("Time GUI", layout)
    
    # While loop for GUI
    while True:
        event, values = window.read()
        
        for time_key in TIME_KEY_LIST:
            check_for_digits_in_key(time_key, window, event, values)
        
        if event == sg.WIN_CLOSED:
            break
        elif event == "Start":
            print("Pressed Start")
            get_hour_min(event, values, window)
    
    pass


if __name__ == "__main__":
    # main()
    main2()
