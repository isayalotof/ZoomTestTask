import requests
import json
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
import os

class ZoomClient:
    def __init__(self, account_id, client_id, client_secret):
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = self.get_access_token()

    def get_access_token(self):
        data = {
            "grant_type": "account_credentials",
            "account_id": self.account_id,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post("https://zoom.us/oauth/token", data=data, headers=headers)
        response.raise_for_status()
        return response.json().get('access_token')

    def create_meeting(self, topic, start_time, duration):
        url = f"https://api.zoom.us/v2/users/me/meetings"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "topic": topic,
            "type": 2,  # Scheduled meeting
            "start_time": start_time.isoformat(),
            "duration": duration,
            "timezone": "UTC"
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        meeting_data = response.json()

        # Save meeting data to a file
        with open('meeting_info.json', 'w') as file:
            json.dump({
                "meeting_id": meeting_data['id'],
                "join_url": meeting_data['join_url'],
                "start_time": meeting_data['start_time']
            }, file, indent=4)

        print("Meeting created and details saved to 'meeting_info.json'")
        return meeting_data

    def get_past_meetings(self):
        url = f"https://api.zoom.us/v2/users/me/meetings"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        # Calculate the start date for the last 7 days
        end_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        start_date = (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ')

        params = {
            "type": "past",  # Only fetch past meetings
            "from": start_date,
            "to": end_date
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        meetings = response.json().get('meetings', [])

        if not meetings:
            print("No past meetings found. Creating a test meeting.")
            # Create a test meeting if none exist
            self.create_meeting("Test Meeting", datetime.now(timezone.utc) + timedelta(minutes=10), 30)
            return self.get_past_meetings()

        # Print details of each past meeting
        for meeting in meetings:
            print(f"Meeting Topic: {meeting['topic']}")
            print(f"Start Time: {meeting['start_time']}")
            # Check if 'participants_count' is present
            participants_count = meeting.get('participants_count', 'N/A')
            print(f"Participants: {participants_count}")

        return meetings


# Example usage
if __name__ == "__main__":
    load_dotenv()
    data_zoom = {
        "account_id": os.environ.get('ZOOM_ACCOUNT_ID'),
        "client_id": os.environ.get('ZOOM_CLIENT_ID'),
        "client_secret": os.environ.get('ZOOM_CLIENT_SECRET'),
    }
    zoom_client = ZoomClient(
        data_zoom['account_id'],
        data_zoom['client_id'],
        data_zoom['client_secret']
    )

    # Create a new meeting
    new_meeting = zoom_client.create_meeting(
        topic="Important Meeting",
        start_time=datetime.now(timezone.utc) + timedelta(days=1),  # Schedule for the next day
        duration=60  # 1 hour
    )

    # Get past meetings in the last 7 days
    past_meetings = zoom_client.get_past_meetings()
