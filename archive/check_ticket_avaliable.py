import time
import asyncio
import traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException

from telegramBot import *


def check_avaliable_tickets():
    tickets_table = driver.find_element(By.CLASS_NAME, "area-list")
    tickets_list = tickets_table.find_elements(By.TAG_NAME, "li")
    tickets_list = [i for i in tickets_list if "身障" not in i.text]
    avaliable_tickets_list = [i.text for i in tickets_list if "已售完" not in i.text]

    if len(avaliable_tickets_list) != 0:
        print("{} - Avaliable Tickets: {}".format(datetime.now(), avaliable_tickets_list))
        return True
    else:
        return False


def scroll_until_table_fully_loaded(pause_time=1.0, max_scrolls=30):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # 到底了，沒再加載新內容
        last_height = new_height


async def check_avaliable_to_buy(concert_date_list):
    url = "https://truecolormusic.tixcraft.com/activity/game/25_mj116"
    # url = "https://tixcraft.com/activity/game/25_mj116"

    driver.get(url)
    time.sleep(1)
    game_table = driver.find_element(By.XPATH, '//*[@id="gameList"]/table')
    game_list = [(i.text, i) for i in game_table.find_elements(By.TAG_NAME, "tr")]

    if len(concert_date_list) != 0:
        target_games = []
        for concert_date in concert_date_list:
            target_game = [i for i in game_list if concert_date in i[0]]
            if len(target_game) != 0:
                target_games.append(target_game[0])
    else:
        target_games = game_list

    if len(target_games) != 0:
        for game in target_games:
            if "已售完" not in game[0]:
                purchase_button = game[1].find_elements(By.TAG_NAME, "td")[3].find_element(By.TAG_NAME, "button")
                driver.execute_script("arguments[0].click();", purchase_button)
                time.sleep(1)
                scroll_until_table_fully_loaded()

                tickets_avaliable = check_avaliable_tickets()
                if tickets_avaliable:
                    msg = "Ticket is avaliable to buy !!! ({})".format(game[0].replace("\n", " "))
                    await tg_notify.sendMessage(msg, chat_name="TimKuo")
                    print("{} - {}".format(datetime.now(), msg))
                else:
                    msg = "Ticket is sold out !!! ({})".format(game[0].replace("\n", " "))
                    print("{} - {}".format(datetime.now(), msg))
                    driver.get(url)
                    time.sleep(1)
            else:
                msg = "Ticket is sold out !!! ({})".format(game[0].replace("\n", " "))
                print("{} - {}".format(datetime.now(), msg))
        
    else:
        msg = "No avaliable concert event !!!"
        print("{} - {}".format(datetime.now(), msg))


if __name__ == "__main__":
    driver = webdriver.Chrome()
    # driver.maximize_window()
    # concert_date_list = ["2025/07/25", "2025/07/26"]
    concert_date_list = ["2025/07/26"]

    while True:
        try:
            asyncio.run(check_avaliable_to_buy(concert_date_list))
        except:
            traceback.print_exc()
        time.sleep(5)