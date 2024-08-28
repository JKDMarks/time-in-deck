import sys, json, datetime
from typing import TypedDict

from fetch_deck_history import Card


class CardTime(TypedDict):
    currently_in_deck: bool
    last_update: datetime.datetime
    total_time_in_deck: datetime.timedelta


def convert_timestring(timestring):
    if "." in timestring:
        return datetime.datetime.strptime(timestring, f"%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        return datetime.datetime.strptime(timestring, f"%Y-%m-%dT%H:%M:%SZ")


def run(deck_history, filename):
    deck_history: list[Card] = list(reversed(deck_history))
    timedelta_dict: dict[str, CardTime] = dict()
    for card in deck_history:
        if card["name"] in timedelta_dict:
            delta = timedelta_dict[card["name"]]
            if card["qty"] == -1 and delta["currently_in_deck"] == True:
                delta["currently_in_deck"] = False
                new_date = convert_timestring(card["date"])
                time_diff = new_date - delta["last_update"]
                delta["total_time_in_deck"] += time_diff
                delta["last_update"] = new_date
            elif card["qty"] == 1:
                if delta["currently_in_deck"] == True:
                    print(f"***trying to add card already in deck, {card['name']}")
                    continue
                delta["currently_in_deck"] = True
                delta["last_update"] = convert_timestring(card["date"])

        else:
            if card["qty"] != 1:
                print("***trying to remove card not in deck")
                breakpoint()
                exit(1)
            new_delta: CardTime = {
                "currently_in_deck": True,
                "last_update": convert_timestring(card["date"]),
                "total_time_in_deck": datetime.timedelta(),
            }
            timedelta_dict[card["name"]] = new_delta

    now = datetime.datetime.now()
    for _, delta in timedelta_dict.items():
        # total_seconds = delta["total_time_in_deck"].total_seconds()
        if delta["currently_in_deck"] == True:
            time_diff = now - delta["last_update"]
            delta["total_time_in_deck"] += time_diff
        delta["time_in_deck_str"] = str(delta["total_time_in_deck"])
        delta["total_time_in_deck"] = delta["total_time_in_deck"].total_seconds()
        delta["last_update"] = str(delta["last_update"])

    timedelta_dict = {
        k: v
        for k, v in sorted(
            timedelta_dict.items(),
            key=lambda item: item[1]["total_time_in_deck"],
            reverse=True,
        )
    }

    new_filename = filename.replace(".json", " history.json")
    with open(new_filename, "w") as f:
        json.dump(timedelta_dict, f, indent=4)


if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, "r") as f:
        deck_history = json.load(f)
    run(deck_history, filename)
