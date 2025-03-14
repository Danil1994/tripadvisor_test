import os
import time
import unittest
from datetime import datetime, timedelta

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from dotenv import load_dotenv
from selenium.common import NoSuchElementException
from utils import swipe
from utils.screenshot import take_screenshot
from utils.utils import (get_next_day, validate_date, wait_for_appear,
                         wait_for_disappear)
from write_read_data import save_to_json

load_dotenv()

appium_server_url = os.getenv("APPIUM_SERVER_URL", 'http://localhost:4723')

PROVIDERS = ("Booking.com", "Priceline", "Vio.com", "Agoda.com", "eDreams", "StayForLong", "ZenHotels.com")


class TestAppium(unittest.TestCase):
    MONTHS_MAP = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }

    @staticmethod
    def generate_dates() -> list[str, str]:
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

        device_name = os.getenv("ANDROID_DEVICE_NAME", "Android")
        options.device_name = device_name

        options.app_package = os.getenv("APP_PACKAGE", "com.google.android.apps.nexuslauncher")
        options.app_activity = os.getenv("APP_ACTIVITY", "com.google.android.apps.nexuslauncher.NexusLauncherActivity")

        options.no_reset = True
        options.language = "en"
        options.locale = "US"

        self.driver = webdriver.Remote(appium_server_url, options=options)
        self.hotel_name = os.getenv("HOTEL_NAME", "The  Grosvenor Hotel")
        dates_env = os.getenv("DATES", "")

        self.dates = dates_env.split(",") if dates_env else self.generate_dates()

    def SetUp(self):
        pass

    def open_tripadvisor(self) -> None:
        # 1.Swipe up (open menu)
        self.driver.swipe(500, 1800, 500, 500, 500)

        time.sleep(2)

        try:
            search_box = self.driver.find_element(AppiumBy.XPATH, '//*[contains(@text, "Search")]')
            search_box.click()
            time.sleep(2)
            search_box.send_keys("Tripadvisor")
            time.sleep(3)
        except NoSuchElementException:
            self.fail("Field 'Search' was not found!")

        try:
            tripadvisor_icon = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Tripadvisor"]')
            tripadvisor_icon.click()
        except NoSuchElementException:
            self.fail("Tripadvisor was not found!")

    def close_login_popup(self) -> None:
        """Checks if there is a registration/authorization window and closes it"""
        try:
            if self.driver.find_element(AppiumBy.XPATH, "//*[contains(@text, 'Create account')]"):
                swipe.down_much(self)
                print("Registration window was closed.")
        except NoSuchElementException:
            print("Registration window was not found.")

    def select_hotel_filter(self) -> None:
        hotel_filter = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Hotels"]')
        hotel_filter.click()
        time.sleep(2)

    def search_hotel(self) -> None:
        try:
            search_box = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Search"]')
            search_box.click()
            time.sleep(2)
        except NoSuchElementException:
            self.fail("'Search' button was not found!")

        try:
            self.driver.switch_to.active_element.send_keys(self.hotel_name)
            time.sleep(3)
        except NoSuchElementException:
            self.fail("Failed to enter text in the search field!")

        self.select_hotel_filter()

        results = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        for result in results:
            if result.text.strip() == self.hotel_name:
                result.click()
                break

    def open_calendar(self) -> None:
        elements = self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
        for el in elements:
            text = el.text
            if "→" in text or "-" in text:
                el.click()
                break

    def swipe_and_find_date(self, day: int, month: str) -> None:
        # Search for the desired month (swipe if dates or month were not found)
        max_swipes = 15
        for _ in range(max_swipes):
            try:
                time.sleep(3)
                month_element = self.driver.find_element(AppiumBy.XPATH,
                                                         f'//android.widget.TextView[contains(@text, "{month}")]')
                month_location = month_element.location  # get month element`s location
                break
            except NoSuchElementException:
                swipe.up(self)
        else:
            raise Exception(f"Unable to find month {month}!")

        # Search for the desired date under month element`s
        try:
            all_days = self.driver.find_elements(AppiumBy.XPATH, f'//android.widget.TextView[@text="{day}"]')

            for day_element in all_days:
                day_location = day_element.location
                # Check if the number is below the found month
                if day_location['y'] > month_location['y']:
                    day_element.click()
                    return

            raise Exception(f"Date {day}.{month} was found, but not in board of month!")

        except NoSuchElementException:
            print(f"❌ Date was not found {day}.{month}")

    def select_dates(self, start_date: str) -> None:
        """
        Selects dates in calendar
        :param start_date: str, dd.mm
        :return: str, or error
        """
        # Swipe to top to be sure that we start from beginning
        swipe.to_top(self)

        def get_month_name(date_str: str) -> [str, str]:
            """Transform 'dd,mm' into dd. month name"""
            day, month = date_str.split(".")
            return self.MONTHS_MAP.get(month), day

        start_month, start_day = get_month_name(start_date)
        self.swipe_and_find_date(int(start_day), start_month)

        # Tap next day, because we need choose two days for registration
        next_day = get_next_day(start_date)
        next_month, next_day = get_month_name(next_day)

        self.swipe_and_find_date(int(next_day), next_month)

        try:
            apply_button = self.driver.find_element(AppiumBy.XPATH, '//android.widget.Button[@text="Apply"]')
            apply_button.click()
        except NoSuchElementException:
            raise Exception("Button 'Apply' was not found.")

    def tap_view_all_button(self) -> bool:
        # This func tries to open "View all deal" button
        # there will be list of providers with price
        # sometimes this button not loaded and need choose others dates
        max_attempts = 5
        day = 1
        for attempt in range(max_attempts):
            print(f"Attempt {attempt + 1} from {max_attempts}...")

            # Founding button "View all..."
            wait_for_disappear(self.driver, 'Loading')
            buttons = self.driver.find_elements(AppiumBy.XPATH, "//*[contains(@text, 'View all ')]")

            if buttons:  # If button was found
                print("✅ Button was found! Click...")
                buttons[0].click()
                return True

            print("❌ Button was not found. Change date...")
            self.open_calendar()
            tomorrow = datetime.today() + timedelta(days=day)
            self.select_dates(tomorrow.strftime("%d.%m"))
            day += 1

        # If after 5 attempts button not founded
        print("⛔ The hotel is too busy, the 'View all' button never appeared")
        info = {("The hotel is too busy, no dates available for the next 5 days", "", "")}
        save_to_json(self.hotel_name, "", info)
        return False

    def get_providers_and_prices(self, date: str) -> set[tuple]:
        """Collects a list of providers and prices, swiping up when needed."""
        time.sleep(2)
        MAX_SWIPES = 5

        all_providers_prices = set()
        swipe_count = 0

        swipe.to_top(self)

        while swipe_count < MAX_SWIPES:
            all_elements = self.driver.find_elements(AppiumBy.XPATH, "//*")

            providers_prices = []

            for element in all_elements:
                # Try different way to get element`s text
                text = element.text.strip() or element.get_attribute("name") or element.get_attribute(
                    "content-desc") or ""

                if text:
                    # If the found name is in the PROVIDERS list, save it
                    if any(provider.lower() in text.lower() for provider in PROVIDERS):
                        providers_prices.append({"provider": text, "price": None})

                    # If text it is price (for example "$92"), save it like price
                    elif "$" in text:
                        providers_prices.append({"provider": None, "price": text})

            # Combine providers with their prices
            temp_provider = None
            final_result = []

            for item in providers_prices:
                if item["provider"]:
                    temp_provider = item["provider"]
                elif item["price"] and temp_provider:
                    screenshot_name = f"{datetime.today().strftime('%d.%m_%H.%M')}_{temp_provider}_{date}_{self.hotel_name}".replace(" ", "_")
                    screenshot_path = take_screenshot(self, screenshot_name)
                    final_result.append((temp_provider, item["price"], screenshot_path))
                    temp_provider = None  # Drop, for next price

            # Add only new data
            new_data = set(final_result) - all_providers_prices

            if not new_data:
                print("No new data, finish search.")
                break  # If after swipe change nothing break cycle

            all_providers_prices.update(new_data)

            print(f"Swipe {swipe_count + 1}: were added {len(new_data)} new records.")

            swipe.up(self)
            time.sleep(2)

            swipe_count += 1

        if len(all_providers_prices) == 0:
            screenshot_name = f"{datetime.today().strftime('%d.%m_%H.%M')}_NO_INFO_{date}_{self.hotel_name}".replace(
                " ", "_")

            screenshot_path = take_screenshot(self, screenshot_name)
            all_providers_prices = {("The dates indicated are already booked", "", screenshot_path)}

        print("Final result:", all_providers_prices)

        return all_providers_prices

    def test_search_and_collect_data(self):
        # each time.sleep its wait for load

        self.open_tripadvisor()
        wait_for_appear(self.driver, 'Search') or wait_for_appear(self.driver, 'Create account')
        self.close_login_popup()
        wait_for_appear(self.driver, 'Search')
        self.search_hotel()
        wait_for_appear(self.driver, self.hotel_name)
        if self.tap_view_all_button():
            wait_for_appear(self.driver, 'Deals')
        for date in self.dates:
            valid_date = validate_date(date)
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
            try:
                # Click "Back" many times to go out from application
                for _ in range(10):
                    self.driver.press_keycode(4)  # KEYCODE_BACK
                    time.sleep(1)  # Time for processing

            except Exception as e:
                print(f"Error exiting the application: {e}")

            self.driver.quit()


if __name__ == '__main__':
    unittest.main()
