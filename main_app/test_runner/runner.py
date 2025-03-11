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

MONTHS_MAP = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}


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
            time.sleep(2)
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

        # for el in elements_text:
        #     print(el)
        return elements_text

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

    def select_dates(self, start_date, end_date):
        """
        Выбирает даты в календаре, если они свободны.

        :param driver: WebDriver instance
        :param start_date: str, дата начала в формате '20'
        :param end_date: str, дата окончания в формате '23'
        :return: str, цена или ошибка
        """

        def is_date_available(date):
            """
            Проверяет, доступна ли указанная дата через `isEnabled()`.
            """
            print(date)
            try:
                el = self.driver.find_element(AppiumBy.XPATH, f'//android.widget.TextView[@text="{date}"]')
                print(el)
                return el.is_enabled()  # Если дата доступна для клика
            except NoSuchElementException:
                return False  # Даты нет на экране

        def swipe_up():
            """
            Свайпает вверх, чтобы найти недостающие даты.
            """
            size = self.driver.get_window_size()
            start_x = size["width"] // 2
            start_y = size["height"] * 0.8
            end_y = size["height"] * 0.5
            self.driver.swipe(start_x, start_y, start_x, end_y, 1000)

        def get_month_name(date_str):
            """Преобразует 'dd,mm' в название месяца"""
            day, month = date_str.split(",")
            return MONTHS_MAP.get(month), day

        start_month, start_day = get_month_name(start_date)
        end_month, end_day = get_month_name(end_date)
        print(start_month, end_month)

        # Поиск нужного месяца (свайпаем, если даты не видны)
        max_swipes = 15
        for _ in range(max_swipes):
            try:
                month_element = self.driver.find_element(AppiumBy.XPATH,
                                                         f'//android.widget.TextView[contains(@text, "{start_month}")]')
                break
            except NoSuchElementException:
                swipe_up()
        else:
            raise Exception(f"Не удалось найти месяц {start_month}!")

        # Проверяем доступность и кликаем
        if not is_date_available(start_day):
            raise Exception(f"Дата {start_day} {start_month} занята!")
        self.driver.find_element(AppiumBy.XPATH, f'//android.widget.TextView[@text="{start_day}"]').click()

        if not is_date_available(end_day):
            raise Exception(f"Дата {end_day} {end_month} занята!")
        self.driver.find_element(AppiumBy.XPATH, f'//android.widget.TextView[@text="{end_day}"]').click()

        # Нажимаем "Apply"
        try:
            apply_button = self.driver.find_element(AppiumBy.XPATH, '//android.widget.Button[@text="Apply"]')
            apply_button.click()
        except NoSuchElementException:
            raise Exception("Не удалось найти кнопку Apply.")

        # Ожидание загрузки цены
        timeout = 10
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                price_element = self.driver.find_element(AppiumBy.XPATH,
                                                         '//android.widget.TextView[contains(@text, "$")]')
                print(f"Цена: {price_element.text}")
                return f"Цена: {price_element.text}"
            except NoSuchElementException:
                time.sleep(1)

        raise Exception("Цена не подгрузилась!")

    def test_search_and_collect_data(self):
        # self.open_tripadvisor()
        # self.search_hotel()
        self.open_calendar()
        self.select_dates("11,04", "12,04")

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()


if __name__ == '__main__':
    unittest.main()
