
from utils.base import *


EVENT_URL = "https://tixcraft.com/activity/game/26_1rtp"
CONCERT_DATES = [
    "2026/03/04",
]


def create_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=opts)


def check_ticket(concert_date):
    driver.get(EVENT_URL)
    print("{} - Checking tickets for date: {}".format(datetime.now(), concert_date))
    time.sleep(0.5)

    game_table = driver.find_element(By.XPATH, '//*[@id="gameList"]/table')
    game_list = [i.text for i in game_table.find_elements(By.TAG_NAME, "tr")]

    if concert_date != "All":
        target_games = [i for i in game_list if concert_date in i]
    else:
        target_games = game_list
    print("{} - Target games found: {}".format(datetime.now(), len(target_games)))

    for game in target_games:
        if "已售完" not in game:
            msg = "Ticket is avaliable to buy !!! ({})".format(game.replace("\n", "\t"))
            asyncio.run(tg_notify.sendMessage(msg, chat_name="TimKuo"))
            print("{} - {}".format(datetime.now(), msg))
            break
        else:
            msg = "Ticket is sold out !!! ({})".format(game.replace("\n", "\t"))
            print("{} - {}".format(datetime.now(), msg))


def main():
    while True:
        for concert_date in CONCERT_DATES:
            try:
                check_ticket(concert_date)
            except Exception as e:
                print("{} - Error occurred: {}".format(datetime.now(), str(e)))
            time.sleep(0.1)
        time.sleep(5)


if __name__ == "__main__":
    driver = create_driver()
    main()