import os


def take_screenshot(self, screenshot_name):
    """ Делает скриншот и сохраняет в папке screenshots/ """
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)  # Создаем папку, если её нет
    file_path = os.path.join(screenshots_dir, f"{screenshot_name}.png")
    self.driver.save_screenshot(file_path)
    return file_path
