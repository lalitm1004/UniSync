import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from dotenv import load_dotenv

class Scraper:
    def __init__(self, headless: bool = True) -> None:
        
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 15)

    def get_weekly_schedule_html(self) -> str:
        self.__login_erp()
        html = self.__scrape_weekly_schedule_html()
        self.driver.quit()
        return html


    def __login_erp(self) -> None:
        load_dotenv()
        LOGIN_URL = "https://prodweb.snu.in/psp/CSPROD/EMPLOYEE/HRMS/?cmd=login"

        self.driver.get(LOGIN_URL)
        
        netid_input = self.driver.find_element(By.ID, "userid")
        netid_input.clear()
        netid_input.send_keys(os.getenv("SNU_NETID"))
        
        password_input = self.driver.find_element(By.ID, "pwd")
        password_input.clear()
        password_input.send_keys(os.getenv("SNU_PASSWORD"))

        submit_button = self.driver.find_element(By.CLASS_NAME, "psloginbutton")
        submit_button.click()

    def __scrape_weekly_schedule_html(self) -> str:
        WEEKLY_SCHEDULE_URL = "https://prodweb.snu.in/psp/CSPROD_1/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_SCHD_W"
        
        self.driver.get(WEEKLY_SCHEDULE_URL)
        self.driver.switch_to.frame(self.driver.find_element(By.ID, "ptifrmtgtframe"))

        schedule_html = self.driver.find_element(By.ID, "WEEKLY_SCHED_HTMLAREA")
        return schedule_html.get_attribute("outerHTML")

if __name__ == "__main__":
    scraper = Scraper(headless=False)
    print(scraper.get_weekly_schedule_html())