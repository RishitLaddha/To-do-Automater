# modules/email_sender.py

import smtplib

def send_email(sender: str, password: str, recipient: str, subject: str, message: str):
    """
    Send an email using Gmail's SMTP server.

    This function constructs an email message with the provided subject and message body, connects to Gmail's
    SMTP server using TLS, logs in with the sender's credentials, and sends the email to the specified recipient.
    After sending, it closes the SMTP connection.

    Args:
        sender (str): The email address from which the email is sent.
        password (str): The password or app-specific password for the sender's Gmail account.
        recipient (str): The email address of the recipient.
        subject (str): The subject line of the email.
        message (str): The body text of the email.

    Returns:
        None

    Raises:
        Exception: If there is an error during the email sending process, an exception will be printed.

    Example:
        >>> send_email("sender@example.com", "password123", "recipient@example.com", "Test Subject", "Test Message")
    """
    try:
        # Construct the email message with a subject header followed by the message body.
        msg = f"Subject: {subject}\n\n{message}"
        # Connect to Gmail's SMTP server on port 587 which supports TLS encryption.
        s = smtplib.SMTP('smtp.gmail.com', 587)
        # Start TLS encryption to secure the connection.
        s.starttls()
        # Log in to the SMTP server using the sender's credentials.
        s.login(sender, password)
        # Send the email from the sender to the recipient with the constructed message.
        s.sendmail(sender, recipient, msg)
        # Terminate the SMTP connection.
        s.quit()
        print(f"[EMAIL] Email sent to {recipient}")
    except Exception as e:
        # If an error occurs, print the error message.
        print("[EMAIL] Failed to send email:", e)
