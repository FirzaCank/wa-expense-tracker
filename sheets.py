import gspread
from google.oauth2.service_account import Credentials

from config import Config

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADERS = ["Tanggal", "Jumlah (IDR)", "Kategori", "Deskripsi", "Metode Pembayaran", "Pesan Asli"]


def _get_worksheet() -> gspread.Worksheet:
    """Authenticate and return the first worksheet of the configured spreadsheet.
    
    Supports both local file path and base64-encoded JSON from environment.
    """
    service_account_path = Config.get_service_account_path()
    credentials = Credentials.from_service_account_file(
        service_account_path, scopes=SCOPES
    )
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(Config.GOOGLE_SHEETS_ID)
    worksheet = spreadsheet.sheet1

    # Write headers if the sheet is empty or headers differ
    first_row = worksheet.row_values(1)
    if first_row != HEADERS:
        worksheet.update("A1", [HEADERS])
        # Bold the header row
        worksheet.format("A1:F1", {"textFormat": {"bold": True}})

    return worksheet


def append_expense(expense: dict, raw_message: str) -> int:
    """Append one expense row. Returns the new row number."""
    worksheet = _get_worksheet()

    row = [
        expense.get("date", ""),
        expense.get("amount", ""),
        expense.get("category", ""),
        expense.get("description", ""),
        expense.get("payment_method", ""),
        raw_message,
    ]

    worksheet.append_row(row, value_input_option="USER_ENTERED")
    return len(worksheet.get_all_values())
