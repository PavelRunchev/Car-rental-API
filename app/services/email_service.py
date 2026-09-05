import os
from typing import cast
import resend
from app.models.user import User
from app.models.reservation import Reservation

resend.api_key = os.getenv("RESEND_API_KEY")

def send_account_activation_email(user: User,token: str,reservation: Reservation) -> None:
    frontend_url = os.getenv("FRONTEND_URL")
    if not frontend_url:
        raise RuntimeError("FRONTEND_URL is not configured.")

    activation_link = f"{frontend_url}/activate-account?token={token}"

    email = {
        "from": "Car Rental <onboarding@resend.dev>",
        "to": [user.email],
        "subject": "Activate your Car Rental account",
        "html": f"""
            <h2>Welcome to Car Rental</h2>

            <p>Hello {user.first_name},</p>

            <p>An account has been created for you by our operator.</p>

            <p>Your reservation has also been created.</p>

            <h3>Reservation details</h3>

            <ul>
                <li>Start date: {reservation.start_date}</li>
                <li>End date: {reservation.end_date}</li>
                <li>Total price: {reservation.total_price}</li>
            </ul>

            <p>To activate your account and set your password, click the button below:</p>

            <p><a href="{activation_link}">Activate account</a></p>

            <p>This activation link will expire after 24 hours.</p>

            <p>Regards,<br>Car Rental</p>
        """
    }

    resend.Emails.send(cast("resend.Emails.SendParams", cast(object, email)))
