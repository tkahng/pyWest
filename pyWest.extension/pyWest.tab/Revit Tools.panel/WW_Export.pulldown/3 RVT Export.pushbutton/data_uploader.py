import logging
import os
import sys
import pickle

import gspread
import google_auth

logger = logging.getLogger(__name__)

# TODO: clean up wrappers
# TODO: refactor


class WorkSheet:
    def __init__(self, google_client, key):
        self.worksheet = google_client.open_by_key(key)

    def get_sheets(self):
        """ Returns dictionary {'sheet_name': sheet_object, ... """
        self.sheet_list = self.worksheet.worksheets()
        self.sheet_dict = {}
        for sheet in self.sheet_list:
            self.sheet_dict[sheet.title] = sheet
        return self.sheet_dict

    def create_sheet(self, title="NoName", rows=1, cols=1):
        new_sheet = None
        try:
            new_sheet = self.worksheet.add_worksheet(title=title, rows=rows, cols=cols)
        except AttributeError as err:
            if str(err) == "'HTTPError' object has no attribute 'read'":
                logger.error("Sheet Already exists. Title: %s", title)
            else:
                logger.error("Unexpected error: %s", sys.exc_info())
        return new_sheet


class Sheet:
    def __init__(self, worksheet, data, title="None"):
        self.worksheet = worksheet
        self.title = title
        self.data = data
        self.cols = max([len(row) for row in data])
        self.rows = len(data)
        if self.title in self.worksheet.get_sheets().keys():
            self.sheet = self.worksheet.sheet_dict[self.title]
            self.worksheet.worksheet.del_worksheet(self.sheet)

        self.sheet = self.worksheet.create_sheet(title=self.title, rows=1, cols=self.cols)
        self.sheet.resize(cols=self.cols, rows=self.rows)

        for i in range(0, self.rows):
            if len(data[i]) < self.cols:
                n = self.cols - len(data[i])
                data[i].extend([""] * n)
            else:
                continue

        sheet_range = self.sheet.range(1, 1, self.rows, self.cols)
        for cell in sheet_range:
            cell.value = self.data[cell.row - 1][cell.col - 1]
        self.cells = sheet_range

    def batch_write(self):
        self.sheet.update_cells(self.cells)

    def write_data(self):
        """ Appends Data """
        for n, row in enumerate(self.data, 1):
            self.sheet.insert_row(row, index=n)


if __name__ == "__main__":
    credentials = google_auth.get_credentials()
    client = gspread.authorize(credentials)
    _script, key, csv_path = sys.argv
    title = os.path.basename(csv_path)

    with open(csv_path, "rb") as fp:
        data = pickle.load(fp)

    # key = '1E5x6yNXZHwc6pd3hkEk4JzB2bUmwTGsRHWqewiJWcd4'
    worksheet = WorkSheet(client, key)
    sheet = Sheet(worksheet, data, title=title)
    sheet.batch_write()
