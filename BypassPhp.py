import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def get_cookie():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        # service = Service(executable_path='/root/idisBot/chromedriver')
        # driver = webdriver.Chrome(service=service,options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)

        driver.get("https://idp.ieml.ru/module.php/core/loginuserpass.php?AuthState=_4f38cd4e83ed20651d74b64bdc83414540946e8fbf%3Ahttps%3A%2F%2Fidp.ieml.ru%2Fsaml2%2Fidp%2FSSOService.php%3Fspentityid%3Didis.ieml.ru%26cookieTime%3D1725699136%26RelayState%3D%252FEducation%252Fprotected%252F")

        time.sleep(3)

        username_input = driver.find_element("id", "username")
        password_input = driver.find_element("id", "password")

        username_input.send_keys("") # login
        password_input.send_keys("") # password

        time.sleep(0.5)

        submit_button = driver.find_element("class name", "btn.btn-primary.submit.btn-ieml")
        submit_button.click()

        time.sleep(3)

        cookies = driver.get_cookies()

        cookie_str = ""
        for cookie in cookies:
            cookie_str += f"{cookie['name']}={cookie['value']}; "

        with open('data.json', 'r+', encoding='utf-8') as file:
            data = json.load(file)
            data["config"]["cookie"] = cookie_str
            file.seek(0)
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.truncate()

        driver.quit()
    except Exception as err:
        print(err)
        return [False, err]
    return [True,"Succes"]
