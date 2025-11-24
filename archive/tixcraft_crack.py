import os
import sys
import cv2
import time
import random
import requests
import traceback
import threading
import pytesseract
import numpy as np
from io import BytesIO
from PIL import Image
from datetime import datetime
from selenium import webdriver
from PIL import Image, ImageEnhance, ImageFilter
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" 
# tesseract_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

def print_log(msg):
    print("{} - {}".format(datetime.now(), msg))


def preprocess_captcha_image(image):
    # Convert to grayscale
    img = image.convert("L")
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)

    # Convert to numpy array for OpenCV processing
    img_np = np.array(img)

    # Apply adaptive thresholding
    img_np = cv2.adaptiveThreshold(img_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Denoising for clearer text
    img_np = cv2.fastNlMeansDenoising(img_np, None, 30, 7, 21)
    
    # Convert back to PIL Image
    return Image.fromarray(img_np)


def waiting_to_open():
    # Wait for the ticket to start selling
    last_print_ts = time.time()*1000 - 5000
    while True:
        current_ts = time.time()*1000

        if current_ts >= start_selling_ts:
            break

        if current_ts - last_print_ts >= 1000:
            print_log("The ticket market will open in {} sec".format(int((start_selling_ts-current_ts)/1000)))
            last_print_ts = current_ts

        time.sleep(0.001)
    print_log("Ticket market is opening".format(datetime.now()))


def click_purchase():
    # Click the "立即購票" Button
    while True:
        try:
            purchase_button = driver.find_element(By.XPATH, "//li[@class='buy']/a")
            ActionChains(driver).move_to_element(purchase_button).click(purchase_button).perform()
            print_log("Purchase button clicked.")
            break
        except Exception as e:
            print_log(f"Error clicking purchase button: {e}")
        time.sleep(0.1)


def click_event():
    # Choose the event by the date we want
    while True:
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, "gameList")))

        try:
            event_selected = False
            rows = driver.find_elements(By.CSS_SELECTOR, "#gameList tbody tr")
            for row in rows:
                date_text = row.find_element(By.TAG_NAME, "td").text
                if concert_date in date_text:
                    purchase_button = row.find_element(By.CLASS_NAME, "btn-primary")
                    purchase_button.click()
                    event_selected = True
                    print_log(f"Clicked '立即訂購' for the performance on {concert_date}")
                    break
                else:
                    print_log("Performance not found.")

            if not event_selected:
                purchase_button = row.find_element(By.CLASS_NAME, "btn-primary")
                purchase_button.click()
            break
        except:
            # traceback.print_exc()
            pass
        time.sleep(0.1)


def click_seat():
    # Choose the seat by the category we want
    while True:
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".zone.area-list"))
        )

        try:
            available_tickets = driver.find_elements(By.CSS_SELECTOR, ".select_form_b a")
            # categories = driver.find_elements(By.CLASS_NAME, "category")
            # target_category = None

            ticket_selected = False
            for ticket in available_tickets:
                ticket_text = ticket.text
                
                if "已售完" not in ticket_text:
                    if (seat_key_word1 in ticket_text) or (seat_key_word2 in ticket_text) or (seat_key_word3 in ticket_text):
                        if "熱賣中" in ticket_text:
                            ticket.click()
                            ticket_selected = True
                            print_log(f"Clicked on ticket: {ticket_text}")
                            break
                        else:
                            ticket_remain = int(ticket_text.split(" ")[3])
                            if ticket_remain >= int(ticket_number):
                                ticket.click()
                                ticket_selected = True
                                print_log(f"Clicked on ticket: {ticket_text}")
                                break

            if not ticket_selected:
                print_log("No available tickets were found.")
            break
        except:
            traceback.print_exc()
            pass
        time.sleep(0.1)


def input_ticket_info():
    while True:
        try:
            select_element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select[id^='TicketForm_ticketPrice']"))
            )
            select = Select(select_element)
            if select.first_selected_option.get_attribute("value") != ticket_number:
                select.select_by_value(ticket_number)
                print_log(f"Ticket number {ticket_number} selected.")
            terms_checkbox = driver.find_element(By.ID, "TicketForm_agree")
            if not terms_checkbox.is_selected():
                terms_checkbox.click()
                print_log("Agreement checkbox clicked.")          
        except:
            # traceback.print_exc()
            pass
        time.sleep(0.1)


def image_verify(start):
    while True:
        try:
            captcha_image = driver.find_element(By.ID, "TicketForm_verifyCode-image")
            captcha_url = captcha_image.get_attribute("src")

            next_img = True
            for i in range(3):
                response = session.get(captcha_url)
                img = Image.open(BytesIO(response.content))
                img = img.convert("L")
                img = img.filter(ImageFilter.MedianFilter())
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(2)  # Increase contrast
                img = img.point(lambda x: 0 if x < 128 else 255)
                # processed_img = preprocess_captcha_image(img)
                
                captcha_text = pytesseract.image_to_string(img).replace("\n","").replace(" ","").lower()
                # captcha_text = pytesseract.image_to_string(processed_img, config=tesseract_config).strip().lower()
                if len(captcha_text) == 4:
                    next_img = False
                    break
            
            if next_img == True:
                captcha_image.click()
            else:
                print_log(f"Captcha text: {captcha_text}")
                captcha_input = driver.find_element(By.ID, "TicketForm_verifyCode")
                captcha_input.clear()
                captcha_input.send_keys(captcha_text)

                submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'btn-primary')]")
                ActionChains(driver).move_to_element(submit_button).click(submit_button).perform()
                end = time.time()

                if WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.ID, "unique_element_id_new_page"))
                ):
                    print_log("Total cost: {}".format(round(end - start, 2)))
                    break
        except:
            pass
            # traceback.print_exc()
    time.sleep(0.1)

if __name__ == "__main__":
    ticket_number = "2"
    concert_date = "2024/12/07"
    seat_key_word1 = "2800"
    seat_key_word2 = "2400"
    seat_key_word3 = "1800"
    start_selling_ts = int((time.time()+5)*1000)
    
    # session = requests.Session()
    # cookies = {"SID": "ma36vl59u3r7o4su59i3siq123"}
    # session.cookies.update(cookies)

    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:9222")
    driver = webdriver.Chrome(options=options)
    time.sleep(1)
    driver.maximize_window()
    driver.get("https://tixcraft.com/activity/detail/24_xalive")

    waiting_to_open()
    start = time.time()
    click_purchase()

    t1 = threading.Thread(target=click_event).start()
    t2 = threading.Thread(target=click_seat).start()
    t3 = threading.Thread(target=input_ticket_info).start()
    # t4 = threading.Thread(target=image_verify, args=(start,)).start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print("\nProgram interrupted. Exiting gracefully...")
            sys.exit(1)
        time.sleep(1)