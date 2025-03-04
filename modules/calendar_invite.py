# modules/calendar_invite.py

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Define the scopes required to manage calendar events.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_credentials():
    """
    Retrieve and return valid user credentials for accessing the Google Calendar API.

    This function performs the following steps:
      1. Checks if a 'token.pickle' file exists. If it does, it loads the stored credentials.
      2. Validates the credentials; if they are invalid or expired, it attempts to refresh them.
      3. If the credentials cannot be refreshed or do not exist, it initiates an OAuth2 flow using
         the client secrets file to obtain new credentials.
      4. Saves the newly obtained credentials to 'token.pickle' for future use.

    Returns:
        google.auth.credentials.Credentials: A credentials object that can be used to authorize
        API requests to the Google Calendar API.

    Example:
        >>> creds = get_credentials()
        >>> print(creds)
    """
    creds = None
    # Check for stored credentials in 'token.pickle'
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials are available, initiate an OAuth2 flow.
    if not creds or not creds.valid:
        # If credentials exist and are expired, refresh them.
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Start OAuth2 flow using the client secrets file.
            flow = InstalledAppFlow.from_client_secrets_file(
                'path to your credentials .json file ',
                SCOPES
            )
            # Open a local server for the authentication process.
            creds = flow.run_local_server(port=0, host="127.0.0.1", open_browser=True)

        # Save the new credentials to 'token.pickle' for subsequent runs.
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def create_calendar_invite(event_details):
    """
    Create a new event in the primary Google Calendar using the provided event details.

    This function retrieves valid credentials by calling get_credentials(), builds the Google Calendar API
    service, and then inserts the event into the primary calendar. After the event is created, it prints
    a link to the event.

    Args:
        event_details (dict): A dictionary containing the details of the event. The dictionary should
                              include keys such as "summary" for the event title, and "start" and "end"
                              which are dictionaries with "dateTime" and "timeZone" keys.

    Returns:
        None

    Example:
        >>> event = {
        ...     "summary": "Team Meeting",
        ...     "start": {"dateTime": "2025-03-15T10:00:00", "timeZone": "America/Los_Angeles"},
        ...     "end": {"dateTime": "2025-03-15T11:00:00", "timeZone": "America/Los_Angeles"}
        ... }
        >>> create_calendar_invite(event)
    """
    # Obtain valid credentials for accessing the Calendar API.
    creds = get_credentials()
    # Build the Google Calendar API service using the retrieved credentials.
    service = build('calendar', 'v3', credentials=creds)
    
    # Insert the event into the primary calendar and execute the API request.
    event = service.events().insert(calendarId='primary', body=event_details).execute()
    # Print the link to the newly created event.
    print(f"Event created: {event.get('htmlLink')}")
