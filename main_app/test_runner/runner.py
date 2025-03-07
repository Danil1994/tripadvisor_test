import unittest
import os
import time
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from datetime import datetime, timedelta

from selenium.webdriver.common.by import By

load_dotenv()
appium_server_url = 'http://localhost:4723'


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

    # def SetUp(self):
    #     self.hotel_name = os.getenv("HOTEL_NAME", "The  Grosvenor Hotel")
    #     self.dates = os.getenv("DATES", self.generate_dates(self))

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
        # 1. Свайпнуть вверх (открыть меню приложений)
        self.driver.swipe(500, 1800, 500, 500, 500)  # Координаты могут меняться

        time.sleep(1)  # Даем время на анимацию

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

        for el in elements_text:
            print(el)
        return elements_text

    def select_hotel_filter(self):
        hotel_filter = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Hotels"]')
        hotel_filter.click()


    def search_hotel(self):
        try:
            search_box = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Search"]')
            search_box.click()
        except:
            self.fail("Не удалось найти кнопку поиска!")

        try:
            self.driver.switch_to.active_element.send_keys(self.hotel_name)
            time.sleep(3)
        except:
            self.fail("Не удалось ввести текст в поле поиска!")

        self.select_hotel_filter()
        # self.get_all_elements()

        # result = self.driver.find_element(AppiumBy.XPATH, '//*[@text="The Grosvenor Hotel"]')
        # result.click()

        results = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        for result in results:
            print(result.text)
            if result.text.strip() == "The Grosvenor Hotel":
                result.click()
                break
        time.sleep(3)

    def test_search_and_collect_data(self):
        self.open_tripadvisor()
        self.search_hotel()

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()


if __name__ == '__main__':
    unittest.main()
