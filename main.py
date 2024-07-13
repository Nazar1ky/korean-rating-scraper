import json
from datetime import UTC, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from files import Files

WEBSITE = "https://www.grac.or.kr/Statistics/SelfRateGameStatistics.aspx"

class Scraper:
    def __init__(self) -> None:
        self._session = requests.session()

        self._session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        })

    def get_data(self, rating: str = ""):
        files = Files(
            rating=rating,
            start_date="2000-01-01",
            end_date=datetime.now(tz=UTC).strftime("%Y-%m-%d"),
        )

        print("Requesting pages and view_state...")

        data_soup = self.get_page_soup(files.get_files())

        page_count = self.get_page_count(data_soup)
        view_state = self.get_view_state(data_soup)

        files.view_state = view_state

        print(f"Pages: {page_count}")

        data = []

        for page in range(page_count):
            print(f"Processing {page+1}/{page_count}")

            files.page = str(page)

            soup = self.get_page_soup(files.get_files())

            data.extend(self.parse_page(soup))

        return data

    def get_page_soup(self, files: dict | None = None) -> BeautifulSoup:
        response = self._session.post(WEBSITE, files=files)

        soup = BeautifulSoup(response.text, "lxml")

        return soup

    def get_page_count(self, soup: BeautifulSoup) -> int:
        pagination = soup.find("div", class_="pagination")

        if not pagination:
            raise RuntimeError("Pagination not founded")

        buttons = pagination.find_all("a")

        if not buttons:
            raise RuntimeError(f"Buttons not founded in pagination: {pagination}")

        href = buttons[-1].get("href")

        if not href:
            raise RuntimeError(f"In button not founded href. Button: {buttons[-1]} Pagination: {pagination}")

        # Example how href look: javascript:__doPostBack('ctl00$ContentHolder$listPager','83')
        page_count = int(
            href.split("'")[-2].split("'")[0],
        )

        return page_count

    # Reference: https://stackoverflow.com/a/73239931
    def get_hidden_input(self, soup: BeautifulSoup) -> dict:
        tags = {}

        hidden_tags = soup.find_all(
            "input",
            type="hidden",
        )

        for tag in hidden_tags:
            tags[tag.get("name")] = tag.get("value")

        return tags

    def get_view_state(self, soup: BeautifulSoup) -> str:
        hidden_inputs = self.get_hidden_input(soup)

        if not hidden_inputs.get("__VIEWSTATE"):
            raise KeyError(f"Can't find __VIEWSTATE in {hidden_inputs}")

        return hidden_inputs["__VIEWSTATE"]

    def parse_page(self, soup: BeautifulSoup) -> list[dict]:
        products = soup.select("tr[id^=ctl00_ContentHolder_rptGradeDoc]")

        if not products:
            raise RuntimeError("No products on page")

        data = []

        for product in products:
            product_td = product.find_all("td")

            product_number = product_td[0].text.strip()
            product_name = product_td[1].text.strip()
            product_date = product_td[2].text.strip()
            product_rating_img = product_td[4].find("img").get("src")

            product_data = {
                "product_number": product_number,
                "product_name": product_name,
                "product_date": product_date,
                "product_rating_img": product_rating_img,
            }

            data.append(product_data)

        return data

def save_data_to_json(filename: str, data: list[dict]) -> None:
    with Path(f"{filename}.json").open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def save_data_to_txt(filename: str, data: list[dict]) -> None:
    text = []

    column1 = max([len(product["product_number"]) for product in data])
    column2 = max([len(product["product_name"]) for product in data])
    column3 = max([len(product["product_date"]) for product in data])
    column4 = max([len(product["product_rating_img"]) for product in data])

    separator = "  |  "

    for product in data:
        text.append(f"{product["product_number"]:<{column1}}{separator}")
        text.append(f"{product["product_name"]:<{column2}}{separator}")
        text.append(f"{product["product_date"]:<{column3}}{separator}")
        text.append(f"{product["product_rating_img"]:<{column4}}\n")

    with Path(f"{filename}.txt").open("w", encoding="utf-8") as file:
        file.write("".join(text))

def main():
    app = Scraper()

    # I use EPIC but you can edit to any you want
    data = app.get_data("epic")

    save_data_to_json("data", data)
    save_data_to_txt("data", data)

if __name__ == "__main__":
    main()
