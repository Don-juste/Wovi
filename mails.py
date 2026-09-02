from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv
load_dotenv()
import os

config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)

fm = FastMail(config)


async def envoyer_otp(email: str, code: str):
    message = MessageSchema(
        subject="Mobile Money - Votre code de connexion",
        recipients=[email],
        body=f"""
        <html>
        <body>
            <h2>Code de vérification</h2>
            <p>Votre code OTP : <strong>{code}</strong></p>
            <p>Il expire dans 5 minutes.</p>
        </body>
        </html>
        """,
        subtype="html"
    )
    await fm.send_message(message)