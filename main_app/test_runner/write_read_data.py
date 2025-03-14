import json
import os
from datetime import datetime


def save_to_json(file_name, hotel_name: str, date: str, info_datas: set):

    json_file = f"{file_name}.json"

    # Check file or create new
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}  # If empty create new dict
    else:
        data = {}

    hotel_data = data.setdefault(hotel_name, {})
    date_data = hotel_data.setdefault(date, {})

    for provider, price, screenshot in info_datas:
        date_data[provider] = {
            "price": price,
            "screenshot": screenshot
        }

    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Data successfully saved in {json_file}")
