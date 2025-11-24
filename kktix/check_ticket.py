
from utils.base import *


EVENT_URL_LIST = [
    "https://kktix.com/events/af3785a1/registrations/new",
    "https://kktix.com/events/af3785b2/registrations/new",
    "https://kktix.com/events/af3785c3/registrations/new",
]


def create_driver():
    opts = Options()
    # opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=opts)


def check_ticket(driver, wait, url):
    driver.get(url)
    print("{} - Checking tickets for event: {}".format(datetime.now(), url))
    
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='registrationsNewApp']/div/div[5]/div[1]/div[1]/div[3]/div[2]")))
    ticket_units = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ticket-unit")))
    target_games = [i.text for i in ticket_units]

    for game in target_games:
        if "Sold Out" not in game:
            game_info = game.split("\n")
            if len(game_info) >= 2:
                location = game_info[0]
                price = game_info[1]
                # print(f"Location: {location} ; Ticket price: {price}")
                msg = "Ticket is avaliable to buy !!! ({})".format(game.replace("\n", " "))
                asyncio.run(tg_notify.sendMessage(msg, chat_name="TimKuo"))
                print("{} - {}".format(datetime.now(), msg))
                break
        else:
            msg = "Ticket is sold out !!! ({})".format(game.replace("\n", "\t"))
            print("{} - {}".format(datetime.now(), msg))

def main(event_url):
    driver = create_driver()
    wait = WebDriverWait(driver, 5)  # 5 seconds timeout
    print("{} - Started monitoring tickets for event: {}".format(datetime.now(), event_url))

    while True:
        try:
            check_ticket(driver, wait, event_url)
        except Exception as e:
            print("{} - Error occurred: {} with event url: {}".format(datetime.now(), str(e), event_url))
        time.sleep(5)


if __name__ == "__main__":
    thread_pool = []
    for event_url in EVENT_URL_LIST:
        t = threading.Thread(target=main, args=(event_url,))
        thread_pool.append(t)
        t.start()
    
    for t in thread_pool:
        t.join()