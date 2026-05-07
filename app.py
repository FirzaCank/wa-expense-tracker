"""
WhatsApp Expense Tracker – FastAPI webhook server.
Receives WhatsApp messages via Twilio, parses them with Gemini,
and saves the result to Google Sheets.
"""

import locale
import logging

import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import Response
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from config import Config
from expense_parser import parse_expense
from sheets import append_expense

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="WA Expense Tracker", version="2.0.0")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_twilio(request: Request, form_data: dict) -> None:
    """Raise HTTP 403 if the Twilio request signature is invalid.

    When behind a proxy (ngrok, Render, etc.), reconstruct the public URL
    from X-Forwarded-Proto / X-Forwarded-Host headers so it matches the URL
    Twilio used when computing the signature.
    """
    if Config.SKIP_TWILIO_VALIDATION:
        logger.warning("Twilio signature validation SKIPPED (dev mode)")
        return

    validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)
    signature = request.headers.get("X-Twilio-Signature", "")

    # Reconstruct the public-facing URL Twilio signed against
    proto = request.headers.get("X-Forwarded-Proto", request.url.scheme)
    host = request.headers.get(
        "X-Forwarded-Host",
        request.headers.get("host", request.url.netloc),
    )
    public_url = f"{proto}://{host}{request.url.path}"

    if not validator.validate(public_url, form_data, signature):
        logger.warning(
            "Invalid Twilio signature from %s (validated url: %s)",
            request.client.host,
            public_url,
        )
        raise HTTPException(status_code=403, detail="Unauthorized")


def _format_idr(amount) -> str:
    """Format a number as IDR string, e.g. 50000 → 'Rp 50.000'."""
    try:
        return f"Rp {int(float(amount)):,}".replace(",", ".")
    except (TypeError, ValueError):
        return str(amount)


def _build_success_reply(expense: dict, row_num: int) -> str:
    return (
        f"*Pengeluaran Tercatat!*\n\n"
        f"Tanggal     : {expense.get('date')}\n"
        f"Jumlah      : {_format_idr(expense.get('amount'))}\n"
        f"Kategori    : {expense.get('category')}\n"
        f"Deskripsi   : {expense.get('description')}\n"
        f"Pembayaran  : {expense.get('payment_method')}\n\n"
        f"_(Baris #{row_num} di Google Sheets)_"
    )


HELP_TEXT = (
    "*Pencatat Pengeluaran WhatsApp*\n\n"
    "Kirim pesan pengeluaranmu dalam bahasa alami!\n\n"
    "*Contoh:*\n"
    "• Makan siang warteg 15rb cash\n"
    "• Grab ke kantor 25000 gopay\n"
    "• Belanja bulanan Indomaret 320ribu debit\n"
    "• Netflix 54rb kartu kredit kemarin\n\n"
    "*Kategori:* Food · Transport · Shopping · Bills · Entertainment · Other\n"
    "*Pembayaran:* Cash · Transfer · Credit Card · Debit Card · E-Wallet · Other\n\n"
    "Ketik *bantuan* atau *help* untuk pesan ini."
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.post("/webhook", summary="Twilio WhatsApp webhook")
async def webhook(
    request: Request,
    Body: str = Form(default=""),
    From: str = Form(default=""),
):
    """Receive a WhatsApp message from Twilio, parse it, and save to Sheets."""
    # Validate Twilio signature before processing
    form_data = dict(await request.form())
    _validate_twilio(request, form_data)

    incoming_msg = Body.strip()
    logger.info("Incoming message from %s: %s", From, incoming_msg)

    resp = MessagingResponse()
    msg = resp.message()

    # Guard: empty message
    if not incoming_msg:
        msg.body(
            "Halo! Kirimkan pesan pengeluaranmu.\n"
            "Contoh: _Makan siang 25rb cash_\n\n"
            "Ketik *bantuan* untuk panduan lengkap."
        )
        return Response(content=str(resp), media_type="application/xml")

    # Help command
    if incoming_msg.lower() in ("help", "bantuan", "?"):
        msg.body(HELP_TEXT)
        return Response(content=str(resp), media_type="application/xml")

    try:
        expense = parse_expense(incoming_msg)
        logger.info("Parsed expense: %s", expense)

        row_num = append_expense(expense, incoming_msg)
        logger.info("Saved to row %d", row_num)

        msg.body(_build_success_reply(expense, row_num))

    except Exception as exc:
        logger.error("Failed to process message: %s", exc, exc_info=True)
        msg.body(
            "❌ Maaf, aku tidak bisa memproses pesanmu.\n\n"
            "Coba tulis lebih jelas, misalnya:\n"
            "_Kopi Starbucks 65rb kartu kredit_"
        )

    return Response(content=str(resp), media_type="application/xml")


@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "wa-expense-tracker"}


@app.post("/test/parse", summary="Test parsing only (no Twilio, no Sheets)")
async def test_parse(body: dict):
    """Debug endpoint — parse a message without Twilio validation or Sheets write."""
    message = body.get("message", "")
    if not message:
        raise HTTPException(status_code=400, detail="'message' field is required")
    expense = parse_expense(message)
    return {"input": message, "parsed": expense}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=Config.PORT, reload=True)
