
import os
import unittest
import json
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.by import By

load_dotenv()
appium_server_url = "http://localhost:4723"


class TripAdvisorTest(unittest.TestCase):
    """Тест-кейс для Tripadvisor"""

    @classmethod
    def setUpClass(cls):
        """Настройка перед тестами"""
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.automation_name = "uiautomator2"
        options.device_name = "Android"
        options.app_package = "com.tripadvisor.tripadvisor",
        options.app_activity = "com.tripadvisor.tripadvisor.home.HomeActivity",
        options.automationName = "UiAutomator2",
        options.language = "en"
        options.locale = "US"

        cls.driver = webdriver.Remote(appium_server_url, options=options)
        time.sleep(3)
        cls.open_tripadvisor(cls)


    def setUp(self):
        self.hotel_name = os.getenv("HOTEL_NAME")
        self.dates = os.getenv("DATES", self.generate_dates(self))
        self.results = {}

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


    @staticmethod
    def open_tripadvisor(cls):
        """Ищем и открываем приложение Tripadvisor"""
        search_box = cls.driver.find_element(By.ID, "com.android.launcher3:id/search_box")
        search_box.click()
        time.sleep(1)

        search_input = cls.driver.find_element(By.ID, "com.android.launcher3:id/search_src_text")
        search_input.send_keys("Tripadvisor")
        time.sleep(2)

        results = cls.driver.find_elements(By.CLASS_NAME, "android.widget.TextView")
        for result in results:
            if "tripadvisor" in result.text.lower():
                result.click()
                time.sleep(5)
                return

        raise Exception("Приложение Tripadvisor не найдено!")

    def select_hotel_filter(self):
        time.sleep(2)
        filters = self.driver.find_elements(By.CLASS_NAME, "android.widget.TextView")

        for filter in filters:
            if filter.text.lower() == "hotel":
                filter.click()
                time.sleep(2)
                return
        raise Exception("Filter 'Hotel' has not been founded!")

    def search_hotel(self):
        """Ищем отель в Tripadvisor"""
        search_box = self.driver.find_element(By.ID, "com.tripadvisor.tripadvisor:id/search_bar")
        search_box.click()
        time.sleep(2)

        search_input = self.driver.find_element(By.ID, "com.tripadvisor.tripadvisor:id/search_src_text")
        search_input.send_keys(self.hotel_name)
        time.sleep(3)

        # self.select_hotel_filter()

        results = self.driver.find_elements(By.CLASS_NAME, "android.widget.TextView")
        results[0].click()
        time.sleep(5)

    def get_prices(self):
        """Получаем цены от разных поставщиков"""
        prices = {}
        providers = self.driver.find_elements(By.ID, "com.tripadvisor.tripadvisor:id/provider_name")
        price_values = self.driver.find_elements(By.ID, "com.tripadvisor.tripadvisor:id/price")

        for provider, price in zip(providers, price_values):
            prices[provider.text] = price.text

        return prices

    def save_screenshot(self):
        """Делаем скриншот"""
        filename = f"{self.hotel_name.replace(' ', '_')}.png"
        self.driver.save_screenshot(filename)
        return filename

    def test_search_and_collect_data(self):
        """Основной тест: поиск отеля, сбор данных, скриншот"""
        self.search_hotel()

        for date in self.dates:
            prices = self.get_prices()
            screenshot = self.save_screenshot()

            self.results[date] = {
                "providers": prices,
                "screenshot": screenshot
            }

        with open("prices.json", "w") as f:
            json.dump({self.hotel_name: self.results}, f, indent=4)

        self.assertTrue(len(self.results) == 5, "Не все даты обработаны!")

    @classmethod
    def tearDownClass(cls):
        """Закрытие драйвера после всех тестов"""
        cls.driver.quit()


if __name__ == "__main__":
    unittest.main()