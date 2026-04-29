import requests
import os
import uuid
import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

class InstantDB:
    def __init__(self):
        self.app_id = os.getenv("INSTANTDB_APP_ID")
        self.admin_token = os.getenv("INSTANTDB_ADMIN_TOKEN")
        self.base_url = "https://api.instantdb.com/admin"
        self.headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "App-Id": self.app_id,
            "Content-Type": "application/json"
        }

    def transact(self, steps):
        """
        Executes a transaction. Steps is a list of [op, namespace, id, data]
        """
        payload = {"steps": steps}
        response = requests.post(f"{self.base_url}/transact", headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Transaction failed ({response.status_code}): {response.text}")
        return response.json()

    def query(self, query_obj):
        """
        Executes a query.
        """
        payload = {"query": query_obj}
        response = requests.post(f"{self.base_url}/query", headers=self.headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Query failed ({response.status_code}): {response.text}")
        try:
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to decode JSON response: {response.text}")

    # Helper methods
    def get_user_by_email(self, email):
        q = {
            "users": {
                "$": {
                    "where": {"email": email}
                }
            }
        }
        res = self.query(q)
        users = res.get("users", [])
        return users[0] if users else None

    def create_user(self, username, email, password_hash):
        user_id = str(uuid.uuid4())
        steps = [
            ["update", "users", user_id, {
                "username": username,
                "email": email,
                "password_hash": password_hash
            }]
        ]
        self.transact(steps)
        return user_id

    def save_summary(self, user_id, original_text, summary_text):
        summary_id = str(uuid.uuid4())
        steps = [
            ["update", "summaries", summary_id, {
                "user_id": user_id,
                "original_text": original_text,
                "summary_text": summary_text,
                "created_at": datetime.datetime.now().isoformat()
            }]
        ]
        self.transact(steps)
        return summary_id

    def delete_summary(self, summary_id):
        steps = [
            ["delete", "summaries", summary_id]
        ]
        self.transact(steps)
        return True

    def get_user_history(self, user_id):
        q = {
            "summaries": {
                "$": {
                    "where": {"user_id": user_id}
                }
            }
        }
        res = self.query(q)
        summaries = res.get("summaries", [])
        # Sort by created_at descending
        return sorted(summaries, key=lambda x: x.get("created_at", ""), reverse=True)
