import json
import os
import time
import unittest
from datetime import datetime, timedelta

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from dotenv import load_dotenv
from selenium.common import NoSuchElementException

load_dotenv()
appium_server_url = 'http://localhost:4723'

DATES = ["12,03", "16,03", "17,03", "25,03"]

MONTHS_MAP = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}

PROVIDERS = ("Booking.com", "Priceline", "Vio.com", "Agoda.com", "eDreams", "StayForLong", "ZenHotels.com")


class TestAppium(unittest.TestCase):
    @classmethod
    def setUpClass(self) -> None:
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.automation_name = "uiautomator2"
        options.device_name = "Android"
        options.app_package = "com.google.android.apps.nexuslauncher"
        options.app_activity = "com.google.android.apps.nexuslauncher.NexusLauncherActivity"
        options.no_reset = True
        options.language = "en"
        options.locale = "US"

        self.driver = webdriver.Remote(appium_server_url, options=options)
        self.hotel_name = os.getenv("HOTEL_NAME", "The  Grosvenor Hotel")
        self.dates = os.getenv("DATES", self.generate_dates(self))

    def SetUp(self):
        pass

    @staticmethod
    def generate_dates(self):
        today = datetime.today()
        return [
            today.strftime("%Y-%m-%d"),
            (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            (today + timedelta(days=4)).strftime("%Y-%m-%d"),
        ]

    def open_tripadvisor(self) -> None:
        """Открывает App Drawer и запускает Tripadvisor"""
        # 1.Swipe up (open menu)
        self.driver.swipe(500, 1800, 500, 500, 500)

        time.sleep(2)

        try:
            self.get_all_elements()
            search_box = self.driver.find_element(AppiumBy.XPATH, '//*[contains(@text, "Search")]')
            search_box.click()
            time.sleep(2)
            search_box.send_keys("Tripadvisor")
            time.sleep(3)
        except:
            self.fail("Field 'Search' was not found!")

        try:
            tripadvisor_icon = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Tripadvisor"]')
            tripadvisor_icon.click()
        except:
            self.fail("Tripadvisor was not found!")

        time.sleep(2)

    def get_all_elements(self):
        # Находим все элементы на экране
        elements = self.driver.find_elements(AppiumBy.XPATH, "//*")

        elements_text = []

        # Извлекаем текст каждого элемента
        for element in elements:
            text = element.text.strip()  # Убираем лишние пробелы
            if text:  # Если текст существует (не пустой)
                elements_text.append(text)
            else:
                # Можно добавить информацию о том, что элемент не содержит текста
                elements_text.append(f"Element with no text: {element.tag_name}")

        return elements

    def select_hotel_filter(self):
        hotel_filter = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Hotels"]')
        hotel_filter.click()
        time.sleep(2)

    def search_hotel(self):
        try:
            search_box = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Search"]')
            search_box.click()
            time.sleep(2)
        except:
            self.fail("Не удалось найти кнопку поиска!")

        try:
            self.driver.switch_to.active_element.send_keys(self.hotel_name)
            time.sleep(3)
        except:
            self.fail("Не удалось ввести текст в поле поиска!")

        self.select_hotel_filter()
        # self.get_all_elements()

        results = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        for result in results:
            if result.text.strip() == "The Grosvenor Hotel":
                result.click()
                break
        time.sleep(3)

    def open_calendar(self):
        elements = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        for el in elements:
            text = el.text
            if "→" in text or "-" in text:
                el.click()
                break

    def swipe_down(self):
        """
        Свайпает вверх, чтобы найти недостающие даты.
        """
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = size["height"] * 0.5
        end_y = size["height"] * 0.8
        self.driver.swipe(start_x, start_y, start_x, end_y, 1000)

    def swipe_up(self):
        """
        Свайпает вверх, чтобы найти недостающие даты.
        """
        size = self.driver.get_window_size()
        start_x = size["width"] // 2
        start_y = size["height"] * 0.8
        end_y = size["height"] * 0.5
        self.driver.swipe(start_x, start_y, start_x, end_y, 1000)

    def swipe_to_top(self):
        previous_page_source = None  # Храним предыдущий экран
        max_swipes = 10  # Лимит на количество свайпов

        for _ in range(max_swipes):
            self.swipe_down()
            time.sleep(1)  # Ждем загрузки

            # Получаем HTML/структуру экрана
            current_page_source = self.driver.page_source

            # Если экран не изменился — значит, достигли верха
            if current_page_source == previous_page_source:
                print("Достигнут верх страницы.")
                break

            previous_page_source = current_page_source

    def select_dates(self, start_date):
        """
        Выбирает даты в календаре, если они свободны.

        :param driver: WebDriver instance
        :param start_date: str, дата начала в формате '20'
        :param end_date: str, дата окончания в формате '23'
        :return: str, цена или ошибка
        """

        def get_month_name(date_str):
            print(date_str)
            """Преобразует 'dd,mm' в название месяца"""
            day, month = date_str.split(",")
            return MONTHS_MAP.get(month), day

        start_month, start_day = get_month_name(start_date)
        print(start_month)

        # Поиск нужного месяца (свайпаем, если даты не видны)
        max_swipes = 15
        for _ in range(max_swipes):
            try:
                time.sleep(2)
                month_element = self.driver.find_element(AppiumBy.XPATH,
                                                         f'//android.widget.TextView[contains(@text, "{start_month}")]')
                break
            except NoSuchElementException:
                self.swipe_up()
        else:
            raise Exception(f"Не удалось найти месяц {start_month}!")

        # Проверяем доступность и кликаем
        try:
            self.driver.find_element(AppiumBy.XPATH, f'//android.widget.TextView[@text="{start_day}"]').click()

        except:
            print(f"❌ Не удалось найти дату {start_day},{start_month}")

        # Выбираем следующий день
        next_day = str(int(start_day) + 1)
        try:
            self.driver.find_element(AppiumBy.XPATH, f'//android.widget.TextView[@text="{next_day}"]').click()

        except:
            print(f"❌ Не удалось найти следующую дату {next_day},{start_month}")

        # Нажимаем "Apply"
        try:
            apply_button = self.driver.find_element(AppiumBy.XPATH, '//android.widget.Button[@text="Apply"]')
            apply_button.click()
        except NoSuchElementException:
            raise Exception("Не удалось найти кнопку Apply.")

    def tap_view_all_button(self):
        try:
            # Поиск кнопки, содержащей "View all "
            time.sleep(3)
            button = self.driver.find_element(AppiumBy.XPATH, "//*[contains(@text, 'View all ')]")
            button.click()
            print("Кнопка 'View all' нажата.")
        except Exception as e:
            print("Кнопка 'View all' не найдена:", e)

    def take_screenshot(self, screenshot_name):
        """ Делает скриншот и сохраняет в папке screenshots/ """
        screenshots_dir = "screenshots"
        os.makedirs(screenshots_dir, exist_ok=True)  # Создаем папку, если её нет
        file_path = os.path.join(screenshots_dir, f"{screenshot_name}.png")
        self.driver.save_screenshot(file_path)
        return file_path

    def get_providers_and_prices(self):
        """Собирает список провайдеров и цен, свайпая вверх при необходимости."""
        time.sleep(2)
        MAX_SWIPES = 5

        all_providers_prices = set()
        swipe_count = 0

        self.swipe_to_top()

        while swipe_count < MAX_SWIPES:
            all_elements = self.driver.find_elements(AppiumBy.XPATH, "//*")

            providers_prices = []

            for element in all_elements:
                # Пробуем разные способы получить текст
                text = element.text.strip() or element.get_attribute("name") or element.get_attribute(
                    "content-desc") or ""

                if text:
                    # Если найденное имя есть в списке PROVIDERS, сохраняем
                    if any(provider.lower() in text.lower() for provider in PROVIDERS):
                        providers_prices.append({"provider": text, "price": None})

                    # Если текст — это цена (например, "$92"), то тоже добавляем
                    elif "$" in text:
                        providers_prices.append({"provider": None, "price": text})

            # Объединяем провайдеров с их ценами
            temp_provider = None
            final_result = []

            print("Providers len: ", len(providers_prices))

            for item in providers_prices:
                if item["provider"]:
                    temp_provider = item["provider"]
                elif item["price"] and temp_provider:
                    screenshot_name = f"{temp_provider}_{self.hotel_name}".replace(" ", "_").replace(".", "")
                    screenshot_path = self.take_screenshot(screenshot_name)
                    final_result.append((temp_provider, item["price"], screenshot_path))
                    temp_provider = None  # Сбрасываем, чтобы не привязывать к следующей цене

            # Добавляем только новые данные
            new_data = set(final_result) - all_providers_prices

            if not new_data:
                print("Новых данных нет, завершаем поиск.")
                break  # Если после свайпа ничего не поменялось, выходим из цикла

            all_providers_prices.update(new_data)  # Обновляем общий список

            print(f"Свайп {swipe_count + 1}: добавлены {len(new_data)} новых записей.")

            self.swipe_up()
            time.sleep(2)

            swipe_count += 1

        if len(all_providers_prices)==0:
            all_providers_prices={("The dates indicated are already booked", "", "")}

        print("Финальный результат:", all_providers_prices)

        return all_providers_prices

    def test_search_and_collect_data(self):
        # self.open_tripadvisor()
        # self.search_hotel()
        # self.tap_view_all_button()
        for date in DATES:
            self.open_calendar()
            self.select_dates(date)
            info = self.get_providers_and_prices()
            save_to_json(self.hotel_name, date, info)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()


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


if __name__ == '__main__':
    unittest.main()
