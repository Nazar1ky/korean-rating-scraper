import json

import requests
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        self.session = requests.session()
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "uk-UA,uk;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.grac.or.kr",
            "Origin": "https://www.grac.or.kr",
            "Referer": "https://www.grac.or.kr/Statistics/SelfRateGameStatistics.aspx",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        self.session.headers.update(headers)

    # Reference: https://stackoverflow.com/a/73239931
    def get_hidden_input(self, content):
        tags = {}
        soup = BeautifulSoup(content, "html.parser")
        hidden_tags = soup.find_all("input", type="hidden")

        for tag in hidden_tags:
            tags[tag.get("name")] = tag.get("value")

        return tags

    def get_form_args(self):
        response = self.session.get("https://www.grac.or.kr/Statistics/SelfRateGameStatistics.aspx")
        self.view_state = self.get_hidden_input(response.content)["__VIEWSTATE"]

    def get_data(self):
        total_data = []
        current_page = 0
        pages = 0

        while current_page <= pages:
            print(f"Working on {current_page}/{pages}")

            files = {
                "__EVENTTARGET": (None, "ctl00$ContentHolder$listPager"),
                "__EVENTARGUMENT": (None, str(current_page)),
                "__VIEWSTATE": (None, self.view_state),
                "ctl00$totalSearch": (None, ""),
                "ctl00$ContentHolder$tbGameTitle": (None, ""),
                "ctl00$ContentHolder$ddlGrade": (None, ""),
                "ctl00$ContentHolder$tbRatingNbr": (None, "EPIC"),
                "ctl00$ContentHolder$CalendarPicker$txtCalStartDate": (None, "2000-01-01"),
                "ctl00$ContentHolder$CalendarPicker$txtCalEndDate": (None, "2024-05-12"),
                "ctl00$ContentHolder$CalendarPicker$ajxMaskStartDate_ClientState": (None, ""),
                "ctl00$ContentHolder$CalendarPicker$ajxMaskEndDate_ClientState": (None, ""),
                "ctl00$ContentHolder$Evaluation$rbSatisfy4": (None, "rbSatisfy4"),
                "ctl00$ContentHolder$Evaluation$taContents": (None, ""),
            }

            response = self.session.post("https://www.grac.or.kr/Statistics/SelfRateGameStatistics.aspx", files=files)

            # self.save_content(response.content)
            data, pages = self.parse_page(response.content)
            total_data.extend(data)

            current_page += 1

        self.save_data_to_json(total_data)
        self.save_data_to_txt(total_data)

    def save_content(self, content):
        with open("index.html", "wb") as file:
            file.write(content)

    def parse_page(self, content):
        soup = BeautifulSoup(content, "lxml")

        products = soup.select("tr[id^=ctl00_ContentHolder_rptGradeDoc]")

        if not products:
            print("No products.")
            return None

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

        pagination = soup.find("div", class_ = "pagination")
        page_count = int(pagination.find_all("a")[-1].get("href").split("'")[3].split("'")[0])

        return data, page_count

    def save_data_to_json(self, data):
        with open("data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def save_data_to_txt(self, data):
        text = ""

        column1 = max([len(product["product_number"]) for product in data])
        column2 = max([len(product["product_name"]) for product in data])
        column3 = max([len(product["product_date"]) for product in data])
        column4 = max([len(product["product_rating_img"]) for product in data])

        for product in data:
            text += f"{product["product_number"]:<{column1}}  |  "

            text += f"{product["product_name"]:<{column2}}  |  "

            text += f"{product["product_date"]:<{column3}}  |  "

            text += f"{product["product_rating_img"]:<{column4}}\n"

        with open("data.txt", "w", encoding="utf-8") as file:
            file.write(text)

if __name__ == "__main__":
    app = Scraper()
    app.get_form_args()
    app.get_data()
