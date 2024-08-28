import sys, os, requests, json
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, ParseResult
from typing import TypedDict


OUTPUT_DIRNAME = "outputs"


class Card(TypedDict):
    name: str
    qty: int
    date: str


def get_p1_url(deck_id):
    return f"https://api2.moxfield.com/v2/decks/all/{deck_id}/history?pageNumber=1&pageSize=100&boardFilter=mainboard"


def get_next_page_url(url, total_pages):
    parse_result = urlparse(url)
    query_dict = parse_qs(parse_result.query)
    next_page_num = int(query_dict["pageNumber"][0]) + 1
    if next_page_num > total_pages:
        return False
    query_dict["pageNumber"] = next_page_num
    new_qd = urlencode(query_dict, doseq=True)
    new_parse_result = ParseResult(
        scheme=parse_result.scheme,
        netloc=parse_result.netloc,
        path=parse_result.path,
        params=parse_result.params,
        query=new_qd,
        fragment=parse_result.fragment,
    )
    return urlunparse(new_parse_result)


def format_data_entry(entry) -> Card:
    return {
        "name": entry["card"]["name"],
        "qty": entry["quantityDelta"],
        "date": entry["updatedAtUtc"],
    }


def add_page_to_list(output_list: list[Card], data):
    if len(set([x["cardType"] for x in data["data"]])) > 1:
        print("***card not normal")
        breakpoint()

    for entry in data["data"]:
        output_list.append(format_data_entry(entry))


def run(deck_id):
    url = get_p1_url(deck_id)
    output_list: list[Card] = []
    data = None
    while url is not False:
        data = requests.get(url).json()
        add_page_to_list(output_list, data)
        print("***len", len(output_list))
        url = get_next_page_url(url, data["totalPages"])

    deck_name = requests.get(
        f"https://api2.moxfield.com/v3/decks/all/{deck_id}"
    ).json()["name"]
    filename = f"./outputs/{deck_name}.json"
    with open(filename, "w") as f:
        json.dump(output_list, f, indent=4)

    return filename


if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIRNAME):
        os.mkdir(OUTPUT_DIRNAME)
    deck_id = sys.argv[1]
    run(deck_id)
