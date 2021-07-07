# -*- coding: utf-8 -*-
from threading import Timer

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


def ratingbot():
    Token = 'tg_token'
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--hide-scrollbars')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    browser.get('rating_url')
    element = browser.find_element_by_xpath('xpath_of_the_specialty')
    actions = ActionChains(browser)
    actions.move_to_element(element).perform()
    browser.execute_script("window.scrollBy(100, 550);")
    el = browser.find_element_by_xpath('xpath_of_the_student')
    el.click()
    browser.save_screenshot('screenie.png')
    browser.close()

    def sendImage():
        url = 'https://api.telegram.org/bot' + Token + '/sendPhoto'
        files = {'photo': open('screenie.png', 'rb')}
        data = {'chat_id': "chat_id"}
        r = requests.post(url, files=files, data=data)
        print(r.status_code, r.reason, r.content)

    sendImage()
    Timer(86400000, ratingbot).start()
    
Timer(19500, ratingbot).start()
