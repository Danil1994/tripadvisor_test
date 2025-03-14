import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from appium.webdriver.common.appiumby import AppiumBy

from datetime import datetime, timedelta


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


def wait_for_appear(driver, text, timeout=10, poll_frequency=1):
    """
    Ожидает появления указанного текста на экране.

    :param driver: WebDriver (Appium)
    :param text: str, текст, который ждем
    :param timeout: int, максимальное время ожидания (секунды)
    :param poll_frequency: int, частота проверки наличия текста (секунды)
    :return: True, если текст появился, иначе False
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


def wait_for_disappear(driver, text, timeout=10, poll_frequency=1):
    """
    Ожидает появления указанного текста на экране.

    :param driver: WebDriver (Appium)
    :param text: str, текст, который ждем
    :param timeout: int, максимальное время ожидания (секунды)
    :param poll_frequency: int, частота проверки наличия текста (секунды)
    :return: True, если текст появился, иначе False
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
