import os
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from dotenv import load_dotenv

@dataclass
class ERPCredentials:
    netid: str
    password: str

    @classmethod
    def from_env(cls) -> 'ERPCredentials':
        load_dotenv()
        netid = os.getenv("SNU_NETID")
        password = os.getenv("SNU_PASSWORD")

        if not netid or not password:
            raise ValueError("Missing cresentials. Ensure SNU_NETID and SNU_PASSWORD are set in your environment variables or .env file.")
    
        return cls(netid=netid, password=password)

class SNUERPScraper:
    # url constants
    LOGIN_URL = "https://prodweb.snu.in/psp/CSPROD/EMPLOYEE/HRMS/?cmd=login"
    WEEKLY_SCHEDULE_URL = "https://prodweb.snu.in/psp/CSPROD_1/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_SCHD_W"
    
    def __init__(self, headless: bool = True, timeout_sec: int = 15) -> None:
        self.timeout_sec = timeout_sec
        self.driver = self._initialize_driver(headless)
        self.wait = WebDriverWait(self.driver, timeout=timeout_sec)

    def _initialize_driver(self, headless: bool) -> webdriver.Chrome:
        options = Options()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(options=options)

    def _login(self, credentials: ERPCredentials) -> None:
        self.driver.get(self.LOGIN_URL)

        netid_input = self.driver.find_element(By.ID, "userid")
        password_input = self.driver.find_element(By.ID, "pwd")
        submit_button = self.driver.find_element(By.CLASS_NAME, "psloginbutton")
        
        netid_input.clear()
        netid_input.send_keys(credentials.netid)
        password_input.clear()
        password_input.send_keys(credentials.password)
        submit_button.click()

        try:
            self.wait.until(lambda driver: driver.current_url != self.LOGIN_URL)
        except TimeoutException:
            raise RuntimeError("Login appears to have failed. Please check your credentials.")
    
    def _get_schedule_html(self) -> str:
        self.driver.get(self.WEEKLY_SCHEDULE_URL)
        self.driver.switch_to.frame(self.driver.find_element(By.ID, "ptifrmtgtframe"))

        schedule_html = self.driver.find_element(By.ID, "WEEKLY_SCHED_HTMLAREA")
        if schedule_html is None:
            raise RuntimeError("Unable to grab weekly schedule html.")
        return schedule_html.get_attribute("outerHTML")

    def get_weekly_schedule_html(self) -> str:
        try:
            credentials = ERPCredentials.from_env()
            self._login(credentials)
            return self._get_schedule_html()
        finally:
            self.driver.quit()
    
def main():
    """test the scraper"""
    try:
        scraper = SNUERPScraper(headless=False)
        schedule_html = scraper.get_weekly_schedule_html()
        print(schedule_html[:500] + "...")
    except Exception as e:
        print(f"Error occured: {str(e)}")

if __name__ == "__main__":
    main()