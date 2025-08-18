import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

from utilities import progress_bar


@dataclass
class ERPCredentials:
    netid: str
    password: str

    @classmethod
    def from_env(cls) -> "ERPCredentials":
        load_dotenv()
        netid = os.getenv("SNU_NETID")
        password = os.getenv("SNU_PASSWORD")

        if not netid or not password:
            raise ValueError(
                "Missing cresentials. Ensure SNU_NETID and SNU_PASSWORD are set in your environment variables or .env file."
            )

        return cls(netid=netid, password=password)


@dataclass
class BrowserOptions:
    binary: Optional[str]

    @classmethod
    def from_env(cls) -> "BrowserOptions":
        load_dotenv()
        binary = os.getenv("SELENIUM_BROWSER_BINARY")

        return cls(binary=binary)


class SNUERPScraper:
    LOGIN_URL = "https://prodweb.snu.in/psp/CSPROD/EMPLOYEE/HRMS/?cmd=login"
    WEEKLY_SCHEDULE_URL = "https://prodweb.snu.in/psc/CSPROD/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL"

    def __init__(self, headless: bool = True, timeout_sec: int = 15) -> None:
        self.timeout_sec = timeout_sec
        self.driver = self.__initialize_driver(headless)
        self.wait = WebDriverWait(self.driver, timeout=timeout_sec)

    def __initialize_driver(self, headless: bool) -> webdriver.Chrome:
        options = Options()

        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        browser_options = BrowserOptions.from_env()
        if bin := browser_options.binary:
            options.binary_location = bin

        return webdriver.Chrome(options=options)

    def __login(self, credentials: ERPCredentials) -> None:
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
            raise RuntimeError(
                "Login appears to have failed. Please check your credentials."
            )

    def __get_html(self) -> List[str]:
        self.driver.get(self.WEEKLY_SCHEDULE_URL)

        course_divs = self.driver.find_elements(
            By.CSS_SELECTOR, 'div[id*="DERIVED_REGFRM1_DESCR20"]'
        )
        if not course_divs:
            raise RuntimeError("Unable to grab course schedule divs")

        html_snippets = [cd.get_attribute("outerHTML") for cd in course_divs]
        return [h for h in html_snippets if h]

    def get_weekly_schedule_html(self) -> List[str]:
        progress_bar("Scraping ERP Data", 0, 1)
        try:
            credentials = ERPCredentials.from_env()
            self.__login(credentials)
            return self.__get_html()
        finally:
            self.driver.quit()
            progress_bar("Scraping ERP Data", 1, 1)


def main():
    """test the scraper"""
    try:
        scraper = SNUERPScraper(headless=False)
        schedule_html = scraper.get_weekly_schedule_html()
        print(schedule_html)
    except Exception as e:
        print(f"Error occured: {str(e)}")


if __name__ == "__main__":
    main()
