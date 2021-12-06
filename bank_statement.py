from datetime import datetime
import itertools
from movement_helper import MovementHelper

class BankStatement:

    def __init__(self) -> None:
        self.dates = {}
        self.movements_order = {}
        self._currency = None
    
    def update(self, snapshot):
        dates = []
        self._currency = snapshot["currency"].upper()
        for raw_movement in snapshot["movements"]:
            movement_date_obj, movement_date = self._get_or_create_movement_date(raw_movement) # Create key for the post date if doesn´t exists
            if movement_date_obj["completed"]:
                continue
    
            self._check_or_create_movement(raw_movement, movement_date, snapshot["fetched_at"]) # create movement if doesnt exists
            dates.append(movement_date)
        
        self._mark_date_as_completed(dates, snapshot["fetched_at"])
    
    def show_movements(self):
        dates = sorted(self.dates.keys(), key=lambda date_s: datetime.strptime(date_s, "%Y-%m-%d"))
        for date in dates:
            # movements = self.dates[date]["movements"]
            # sorted_movements = sorted(movements.values(), key=lambda mv: datetime.fromisoformat(mv["accountable_date"].strip("Z")))
            # for movement in sorted_movements:
            #     income_outcome = 1 if movement["type"] == "inbound" else -1
            #     print(f'{movement["accountable_date"]} | {income_outcome * movement["amount"]} | {movement["description"]}')

            for movement_key in self.movements_order[date]:
                movement = self.dates[date]["movements"][movement_key]
                print(f'{movement["post_date"]} | {movement["amount"]} | {movement["description"]}')

    def _get_or_create_movement_date(self, movement):
        date_to_check = MovementHelper.key_from_date(movement["accountable_date"])

        if date_to_check not in self.dates.keys():
            self.dates[date_to_check] = {
                "movements": {},
                "completed": False
            }
        return self.dates[date_to_check], date_to_check
    
    def _check_or_create_movement(self, raw_movement, movement_date, fetched_at):
        movements = self.dates[movement_date]["movements"]
        movement_key = MovementHelper.make_movement_key(raw_movement)
        try:
            for count in itertools.count():
                last_updated = movements[movement_key]["last_update"]
                if last_updated != fetched_at:
                    movements[movement_key]["last_update"] = fetched_at
                    break
                movement_key = MovementHelper.make_movement_key(raw_movement, count+1)
        except KeyError:
            movements[movement_key] = MovementHelper.create_movement(self._currency, raw_movement)
            movements[movement_key]["last_update"] = fetched_at
            self._create_or_insert_movement_key(movement_key, raw_movement, movement_date)
    
    def _mark_date_as_completed(self, dates, fetched_date: str):

        for date in dates:
            if MovementHelper.check_completed_date(fetched_date, date):
                self.dates[date]["completed"] = True

    def _create_or_insert_movement_key(self, movement_key, raw_movement, movement_date):
        try:
            movements = self.dates[movement_date]["movements"]
            for mv_index in range(len(self.movements_order[movement_date])):
                movement_key_in_order = self.movements_order[movement_date][mv_index]
                date_comparison = MovementHelper.compare_isodate(raw_movement["accountable_date"], movements[movement_key_in_order]["post_date"])
                if date_comparison == -1:
                    self.movements_order[movement_date].insert(mv_index, movement_key)
                    break
                elif date_comparison == 0:
                    self.movements_order[movement_date].insert(mv_index + 1, movement_key)
                    break
        except KeyError:
            self.movements_order[movement_date] = [movement_key]
