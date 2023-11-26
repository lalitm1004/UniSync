import datetime
import os
import pandas
import pytz
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathlib import Path

# Google Imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Selenium Imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()

CLIENT_SECRET_PATH = str(Path("secrets/client_secret.json"))
TOKEN_PATH = str(Path("secrets/token.json"))


def get_calendar_service():
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())

    calendar_service = build("calendar", "v3", credentials=creds)
    return calendar_service


def login() -> None:
    LOGIN_URL = "https://prodweb.snu.in/psp/CSPROD/EMPLOYEE/HRMS/?cmd=login"
    driver.get(LOGIN_URL)
    netid = driver.find_element(By.ID, "userid")
    password = driver.find_element(By.ID, "pwd")
    login = driver.find_element(By.CLASS_NAME, "psloginbutton")

    netid.clear()
    netid.send_keys(os.getenv("NETID"))
    password.clear()
    password.send_keys(os.getenv("PASSWORD"))
    login.click()


def grab_html_data():
    """
    Code written by
    1. Pustak Pathak - https://github.com/PustakP
    """
    login()
    url = "https://prodweb.snu.in/psp/CSPROD/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_SCHD_W"  # Replace with the desired URL

    # Initialize a Selenium WebDriver (make sure you have the corresponding browser driver installed)
    driver.get(url)

    # Detects when user logs in and closes browser after grabbing relevant html data
    iframe_locator = (By.ID, "ptifrmtgtframe")
    wait = WebDriverWait(driver, 60)
    try:
        iframe = wait.until(EC.presence_of_element_located(iframe_locator))
        iframe_src = iframe.get_attribute("src")
    except:
        print("Timeout.")

    # Open the iframe source URL
    driver.get(iframe_src)
    iframe_html_content = driver.page_source

    driver.quit()
    return iframe_html_content


def parse_html_data(html_data):
    soup = BeautifulSoup(html_data, "html.parser")

    element = soup.find("table", id="WEEKLY_SCHED_HTMLAREA")

    table = pandas.read_html(str(element.prettify()))[0]

    raw_schedule = {
        0: table[table.columns[1]].tolist(),
        1: table[table.columns[2]].tolist(),
        2: table[table.columns[3]].tolist(),
        3: table[table.columns[4]].tolist(),
        4: table[table.columns[5]].tolist(),
        5: table[table.columns[6]].tolist(),
        6: table[table.columns[7]].tolist(),
    }

    formatted_schedule = {}
    for i in range(0, 7):
        unique_list = []
        for element in raw_schedule[i]:
            if (
                element not in unique_list  # Check for duplicates
                and not element != element  # Check for NaN
                and not element.count("Floor") > 1
                and not element.count("Block") > 1
            ):
                unique_list.append(element)

        for index, element in enumerate(unique_list):
            unique_list[index] = [
                i
                for i in element.split(" ")
                if i
                not in [
                    "",
                    "-",
                    "Floor",
                    "Block",
                    "G.",
                    "F.",
                    "S.",
                    "T.",
                    "A",
                    "B",
                    "C",
                    "D",
                ]
            ]

        formatted_schedule[i] = unique_list

    for i in range(0, 7):
        day_schedule = formatted_schedule[i]
        for index, element in enumerate(day_schedule):
            _class_data = {
                "class_code": element[1],
                "class_type": element[2],
                "start_timing": element[4],
                "end_timing": element[5],
                "venue": element[6],
            }
            day_schedule[index] = _class_data
        formatted_schedule[i] = day_schedule

    return formatted_schedule


def fetch_week_timestamps() -> tuple:
    current_datetime_kolkata = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    start_of_week = current_datetime_kolkata - datetime.timedelta(
        days=current_datetime_kolkata.weekday() + 1,
        hours=current_datetime_kolkata.hour,
        minutes=current_datetime_kolkata.minute,
        seconds=current_datetime_kolkata.second,
    )
    end_of_week = start_of_week + datetime.timedelta(
        days=6, hours=23, minutes=59, seconds=59
    )

    # Convert the start and end of the week to RFC3339 timestamps
    start_of_week_rfc3339 = start_of_week.isoformat()
    end_of_week_rfc3339 = end_of_week.isoformat()

    return (start_of_week_rfc3339, end_of_week_rfc3339)


def main():
    calendar_service = get_calendar_service()

    # Create SNU.Schedule calendar if it doesnt exist already
    snu_calendar = None
    page_token = None
    while True:
        calendars = calendar_service.calendarList().list(pageToken=page_token).execute()
        for calendar in calendars["items"]:
            snu_calendar = calendar if calendar["summary"] == "SNU.Schedule" else None
        page_token = calendars.get("nextPageToken")
        if not page_token:
            break

    if not snu_calendar:
        request_body = {"summary": "SNU.Schedule", "timezone": "Asia/Kolkata"}
        snu_calendar = calendar_service.calendars().insert(body=request_body).execute()
        # Access calendar id -> snu_calendar["id"]
    html_data = grab_html_data()
    schedule_data = parse_html_data(html_data=html_data)

    week_timings = fetch_week_timestamps()

    calendar_events = []
    page_token = None
    while True:
        events = (
            calendar_service.events()
            .list(
                calendarId=snu_calendar["id"],
                timeMin=week_timings[0],
                timeMax=week_timings[1],
                pageToken=page_token,
            )
            .execute()
        )
        for event in events["items"]:
            calendar_events.append(event)
        page_token = events.get("nextPageToken")

        if not page_token:
            break

    for event in calendar_events:
        calendar_service.events().delete(
            calendarId=snu_calendar["id"], eventId=event["id"]
        ).execute()

    for day, events_list in schedule_data.items():
        for event_details in events_list:
            event_title = (
                f"{event_details['class_code']} - {event_details['class_type']}"
            )
            event_location = event_details["venue"]

            # Parse start and end timings
            day_offset = datetime.timedelta(
                days=1 * (day - datetime.datetime.now().weekday())
            )

            start_time = datetime.datetime.strptime(
                event_details["start_timing"], "%I:%M%p"
            )
            end_time = datetime.datetime.strptime(
                event_details["end_timing"], "%I:%M%p"
            )
            monday = datetime.datetime.now() + day_offset
            start_day_time = monday.replace(
                hour=start_time.hour, minute=start_time.minute
            )
            end_day_time = monday.replace(hour=end_time.hour, minute=end_time.minute)

            # Create an event
            event = {
                "summary": event_title,
                "location": event_location,
                "start": {
                    "dateTime": start_day_time.isoformat(),
                    "timeZone": "Asia/Calcutta",
                },
                "end": {
                    "dateTime": end_day_time.isoformat(),
                    "timeZone": "Asia/Calcutta",
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 15},
                        {"method": "popup", "minutes": 30},
                    ],
                },
            }

            # Insert event to Google Calendar
            calendar_service.events().insert(
                calendarId=snu_calendar["id"], body=event
            ).execute()


if __name__ == "__main__":
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)
    main()
