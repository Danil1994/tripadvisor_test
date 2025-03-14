import time
from datetime import datetime, timedelta

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait


def validate_date(date_input: (int, str)) -> [str, None]:
    date_input = str(date_input)
    date_input = date_input.replace(",", ".")

    try:
        # separate date
        day, month = map(int, date_input.split("."))
        # valid checking
        datetime(year=2024, month=month, day=day)
        return f"{day:02}.{month:02}"
    except (ValueError, IndexError):
        return None


def get_next_day(date_str: str) -> str:
    day, month = date_str.split(".")
    today = datetime.today()
    try:
        current_date = datetime(today.year, int(month), int(day))
    except ValueError:
        return "Uncorrect date of month"

    next_date = current_date + timedelta(days=1)
    return next_date.strftime("%d.%m")


def wait_for_appear(driver, text, timeout=15, poll_frequency=1):
    """
    Waits for the specified text to appear on the screen.

    :param driver: WebDriver (Appium)
    :param text: str, text to wait for
    :param timeout: int, maximum wait time (seconds)
    :param poll_frequency: int, frequency of checking for text (seconds)
    :return: True, if text appears, otherwise False
    """
    time.sleep(1)
    try:
        WebDriverWait(driver, timeout, poll_frequency=poll_frequency).until(
            lambda x: x.find_elements(AppiumBy.XPATH, f"//*[contains(@text, '{text}')]")
        )
        print(f"✅ Text '{text}' was founded.")
        return True
    except TimeoutException:
        print(f"⛔ Text '{text}' did`t appear during {timeout} seconds.")
        return False


def wait_for_disappear(driver, text, timeout=15, poll_frequency=1):
    """
    Waits for the specified text to disappear on the screen.

    :param driver: WebDriver (Appium)
    :param text: str, text to wait for
    :param timeout: int, maximum wait time (seconds)
    :param poll_frequency: int, frequency of checking for text (seconds)
    :return: True, if text disappears, otherwise False
    """
    time.sleep(1)
    try:
        WebDriverWait(driver, timeout, poll_frequency=poll_frequency).until_not(
            lambda x: x.find_elements(AppiumBy.XPATH, f"//*[contains(@text, '{text}')]")
        )
        print(f"✅ Text '{text}' disappear.")
        return True
    except TimeoutException:
        print(f"⛔ Text '{text}' did`t disappear during {timeout} seconds.")
        return False
