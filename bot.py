# -*- coding: utf-8 -*-
from threading import Timer

import psutil
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

tg_token = 'TOKEN'  # token of  Telegram bot
# Place name of the specialty (it used to search how many applications have been submitted)
xpath_of_the_specialty = "//*[contains(text(), 'SPECIALITY_NAME')]"
xpath_of_the_student = "//td[contains(text(),'SURNAME')]"  # Student's surname
rating_url = 'URL_rating'  # URL of the rating
number_url = 'URL_numbers'  # URL of the collage places
chat_id = 'ID'  # Here you can place your Telegram id or ID of your channel
before = 'null'  # used to check the statement: 'is date of rating has been changed?'
placement = 11  # place at rating at the start (or just a random number)


def ratingbot():
    global before
    global placement
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--disable-javascript')
    browser = webdriver.Chrome(options=options)
    browser.get(rating_url)
    ratingDate = browser.find_element_by_xpath(
        "//*[contains(text(), 'года')]").text  # 1 word from the rating title, for example: 'года'
    element = browser.find_element_by_xpath(xpath_of_the_specialty)
    actions = ActionChains(browser)
    actions.move_to_element(element).perform()
    browser.execute_script("window.scrollBy(100, 570);")
    el = browser.find_element_by_xpath(xpath_of_the_student)
    el.click()  # It singles out your name
    # Disable el.click() id program is crashing
    rating = int(browser.find_element_by_xpath(
        xpath_of_the_student + "/preceding-sibling::td[1]").text)  # Copying place in rating (preceding <tg> html tag)
    browser.save_screenshot('screenie.png')

    def sendImage():  # Sending image in the Telegram
        url = 'https://api.telegram.org/bot' + tg_token + '/sendPhoto'
        files = {'photo': open('screenie.png', 'rb')}
        data = {'chat_id': chat_id}
        r = requests.post(url, files=files, data=data)
        print(r.status_code, r.reason, r.content)
    if ratingDate == before:  # /* FIXME */ Kludge for the first start
        browser.close()
        Timer(3600, ratingbot).start()  # Waiting 1 hour
    else:
        diff = 0
        browser.get(number_url)
        number = browser.find_element_by_xpath(xpath_of_the_specialty + '/following::p[2]').text
        diff = placement - rating
        if diff < 0:
            url = 'https://api.telegram.org/bot' + tg_token + '/sendMessage'
            data = {'chat_id': chat_id,
                    'text': 'Погружение! Текущее место в рейтинге абитуриентов ' + ratingDate.lower() + ': ' + str(rating) + ' из ' + str(number) + '(' + str(diff) + ')'}
            r = requests.post(url, data=data)
            print(r.status_code, r.reason)
        if diff < 0:
            url = 'https://api.telegram.org/bot' + tg_token + '/sendMessage'
            data = {'chat_id': chat_id,
                    'text': 'Оп-оп! Живём-живём! Текущее место в рейтинге абитуриентов ' + ratingDate.lower() + ': ' + str(rating) + ' из ' + str(number) + '(+' + str(diff) + ')'}
            r = requests.post(url, data=data)
            print(r.status_code, r.reason)
        if diff == 0:
            url = 'https://api.telegram.org/bot' + tg_token + '/sendMessage'
            data = {'chat_id': chat_id,
                    'text': 'Ничего не изменилось.... с прошедшего дня... Текущее место в рейтинге абитуриентов ' + ratingDate.lower() + ': ' + str(rating) + ' из ' + str(number)}
            r = requests.post(url, data=data)
            print(r.status_code, r.reason)
    sendImage()  # If you have no need of the screenshot, you can comment this string
    before = ratingDate
    placement = rating
    browser.close()
    Timer(43200, ratingbot).start()  # Waiting 12 hours

try:
    ratingbot()
except:
    PROCNAME = "chrome"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()
    ratingbot()
