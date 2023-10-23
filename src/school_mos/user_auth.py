from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from .errors import InvalidCredentialsError


class _Token:
    @staticmethod
    def obtain(login, password) -> str:
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(options=options)

        driver.get(
            'https://login.mos.ru/sps/login/methods/password?bo=%2Fsps%2Foauth%2Fae%3Fresponse_type%3Dcode%26access_type%3Doffline%26client_id%3Ddnevnik.mos.ru%26scope%3Dopenid%2Bprofile%2Bbirthday%2Bcontacts%2Bsnils%2Bblitz_user_rights%2Bblitz_change_password%26redirect_uri%3Dhttps%253A%252F%252Fschool.mos.ru%252Fv3%252Fauth%252Fsudir%252Fcallback%26state%3D')
        sleep(2)

        login_input = driver.find_element(By.XPATH, '//*[@id="login"]')
        login_input.send_keys(login)
        password_input = driver.find_element(By.XPATH, '//*[@id="password"]')
        password_input.send_keys(password)

        button = driver.find_element(By.XPATH, '//*[@id="bind"]')
        button.click()
        sleep(1)
        data = driver.get_cookie("aupd_token")
        driver.close()
        if data:
            return data["value"]
        raise InvalidCredentialsError()
