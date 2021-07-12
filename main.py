import csv
import os
from time import sleep

from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import \
    presence_of_element_located
from selenium.webdriver.support.ui import WebDriverWait

URL_WEBMASTER = 'https://webmaster.yandex.ru/sites/'
URL_ADD_HOST = 'https://webmaster.yandex.ru/sites/add/'
WAIT_SEC = 60


def get_driver() -> webdriver.Chrome:
    try:
        driver = webdriver.Chrome(executable_path=os.path.join(os.getcwd(), 'chromedriver'))
    except WebDriverException:
        driver = webdriver.Chrome(executable_path=os.path.join(os.getcwd(), 'chromedriver.exe'))
    return driver


def login_web_master(driver: webdriver.Chrome, login: str, pswrd: str):
    wait = WebDriverWait(driver, WAIT_SEC)
    driver.get(URL_WEBMASTER)
    login_field = wait.until(presence_of_element_located((By.XPATH, ".//input[@name='login']")))
    login_field.send_keys(login + Keys.RETURN)
    pass_field = wait.until(presence_of_element_located((By.XPATH, ".//input[@name='passwd']")))
    pass_field.send_keys(pswrd + Keys.RETURN)
    wait.until(presence_of_element_located((By.XPATH, ".//div[@class='Header-User']")))


def add_host(driver: webdriver.Chrome, host: str):
    wait = WebDriverWait(driver, WAIT_SEC)
    driver.get(URL_ADD_HOST)
    host_field = wait.until(presence_of_element_located((By.XPATH, ".//input[@name='hostName']")))
    host_field.send_keys(host + Keys.RETURN)
    verify_button = wait.until(
        presence_of_element_located((By.CSS_SELECTOR, '.verification__verify'))
    )
    verify_button.click()
    wait.until(presence_of_element_located((By.CSS_SELECTOR, '.luna-table__delete')))


def add_region(driver: webdriver.Chrome, host: str, region: str):
    wait = WebDriverWait(driver, WAIT_SEC)
    link = wait.until(
        presence_of_element_located((By.XPATH, ".//a[contains(@href,'/info/regions/')]"))
    )
    driver.get(link.get_attribute('href'))
    edit_btn = wait.until(
        presence_of_element_located((By.CSS_SELECTOR, '.regions-webmaster__edit-button'))
    )
    edit_btn.click()
    region_info_host_field = wait.until(
        presence_of_element_located((By.CSS_SELECTOR, '.input__control'))
    )
    region_info_host_field.send_keys(host)
    add_btn = wait.until(
        presence_of_element_located((By.CSS_SELECTOR, '.regions-select__add-button'))
    )
    add_btn.click()
    region_field = wait.until(
        presence_of_element_located((By.XPATH, ".//input[@aria-autocomplete='list']"))
    )
    region_field.click()
    region_field.send_keys(f'  {region}')
    sleep(2)
    region_field.send_keys(Keys.ARROW_DOWN)
    region_field.send_keys(Keys.RETURN)
    save_btn = wait.until(
        presence_of_element_located((By.CSS_SELECTOR, '.regions-webmaster__save-button'))
    )
    save_btn.click()
    wait.until(presence_of_element_located((By.CSS_SELECTOR, '.regions__moderation-action')))


def add_hosts_with_region(driver, hosts):
    result_csv = []
    for city, host, *tail_status in hosts:
        if tail_status:
            status = tail_status[0]
        else:
            status = None

        if status is None or status != 'err':
            try:
                add_host(driver, host)
                add_region(driver, host, city)
            except Exception:
                logger.error(host)
                status = 'err'
                continue
            else:
                status = 'done'
            finally:
                result_csv.append([city, host, status])
        else:
            result_csv.append([city, host, status])
    return result_csv


@logger.catch
def run():
    with get_driver() as driver:
        with open('hosts.csv', 'r') as hosts_file:
            hosts = csv.reader(hosts_file)
            login, pswrd, *_tail = hosts.__next__()
            login_web_master(driver, login, pswrd)
            result_csv = [[login, pswrd]]
            result_csv.extend(add_hosts_with_region(driver, hosts))
    with open('hosts.csv', 'w') as result_file:
        writer = csv.writer(result_file)
        writer.writerows(result_csv)


if __name__ == '__main__':
    run()
