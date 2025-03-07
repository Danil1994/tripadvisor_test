import unittest
import os
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy


apk_path = os.path.abspath("main_app/tests_runner/Tripadvisor.apk")
appium_server_url = 'http://localhost:4723'


class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.automation_name = "uiautomator2"
        options.device_name = "Android"
        options.app_package = "com.google.android.apps.nexuslauncher"
        options.app_activity = "com.google.android.apps.nexuslauncher.NexusLauncherActivity"

        options.no_reset=True
        options.language = "en"
        options.locale = "US"

        self.driver = webdriver.Remote(appium_server_url, options=options)


    def test_open_tripadvisor(self) -> None:
        """Открывает App Drawer и запускает Tripadvisor"""
        # 1. Свайпнуть вверх (открыть меню приложений)
        self.driver.swipe(500, 1800, 500, 500, 500)  # Координаты могут меняться

        time.sleep(2)  # Даем время на анимацию

        # 2. Найти иконку Tripadvisor и кликнуть
        try:
            tripadvisor_icon = self.driver.find_element(AppiumBy.XPATH, '//*[@text="Tripadvisor"]')
            tripadvisor_icon.click()
        except:
            self.fail("Не удалось найти иконку Tripadvisor!")

        time.sleep(3)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()


if __name__ == '__main__':
    unittest.main()


