from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from .errors import InvalidCredentialsError

from random import randint


class _Token:
    @staticmethod
    def obtain(login, password) -> str:
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)
        wait = WebDriverWait(driver, 10)
        driver.get(
            'https://login.mos.ru/sps/login/methods/password?bo=%2Fsps%2Foauth%2Fae%3Fresponse_type%3Dcode%26access_type%3Doffline%26client_id%3Ddnevnik.mos.ru%26scope%3Dopenid%2Bprofile%2Bbirthday%2Bcontacts%2Bsnils%2Bblitz_user_rights%2Bblitz_change_password%26redirect_uri%3Dhttps%253A%252F%252Fschool.mos.ru%252Fv3%252Fauth%252Fsudir%252Fcallback%26state%3D')

        login_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#login')))
        password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#password')))

        login_input.send_keys(login)
        password_input.send_keys(password)

        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#bind')))
        sleep(randint(10, 15) / 10)
        button.click()

        data = driver.get_cookie("aupd_token")
        driver.close()
        if data:
            return data["value"]
        raise InvalidCredentialsError
