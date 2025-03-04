# main.py

import datetime
import threading
import time

from modules import gemini_parser, email_sender, stock_fetcher, calendar_invite

# Your Gmail credentials to be used for sending emails.
EMAIL_SENDER = "example@gmail.com"
EMAIL_PASSWORD = "16 digit app password here"


def dispatch_task(task: dict):
    """
    Execute a single task based on its type.

    This function is called by a timer when a scheduled task is due. It examines the 'task_type' field in the 
    provided task dictionary and performs the corresponding action:
      - For "email_reminder", it sends an email reminder.
      - For "stock_price", it fetches the current stock price and sends an email with the update.
      - For "calendar_invite", it creates a calendar event using the provided event details.
      - For unknown task types, it prints an error message.

    Args:
        task (dict): A dictionary representing a task. The dictionary should include:
                     - "task_type" (str): The type of task ("email_reminder", "stock_price", "calendar_invite").
                     - Other keys such as "email", "subject", "message", "stock_symbol", or "event" depending on the task.

    Returns:
        None

    Example:
        >>> task = {
        ...     "task_type": "email_reminder",
        ...     "email": "user@example.com",
        ...     "subject": "Meeting Reminder",
        ...     "message": "Don't forget the meeting at 3 PM."
        ... }
        >>> dispatch_task(task)
    """
    task_type = task.get("task_type")
    print(f"[DISPATCH] Executing task: {task}")

    if task_type == "email_reminder":
        # Use sender email if the parsed email is "unknown" or missing.
        email = task.get("email", EMAIL_SENDER)
        if email.lower() == "unknown":
            email = EMAIL_SENDER
        subject = task.get("subject", "Reminder")
        message = task.get("message", "")
        email_sender.send_email(EMAIL_SENDER, EMAIL_PASSWORD, email, subject, message)

    elif task_type == "stock_price":
        # For stock price tasks, fetch the stock price and email the result.
        ticker = task.get("stock_symbol", "AAPL")
        price = stock_fetcher.get_stock_price(ticker)
        subject = task.get("subject", f"Stock Price Update for {ticker}")
        message = f"The current price for {ticker} is {price}"
        email = task.get("email", EMAIL_SENDER)
        if email.lower() == "unknown":
            email = EMAIL_SENDER
        email_sender.send_email(EMAIL_SENDER, EMAIL_PASSWORD, email, subject, message)

    elif task_type == "calendar_invite":
        # For calendar invites, format event details and create the invite.
        event_details = task.get("event")
        if event_details:
            # If event_details "start" and "end" times are strings, convert them to the structure required by the API.
            if isinstance(event_details.get("start"), str):
                event_details = {
                    "summary": event_details.get("summary", "Meeting"),
                    "start": {
                        "dateTime": event_details.get("start"),
                        "timeZone": "America/Los_Angeles"
                    },
                    "end": {
                        "dateTime": event_details.get("end"),
                        "timeZone": "America/Los_Angeles"
                    }
                }
            calendar_invite.create_calendar_invite(event_details)
        else:
            print("[DISPATCH] No event details provided for calendar_invite.")
    else:
        print(f"[DISPATCH] Unknown task type: {task_type}")


def schedule_task(task: dict):
    """
    Schedule a one-off task to be executed at its designated time.

    This function calculates the delay until the task should be executed based on the provided time in the task.
    The task time can be provided as an ISO format string (e.g., "2025-03-15T16:19:00") or as a "HH:MM" string,
    in which case it assumes the task is scheduled for today. If the computed delay is negative (i.e., the time has 
    already passed), the task is executed immediately. For "calendar_invite" tasks, the delay is set to 0.

    Args:
        task (dict): A dictionary representing a task. It must contain:
                     - "time" (str): The scheduled time for the task execution, either in ISO format or "HH:MM".
                     - "task_type" (str): The type of task to be scheduled.

    Returns:
        None

    Example:
        >>> task = {
        ...     "task_type": "email_reminder",
        ...     "time": "17:00",
        ...     "email": "user@example.com",
        ...     "subject": "Meeting Reminder",
        ...     "message": "Don't forget the meeting at 3 PM."
        ... }
        >>> schedule_task(task)
    """
    task_time_str = task.get("time", "")
    now = datetime.datetime.now()

    try:
        if "T" in task_time_str:
            # If the time string is in ISO format, convert it directly.
            scheduled_time = datetime.datetime.fromisoformat(task_time_str)
        else:
            # If the time string is in "HH:MM" format, combine it with today's date.
            today = now.date()
            scheduled_time = datetime.datetime.strptime(f"{today} {task_time_str}", "%Y-%m-%d %H:%M")
    except Exception as e:
        print(f"[SCHEDULER] Error parsing time '{task_time_str}': {e}")
        dispatch_task(task)
        return

    # Calculate delay in seconds until the scheduled time.
    delay = (scheduled_time - now).total_seconds()

    # For calendar_invite tasks, execute immediately.
    if task.get("task_type") == "calendar_invite":
        delay = 0

    if delay < 0:
        delay = 0  # If the scheduled time is in the past, execute immediately.

    print(f"[SCHEDULER] Scheduling '{task.get('task_type')}' in {delay:.2f} seconds (at {scheduled_time})")
    threading.Timer(delay, dispatch_task, args=[task]).start()


def main():
    """
    Main function to execute the task scheduling workflow.

    This function performs the following steps:
      1. Reads the raw tasks from the "todo.txt" file.
      2. Uses the Gemini parser to convert the raw task text into a structured list of task dictionaries.
      3. Schedules each task based on its specified execution time using schedule_task().
      4. Keeps the main thread alive so that scheduled tasks can run, until interrupted by the user.

    Returns:
        None

    Detailed Workflow:
      - The function opens "todo.txt" to read the task instructions.
      - It calls gemini_parser.parse_tasks() to process the instructions into a list of tasks.
      - It optionally prints the parsed tasks using gemini_parser.pretty_print_tasks() for debugging.
      - It then iterates over the list of tasks and schedules each one by calling schedule_task().
      - Finally, it enters an infinite loop, sleeping for 60 seconds at a time, so that the program continues running.
      - The loop can be exited gracefully with a KeyboardInterrupt (Ctrl+C).

    Example:
        >>> python3 main.py
    """
    # 1. Read the raw tasks from file "todo.txt"
    with open("todo.txt", "r") as f:
        tasks_text = f.read()

    # 2. Parse tasks using Gemini parser to get a structured list of tasks
    tasks = gemini_parser.parse_tasks(tasks_text)
    gemini_parser.pretty_print_tasks(tasks)  # Optional: print parsed tasks for debugging

    # 3. Schedule each task based on its designated execution time
    for task in tasks:
        schedule_task(task)

    # 4. Keep the main thread alive so that scheduled tasks can execute
    print("[MAIN] Running. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("[MAIN] Shutting down scheduler.")


if __name__ == "__main__":
    main()
