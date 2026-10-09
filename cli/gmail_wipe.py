"""Delete ALL messages in a Gmail account (inbox, spam, trash, promotions, every label).

Usage:
    python gmail_wipe.py --dry-run     # only show how many messages would be deleted
    python gmail_wipe.py               # permanent delete (asks you to type your address to confirm)
    python gmail_wipe.py --trash       # move to Trash instead of permanent delete (recoverable 30 days)
"""
import argparse
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://mail.google.com/"]  # required for permanent delete
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDS_FILE = os.path.join(HERE, "credentials.json")
TOKEN_FILE = os.path.join(HERE, "token.json")


def get_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                sys.exit("credentials.json not found - see README.md step 1.")
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def list_ids(service, limit=1000, query=None):
    """Return up to `limit` message IDs from anywhere, including Spam and Trash."""
    ids, token = [], None
    while len(ids) < limit:
        resp = service.users().messages().list(
            userId="me", includeSpamTrash=True, maxResults=500, pageToken=token, q=query
        ).execute()
        ids += [m["id"] for m in resp.get("messages", [])]
        token = resp.get("nextPageToken")
        if not token:
            break
    return ids[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="count only, delete nothing")
    ap.add_argument("--trash", action="store_true", help="move to Trash instead of permanent delete")
    args = ap.parse_args()

    service = get_service()
    profile = service.users().getProfile(userId="me").execute()
    email, total = profile["emailAddress"], profile["messagesTotal"]
    print(f"Account: {email}\nMessages (all folders, incl. spam/trash): {total}")

    if args.dry_run:
        return
    if total == 0:
        print("Nothing to delete.")
        return

    action = "MOVE TO TRASH" if args.trash else "PERMANENTLY DELETE (cannot be undone)"
    print(f"\nAbout to {action} ALL {total} messages in {email}.")
    if input(f"Type the account address ({email}) to confirm: ").strip().lower() != email.lower():
        sys.exit("Address did not match. Aborted.")

    done = 0
    while True:
        ids = list_ids(service, query="-in:trash" if args.trash else None)
        if not ids:
            break
        if args.trash:
            service.users().messages().batchModify(
                userId="me", body={"ids": ids, "addLabelIds": ["TRASH"], "removeLabelIds": ["INBOX"]}
            ).execute()
        else:
            service.users().messages().batchDelete(userId="me", body={"ids": ids}).execute()
        done += len(ids)
        print(f"Processed {done}")
    print("Done.")


if __name__ == "__main__":
    main()
