import os


def take_screenshot(self, screenshot_name):
    """ Do screenshot and saves it in  screenshots/ """
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)  # Create folder if it not exists
    file_path = os.path.join(screenshots_dir, f"{screenshot_name}.png")
    self.driver.save_screenshot(file_path)
    return file_path
