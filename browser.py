from itertools import cycle
from time import sleep

import pandas as pd
import logging
from io import BytesIO
from PIL import Image

from captcha_solver import CaptchaSolver
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


class Data:
    def __init__(self):
        url = ('https://docs.google.com/spreadsheets/d/1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZ'
               'bw/export?format=csv&id=1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZbw&gid=92476905')
        self.dataframe = pd.read_csv(url)

    def __call__(self, arg):
        value = self.dataframe[arg].dropna()
        return value


class Browser:
    def __init__(self):
        # self.driver = webdriver.Firefox(firefox_binary=r'C:\Users\KIEV-COP-4\AppData\Local\Mozilla Firefox\firefox.exe')
        options =  webdriver.ChromeOptions()
        options.add_argument('--proxy-server=109.248.7.161:11795')
        self.driver = webdriver.Chrome(options=options)

    def find_element(self, el_xpath):
        try:
            element = WebDriverWait(self.driver, 10).until(lambda d: self.driver.find_element_by_xpath(el_xpath))
            return element
        except Exception as error:
            logging.exception(error)
            return False

    def solve_captcha(self, captcha_element, file_name: str = 'captcha.png') -> str:
        location = captcha_element.location_once_scrolled_into_view
        size = captcha_element.size
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        im = Image.open(BytesIO(self.driver.get_screenshot_as_png()))
        im = im.crop((left, top, right, bottom))
        im.save(file_name)
        solver = CaptchaSolver('rucaptcha', api_key='42a3a6c8322f1bec4b5ba84b85fdbe2f')
        raw_data = open(file_name, 'rb').read()
        print('solving captcha')
        try:
            captcha_answer = solver.solve_captcha(raw_data, recognition_time=80)
            return captcha_answer
        except Exception as error:
            logging.exception(error)
            return ''

    def spam(self, title, description, contact, email):
        url = 'http://www.gowork.in.ua/dobavit-vakansiyu/'
        self.driver.get(url)
        self.find_element('//*/input[@name="your-email"]').send_keys(email)
        self.find_element('//*/input[@name="your-subject"]').send_keys(title)
        self.find_element('//*/textarea[@name="yslov"]').send_keys(description)
        self.find_element('//*/input[@name="contact"]').send_keys(contact)
        captcha_answer = self.solve_captcha(self.find_element('//*/img[@alt="captcha"]'))
        self.find_element('//*[@id="wpcf7-f67-p63-o1"]/form/p[6]/span/input').send_keys(captcha_answer)
        self.find_element('//*/input[@type="submit"]').click()
        sleep(10)


class Client:
    def __init__(self):
        self.data = Data()
        browser = Browser()
        title = cycle(self.data('title'))
        description = cycle(self.data('description'))
        contact = cycle(self.data('contact'))
        email = cycle(self.data('email'))
        while True:
            browser.spam(next(title), next(description), next(contact), next(email))


if __name__ == '__main__':
    Client()
