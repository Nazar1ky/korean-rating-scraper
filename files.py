from dataclasses import dataclass


@dataclass
class Files:
    view_state: str = ""
    page: str = "0"
    game_title: str = ""
    grade: str = ""
    rating: str = ""
    start_date: str = "2000-01-01"
    end_date: str = ""

    def get_files(self) -> dict:
        files = {
            "__EVENTTARGET": (None, "ctl00$ContentHolder$listPager"),
            "__EVENTARGUMENT": (None, self.page),
            "__VIEWSTATE": (None, self.view_state),
            "ctl00$totalSearch": (None, ""),
            "ctl00$ContentHolder$tbGameTitle": (None, self.game_title),
            "ctl00$ContentHolder$ddlGrade": (None, self.grade),
            "ctl00$ContentHolder$tbRatingNbr": (None, self.rating),
            "ctl00$ContentHolder$CalendarPicker$txtCalStartDate": (
                None,
                self.start_date,
            ),
            "ctl00$ContentHolder$CalendarPicker$txtCalEndDate": (
                None,
                self.end_date,
            ),
            "ctl00$ContentHolder$CalendarPicker$ajxMaskStartDate_ClientState": (
                None,
                "",
            ),
            "ctl00$ContentHolder$CalendarPicker$ajxMaskEndDate_ClientState": (
                None,
                "",
            ),
            "ctl00$ContentHolder$Evaluation$rbSatisfy4": (None, "rbSatisfy4"),
            "ctl00$ContentHolder$Evaluation$taContents": (None, ""),
        }

        return files
