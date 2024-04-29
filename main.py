from genericpath import isfile
import os.path, re, os, json, pyautogui
from time import sleep
from xmlrpc.client import TRANSPORT_ERROR

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from subprocess import Popen, PIPE, STDOUT

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]

BIN = "/opt/cisco/secureclient/bin/vpn"


def authenticate():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def mark_as_read(creds):
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
        messages = results.get("messages", [])

        if not messages:
            # print("No new messages.")
            pass
        else:
            # print(f"Total messages: {len(messages)}")
            for message in messages[:10]:
                service.users().messages().modify(
                    userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}
                ).execute()

        print("Marked as read.")
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        # print(f"An error occurred: {error}")
        pass
    return None


def twofa_token(creds):
    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
        messages = results.get("messages", [])

        if not messages:
            # print("No new messages.")
            pass
        else:
            # print(f"Total messages: {len(messages)}")
            for message in messages[:10]:
                msg = service.users().messages().get(userId="me", id=message["id"]).execute()
                if (
                    "UNREAD" in msg["labelIds"]
                    and "INBOX" in msg["labelIds"]
                    and "HKU 2FA login".lower() in msg["snippet"].lower()
                ):
                    matches = re.findall(r"token\s+code\s+(\d+)", msg["snippet"], re.IGNORECASE)
                    if matches and len(matches[0]) == 6:
                        service.users().messages().modify(
                            userId="me", id=message["id"], body={"removeLabelIds": ["UNREAD"]}
                        ).execute()
                        return matches[0]
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        # print(f"An error occurred: {error}")
        pass
    return None


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    if not os.path.isfile("vpn_credentials.json"):
        return

    if not os.path.isfile(BIN):
        return

    with open("vpn_credentials.json") as f:
        vpn = json.load(f)

    sleep(5)
    pyautogui.write(vpn["username"])
    pyautogui.press("enter")

    pyautogui.write(vpn["password"])
    pyautogui.press("enter")

    creds = authenticate()
    mark_as_read(creds)

    cnt = 0
    while True:
        sleep(5)
        cnt += 1
        token = twofa_token(creds)
        if token:
            print(f"Token found: {token}")
            pyautogui.write(token)
            pyautogui.press("enter")
            break
        if cnt > 100:
            # print("Timeout. Exiting.")
            break


if __name__ == "__main__":
    main()
