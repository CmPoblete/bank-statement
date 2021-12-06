from uuid import uuid4
from datetime import datetime
from dateutil import parser

class MovementHelper:
    
    @staticmethod
    def create_movement(currency, raw_movement):

        recipient, sender, comment = MovementHelper.parse_sender_recipient(raw_movement)
        movement = {
            "id": uuid4(),
            "object": "movement",
            "amount": raw_movement["amount"] * (1 if raw_movement["type"] == "inbound" else -1),
            "post_date": MovementHelper.to_iso8601(raw_movement["accountable_date"]),
            "description": raw_movement["description"],
            "transaction_date": MovementHelper.to_iso8601(raw_movement["date"]) if "date" in raw_movement.keys() else None,
            "currency": currency,
            "reference_id": raw_movement["id"] if "id" in raw_movement.keys() else None,
            "type": MovementHelper.get_movement_type(raw_movement),
            "pending": False,
            "recipient_account": recipient,
            "sender_account": sender,
            "comment": comment

        }
        return movement
    
    @staticmethod
    def make_movement_key(raw_movement, count=0):
        try:
            if raw_movement["id"] is not None:
                return raw_movement["id"]
            return f'{raw_movement["amount"]}-{raw_movement["type"][0]}-{count}'
        except KeyError:
            return f'{raw_movement["amount"]}-{raw_movement["type"][0]}-{count}'

    @staticmethod
    def key_from_date(string_date:str):
        date_object = parser.isoparse(string_date)
        return date_object.strftime("%Y-%m-%d")
    
    @staticmethod
    def check_completed_date(fetched_date: str, movement_date: str):
        fetched_at = parser.isoparse(fetched_date).date()
        movement_date = datetime.strptime(movement_date, "%Y-%m-%d").date()
        return movement_date < fetched_at
    
    @staticmethod
    def compare_isodate(date_1: str, date_2: str):
        first_date = parser.isoparse(date_1)
        second_date = parser.isoparse(date_2)
        return -1 if first_date < second_date else 0 if first_date == second_date else 1
    
    @staticmethod
    def to_iso8601(date: str) -> str:
        if date is None:
            return date
        date_obj = parser.isoparse(date)
        return date_obj.strftime("%Y-%m-%dT%H:%M:%H.%fZ")
    
    @staticmethod
    def get_movement_type(raw_movement) -> str:
        if "comment" in raw_movement["movement_meta"].keys():
            return "transfer"
        elif raw_movement["movement_meta"] == {} and raw_movement["document_number"] == "0000000000":
            return "check"
        return "other"
    
    @staticmethod
    def parse_sender_recipient(raw_movement):
        movement_meta = raw_movement["movement_meta"]
        recipient = None
        sender = None
        comment = movement_meta["comment"] if "comment" in movement_meta.keys() else None
        if "recipient_account" in movement_meta.keys():
            recipient = {
                "holder_id": movement_meta["recipient_rut"],
                "holder_name": movement_meta["recipient_name"] if "recipient_name" in movement_meta.keys() else None,
                "number": movement_meta["recipient_account"],
                "institution": {
                    "id": movement_meta["recipient_bank"],
                    "name": movement_meta["recipient_bank_raw_name"],
                    "country": movement_meta["recipient_bank"].split("_")[0]
                }
            }
        elif "sender_account" in movement_meta.keys():
            sender = {
                "holder_id": movement_meta["sender_rut"],
                "holder_name": movement_meta["sender_name"] if "sender_name" in movement_meta.keys() else None,
                "number": movement_meta["sender_account"],
                "institution": {
                    "id": movement_meta["sender_bank"],
                    "name": movement_meta["sender_bank_raw_name"],
                    "country": movement_meta["sender_bank"].split("_")[0]
                }
            }

        return recipient, sender, comment
