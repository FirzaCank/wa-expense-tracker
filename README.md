# WhatsApp Expense Tracker

A Python-based WhatsApp expense tracker. Messages received via Twilio are parsed by Gemini AI and saved to Google Sheets.

## Architecture

```
WhatsApp → Twilio → POST /webhook (FastAPI) → Gemini API (parse)
                                             → Google Sheets (save)
                                             → WhatsApp (confirmation in Indonesian)
```

## File Structure

```
├── app.py               ← FastAPI webhook server (port 3000)
├── expense_parser.py    ← Expense parsing via Gemini API
├── sheets.py            ← Append data to Google Sheets
├── config.py            ← Load environment variables
├── requirements.txt     ← Python dependencies
├── .env.example         ← Credentials template
└── service_account.json ← (create yourself, never commit)
```

## Google Sheets Columns

| Tanggal | Jumlah (IDR) | Kategori | Deskripsi | Metode Pembayaran | Pesan Asli |

## System Dependencies

Beyond Python packages, you also need:

| Tool | Purpose | Install |
|------|---------|---------|
| **ngrok** | Expose local server to the internet for Twilio testing | `brew install ngrok` |

> ngrok is a CLI binary, not a Python package — it is intentionally absent from `requirements.txt`.

## Setup

### 1. Clone & install dependencies

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in .env with your credentials
```

### 3. Google Sheets API

1. Open [Google Cloud Console](https://console.cloud.google.com/) → create a new project
2. Enable **Google Sheets API** and **Google Drive API**
3. Create a **Service Account** → create a key → download the JSON file
4. Save the JSON file as `service_account.json` in the project root
5. Create a new Google Sheet and copy the **Spreadsheet ID** from the URL:
   `https://docs.google.com/spreadsheets/d/**SPREADSHEET_ID**/edit`
6. Share the sheet with the service account email (`client_email` in the JSON) with **Editor** role

### 4. Twilio WhatsApp

1. Sign up at [Twilio](https://www.twilio.com/) → activate the **WhatsApp Sandbox**
2. Copy **Account SID** and **Auth Token** into `.env`
3. Set the webhook URL to `https://your-domain.com/webhook` (method: POST)

### 5. Gemini API

1. Open [Google AI Studio](https://aistudio.google.com/apikey)
2. Create an API key → add it to `.env` as `GEMINI_API_KEY`

### 6. ngrok (for local testing)

```bash
# Install (macOS)
brew install ngrok

# Sign up for a free account at https://ngrok.com → Dashboard → copy your authtoken
ngrok config add-authtoken <your-authtoken>
```

> The authtoken is stored in `~/.config/ngrok/ngrok.yml` — you only need to run this once.

## Running the Server

### Development (with auto-reload)

```bash
make dev
# or: uvicorn app:app --reload --port 3000
```

### Production

```bash
make run
# or: uvicorn app:app --host 0.0.0.0 --port 3000 --workers 2
```

### Expose locally via ngrok

```bash
# In a separate terminal from the server
make ngrok
# or: ngrok http 3000
```

ngrok will display a public URL, e.g.:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:3000
```

Set that URL as your Twilio webhook:
```
https://abc123.ngrok-free.app/webhook
```

> ⚠️ The ngrok URL changes on every restart (free plan). For a permanent URL, upgrade to ngrok paid or deploy to Render.

## Makefile Shortcuts

| Command | Description |
|---------|-------------|
| `make dev` | Start server with auto-reload |
| `make run` | Start production server |
| `make install` | Create venv and install dependencies |
| `make kill` | Free port 3000 |
| `make test-health` | Check health endpoint |
| `make test-parse` | Test expense parsing |
| `make ngrok` | Expose port via ngrok |
| `make freeze` | Update requirements.txt |

## Example Messages

Send these to your Twilio WhatsApp number:

```
Makan siang warteg 15rb cash
Grab ke kantor 25000 gopay
Belanja Indomaret 320ribu debit
Netflix 54rb kartu kredit kemarin
Bayar listrik 180000 transfer
```

The bot replies in Indonesian with a summary of the recorded expense.

## Health Check

```
GET http://localhost:3000/health
```

## Test Parsing (no Twilio required)

```bash
make test-parse
# or:
curl -X POST http://localhost:3000/test/parse \
  -H "Content-Type: application/json" \
  -d '{"message": "Makan siang warteg 15rb cash"}'
```

