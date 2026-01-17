from bs4 import BeautifulSoup, Tag
from pathlib import Path
from typing import Final, List, Union, cast

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from config.app_config import AppConfig, ERPCredentials

APP_CONFIG = AppConfig.from_toml()


class SNUERPScraper:
    LOGIN_URL: Final[str] = "https://prodweb.snu.in/psp/CSPROD/EMPLOYEE/HRMS/?cmd=login"
    WEEKLY_SCHEDULE_URL: Final[str] = (
        "https://prodweb.snu.in/psc/CSPROD/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL"
    )

    def __init__(
        self,
        headless: bool = APP_CONFIG.RUN_HEADLESS_BROWSER_INSTANCE,
        timeout_sec: int = 15,
    ) -> None:
        self.timeout_sec = timeout_sec
        self.driver = self._create_driver(headless)
        self.wait = WebDriverWait(self.driver, timeout=timeout_sec)

    def _create_driver(self, headless: bool) -> webdriver.Chrome:
        options = Options()
        if headless:
            options.add_argument("--headless=new")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        return webdriver.Chrome(options)

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
        except TimeoutException as exc:
            raise RuntimeError("Login failed. Please verify your credentials.") from exc

    def _get_course_divs(self) -> List[str]:
        self.driver.get(self.WEEKLY_SCHEDULE_URL)

        course_divs = self.driver.find_elements(
            By.CSS_SELECTOR, 'div[id*="DERIVED_REGFRM1_DESCR20"]'
        )
        if not course_divs:
            raise RuntimeError("Unable to grab course schedule divs")

        html_snippets = [cd.get_attribute("outerHTML") for cd in course_divs]
        return [h for h in html_snippets if h]

    def get_weekly_schedule_html(self) -> List[str]:
        try:
            credentials = ERPCredentials.from_env()
            self._login(credentials)
            return self._get_course_divs()
        finally:
            self.driver.quit()


def write_weekly_schedule_to_html(
    weekly_schedule: List[str], path: Union[str, Path]
) -> None:
    if isinstance(path, str):
        path = Path(path)

    path.parent.mkdir(parents=True, exist_ok=True)

    soup = BeautifulSoup("<html><body></body></html>", "html.parser")
    body = cast(Tag, soup.body)

    for raw_html in weekly_schedule:
        fragment = BeautifulSoup(raw_html, "html.parser")
        body.append(fragment)

    pretty_html = soup.prettify()
    path.write_text(pretty_html, encoding="utf-8")


def test():
    try:
        scraper = SNUERPScraper(headless=False)
        schedule_html = scraper.get_weekly_schedule_html()
        print(schedule_html[0])
        write_weekly_schedule_to_html(
            schedule_html, "data/sample/sample-weekly-sched.html"
        )
        print("Saved to 'data/sample/sample-weekly-sched.html'")
    except Exception as e:
        print(f"Error occured: {str(e)}")


if __name__ == "__main__":
    test()
