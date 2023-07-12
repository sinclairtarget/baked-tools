import os
import logging
import sys
from datetime import datetime

import gspread


JSON_KEYFILE_PATH_ENV_VAR = "GOOGLE_SERVICE_ACCOUNT_KEYFILE_PATH"
DEFAULT_PATH = "./service_account.json"


logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    def __init__(self):
        path = os.environ.get(JSON_KEYFILE_PATH_ENV_VAR) or DEFAULT_PATH

        try:
            self._g = gspread.service_account(filename=path)
        except FileNotFoundError as e:
            logger.error("Could not find service account JSON keyfile.")
            logger.error(f"Expected to find file at path: {SERVICE_ACCOUNT_JSON_KEYFILE_PATH}")
            raise GoogleCredentialsNotFoundError("Could not find JSON keyfile.")

    def sync_shots_to_spreadsheet(self, spreadsheet_id, shots):
        logger.info(f"Updating spreadsheet with ID {spreadsheet_id}...")

        try:
            spreadsheet = self._g.open_by_key(spreadsheet_id)
        except gspread.exceptions.SpreadsheetNotFound:
            msg = f"Spreadsheet not found with ID: {spreadsheet_id}"
            logger.error(msg)
            return False, msg
        except gspread.exceptions.APIError as e:
            try:
                status = e.response.json()["error"]["status"]
            except:
                status = "Unknown"

            msg = f"Got Google Sheets API error: {status}"
            logger.error(msg)
            return False, msg

        worksheet = spreadsheet.get_worksheet(1)

        # Clear the existing data from the worksheet
        worksheet.clear()

        # Populate the Google Sheet with the ShotGrid data
        header_row = [
            "Code",
            "Description",
            "Status",
            "Turnover Notes",
            "Delivery Notes",
        ]

        shot_rows = [
            [
                shot["code"],
                shot["description"],
                shot["sg_status_list"],
                shot["sg_turnover_notes"],
                shot["sg_delivery_notes"],
            ]
            for shot in shots
        ]

        # Add a timestamp to the bottom of the data
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        timestamp_row = ["", "", "", "", "", "", f"Last updated on {timestamp}"]

        worksheet.append_rows([header_row, *shot_rows, timestamp_row])
        return True, None
