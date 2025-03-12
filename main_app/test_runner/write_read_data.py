import json
import os


def save_to_json(hotel_name: str, date: str, info_datas: set):
    """ Сохраняет данные о ценах и скриншотах в JSON, дописывая новые данные """

    json_file = "data.json"

    # Проверяем, есть ли уже файл с данными
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                data = {}  # Если файл пуст, создаем новый словарь
    else:
        data = {}

    # Обновляем данные
    hotel_data = data.setdefault(hotel_name, {})
    date_data = hotel_data.setdefault(date, {})

    for provider, price, screenshot in info_datas:
        date_data[provider] = {
            "price": price,
            "screenshot": screenshot
        }

    # Сохраняем обратно в JSON
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    print(f"Данные успешно сохранены в {json_file}")
