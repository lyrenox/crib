import os

from pymongo import MongoClient


global client
client = MongoClient(os.environ('ATLAS_HOST'))
db = client.database

class UserEntry:
    def __init__(self, server_id: str, donor_id: int = None):
        self.col = db[server_id]
        self.id = donor_id

    def set_amount(self, amount:int):
        query = {"user_id": self.id}
        value = {"user_id": self.id, "amount": amount, "donations": 0}
        self.col.replace_one(query, value, upsert=True)
        print(f"Replace data for user {self.id}")

    def update_amount(self, amount:int):
        query = {"user_id": self.id}
        doc = self.col.find_one(query)

        if doc is None:
            new_value = {"user_id": self.id, "amount": amount, "donations": 1}
            self.col.insert_one(new_value)
            print(f"Created new data for user {self.id}")
        else:
            new_amount = self.col.find_one({"user_id": self.id})["amount"] + amount
            new_donations = self.col.find_one({"user_id": self.id})["donations"] + 1 if amount > 0 else -1
            new_value = {"$set": {"amount": new_amount, "donations": new_donations}}
            self.col.update_one(query, new_value)
            print(f"Updated data for user {self.id}")

    def fetch(self):
        query = {"user_id": self.id}
        doc = self.col.find_one(query)
        return doc

    def sort(self):
        doc = self.col.find().sort("amount", -1)
        return [i for i in doc]

