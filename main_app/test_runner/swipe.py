import time


def down_little(self):
    """
    Свайпает вверх, чтобы найти недостающие даты.
    """
    size = self.driver.get_window_size()
    start_x = size["width"] // 2
    start_y = size["height"] * 0.7
    end_y = size["height"] * 0.9
    self.driver.swipe(start_x, start_y, start_x, end_y, 1000)

def down_much(self):
    """
    Свайпает вверх, чтобы найти недостающие даты.
    """
    size = self.driver.get_window_size()
    start_x = size["width"] // 2
    start_y = size["height"] * 0.5
    end_y = size["height"] * 0.9
    self.driver.swipe(start_x, start_y, start_x, end_y, 1000)



def up(self):
    """
    Свайпает вверх, чтобы найти недостающие даты.
    """
    size = self.driver.get_window_size()
    start_x = size["width"] // 2
    start_y = size["height"] * 0.8
    end_y = size["height"] * 0.5
    self.driver.swipe(start_x, start_y, start_x, end_y, 1000)


def to_top(self):
    previous_page_source = None  # Храним предыдущий экран
    max_swipes = 10  # Лимит на количество свайпов

    for _ in range(max_swipes):
        down_little(self)
        time.sleep(1)  # Ждем загрузки

        # Получаем HTML/структуру экрана
        current_page_source = self.driver.page_source

        # Если экран не изменился — значит, достигли верха
        if current_page_source == previous_page_source:
            print("Достигнут верх страницы.")
            break

        previous_page_source = current_page_source
