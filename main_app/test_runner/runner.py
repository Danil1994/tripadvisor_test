import os
import time
import unittest
import swipe

from datetime import datetime, timedelta

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from dotenv import load_dotenv
from selenium.common import NoSuchElementException

from screenshot import take_screenshot
from write_read_data import save_to_json

load_dotenv()
appium_server_url = 'http://localhost:4723'

DATES = ["13,03", 16.03, "17.03", "31.03", "32.03"]

PROVIDERS = ("Booking.com", "Priceline", "Vio.com", "Agoda.com", "eDreams", "StayForLong", "ZenHotels.com")


class TestAppium(unittest.TestCase):
    MONTHS_MAP = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }

    @staticmethod
    def generate_dates():
        today = datetime.today()
        return [
            today.strftime("%d.%m"),
            (today + timedelta(days=1)).strftime("%d.%m"),
            (today + timedelta(days=2)).strftime("%d.%m"),
            (today + timedelta(days=5)).strftime("%d.%m"),
            (today + timedelta(days=20)).strftime("%d.%m"),
        ]

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
        dates_env = os.getenv("DATES")

        if not dates_env:
            self.dates = self.generate_dates()

    def SetUp(self):
        pass

    def open_tripadvisor(self) -> None:
        """Открывает App Drawer и запускает Tripadvisor"""
        # 1.Swipe up (open menu)
        self.driver.swipe(500, 1800, 500, 500, 500)

        time.sleep(2)

        try:
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

    def close_login_popup(self):
        """ Проверяет, есть ли окно регистрации/авторизации, и закрывает его """
        try:
            if self.driver.find_element(AppiumBy.XPATH, "//*[contains(@text, 'Create account')]"):
                swipe.down_much(self)
                print("Окно регистрации закрыто.")
        except NoSuchElementException:
            print("Окно регистрации не найдено.")

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

        results = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        for result in results:
            if result.text.strip() == "The Grosvenor Hotel":
                result.click()
                break

    def validate_date(self, date_input):
        # Если дата — число, приводим к строке
        date_input = str(date_input)

        # Заменяем запятую на точку
        date_input = date_input.replace(",", ".")

        try:
            # Разбираем день и месяц
            day, month = map(int, date_input.split("."))

            # Проверяем корректность даты, используя datetime
            datetime(year=2024, month=month, day=day)  # 2024 — високосный год, подходит для проверки

            # Возвращаем дату в правильном формате
            return f"{day:02}.{month:02}"
        except (ValueError, IndexError):
            return None

    def open_calendar(self):
        elements = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        for el in elements:
            text = el.text
            if "→" in text or "-" in text:
                el.click()
                break

    def select_dates(self, start_date):
        """
        Выбирает даты в календаре, если они свободны.

        :param driver: WebDriver instance
        :param start_date: str, дата начала в формате '20'
        :return: str, или ошибка
        """
        swipe.to_top(self)

        def get_next_day(date_str):
            day, month = date_str.split(".")
            today = datetime.today()
            try:
                current_date = datetime(today.year, int(month), int(day))
            except ValueError:
                return "Некорректное число месяца"

            next_date = current_date + timedelta(days=1)
            return next_date.strftime("%d.%m")

        def get_month_name(date_str):
            """Преобразует 'dd,mm' в название месяца"""
            day, month = date_str.split(".")
            return self.MONTHS_MAP.get(month), day

        def swipe_and_find_date(day, month):
            # Поиск нужного месяца (свайпаем, если даты не видны)
            max_swipes = 15
            for _ in range(max_swipes):
                try:
                    time.sleep(3)
                    month_element = self.driver.find_element(AppiumBy.XPATH,
                                                             f'//android.widget.TextView[contains(@text, "{month}")]')
                    month_location = month_element.location  # Получаем координаты месяца
                    month_size = month_element.size  # Получаем размеры блока месяца
                    break
                except NoSuchElementException:
                    swipe.up(self)
            else:
                raise Exception(f"Не удалось найти месяц {month}!")

            # Поиск числа внутри указанного месяца
            try:
                all_days = self.driver.find_elements(AppiumBy.XPATH, f'//android.widget.TextView[@text="{day}"]')

                for day_element in all_days:
                    day_location = day_element.location
                    # Проверяем, находится ли число ниже найденного месяца
                    if day_location['y'] > month_location['y']:
                        day_element.click()
                        return

                raise Exception(f"Дата {day}.{month} найдена, но вне границ месяца!")

            except NoSuchElementException:
                print(f"❌ Не удалось найти дату {day}.{month}")

        start_month, start_day = get_month_name(start_date)
        swipe_and_find_date(int(start_day), start_month)

        # Выбираем следующий день
        next_day = get_next_day(start_date)
        next_month, next_day = get_month_name(next_day)

        swipe_and_find_date(int(next_day), next_month)

        try:
            apply_button = self.driver.find_element(AppiumBy.XPATH, '//android.widget.Button[@text="Apply"]')
            apply_button.click()
        except NoSuchElementException:
            raise Exception("Не удалось найти кнопку Apply.")

    def tap_view_all_button(self):
        max_attempts = 5
        day = 1
        for attempt in range(max_attempts):
            print(f"Попытка {attempt + 1} из {max_attempts}...")

            # Поиск кнопки "View all"
            time.sleep(5)
            buttons = self.driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'View all ')]")

            if buttons:  # Если кнопка найдена
                print("✅ Кнопка найдена! Нажимаем...")
                buttons[0].click()
                return  # Выход из функции после успешного нажатия

            print("❌ Кнопка не найдена. Пробуем изменить дату...")
            self.open_calendar()
            tomorrow = datetime.today() + timedelta(days=day)
            self.select_dates(tomorrow.strftime("%d.%m"))
            day += 1

        # Если после 5 попыток кнопка не найдена
        print("⛔ Отель слишком занят, кнопка 'View all' так и не появилась!")
        info = {("Отель слишком занят, нет свободных дат ближайшие 5 дней", "", "")}
        save_to_json(self.hotel_name, "", info)

    def get_providers_and_prices(self, date):
        """Собирает список провайдеров и цен, свайпая вверх при необходимости."""
        time.sleep(2)
        MAX_SWIPES = 5

        all_providers_prices = set()
        swipe_count = 0

        swipe.to_top(self)

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

            for item in providers_prices:
                if item["provider"]:
                    temp_provider = item["provider"]
                elif item["price"] and temp_provider:
                    screenshot_name = f"{date}_{temp_provider}_{self.hotel_name}".replace(" ", "_")
                    screenshot_path = take_screenshot(self, screenshot_name)
                    final_result.append((temp_provider, item["price"], screenshot_path))
                    temp_provider = None  # Сбрасываем, чтобы не привязывать к следующей цене

            # Добавляем только новые данные
            new_data = set(final_result) - all_providers_prices

            if not new_data:
                print("Новых данных нет, завершаем поиск.")
                break  # Если после свайпа ничего не поменялось, выходим из цикла

            all_providers_prices.update(new_data)  # Обновляем общий список

            print(f"Свайп {swipe_count + 1}: добавлены {len(new_data)} новых записей.")

            swipe.up(self)
            time.sleep(2)

            swipe_count += 1

        if len(all_providers_prices) == 0:
            screenshot_name = f"{date}_NO_INFO_{self.hotel_name}".replace(" ", "_")
            screenshot_path = take_screenshot(self, screenshot_name)
            all_providers_prices = {("The dates indicated are already booked", "", screenshot_path)}

        print("Финальный результат:", all_providers_prices)

        return all_providers_prices

    def test_search_and_collect_data(self):
        self.open_tripadvisor()
        time.sleep(9)
        self.close_login_popup()
        time.sleep(2)
        self.search_hotel()
        time.sleep(6)
        self.tap_view_all_button()
        time.sleep(5)
        for date in self.dates:
            valid_date = self.validate_date(date)
            if valid_date:
                self.open_calendar()
                self.select_dates(valid_date)
                info = self.get_providers_and_prices(valid_date)
                save_to_json(self.hotel_name, valid_date, info)
            else:
                info = {("Inputted data are incorrect", "", "")}
                save_to_json(self.hotel_name, date, info)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()


if __name__ == '__main__':
    unittest.main()
