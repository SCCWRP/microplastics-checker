from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import COMMASPACE, formatdate
from email import encoders
import smtplib
from smtplib import SMTPException
import boto3
import pandas as pd
import mimetypes

# Send email with Amazon SES (instead of postfix)
def send_mail(
    send_from="dockerchecker@sccwrp.co",
    send_to=[],
    subject="",
    body="",
    files=None,
    aws_region="us-west-2"
):
    if not send_to:
        raise ValueError("Recipient list cannot be empty.")

    # Create SES client
    ses_client = boto3.client("ses", region_name=aws_region)

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = send_from
    msg["To"] = ", ".join(send_to)
    msg["Subject"] = subject

    # Attach the email body
    msg.attach(MIMEText(body, "plain"))

    # Attach files if provided
    if files:
        for file_path in files:
            try:
                mime_type, _ = mimetypes.guess_type(file_path)
                mime_type = mime_type or "application/octet-stream"
                main_type, sub_type = mime_type.split("/", 1)

                with open(file_path, "rb") as file:
                    attachment = MIMEBase(main_type, sub_type)
                    attachment.set_payload(file.read())

                encoders.encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition", f'attachment; filename="{file_path.split("/")[-1]}"'
                )
                msg.attach(attachment)
            except Exception as e:
                print(f"Failed to attach {file_path}: {e}")

    # Send email using AWS SES
    response = ses_client.send_raw_email(
        Source=send_from,
        Destinations=send_to,
        RawMessage={"Data": msg.as_string()},
    )

    return response

def data_receipt(send_from, always_send_to, login_email, dtype, submissionid, originalfile, tables, eng, mailserver, login_info, cc = None, *args, **kwargs):
    """
    Depending on the project, this function will likely need to be modified. In some cases there are agencies and data owners that
    must be incuded in the email body or subject.

    send_from must be a string, like admin@chceker.sccwrp.org
    always_send_to are the email addresses which will always receive the email, which may or may not always be the maintainers
    login_email is the email the user logged in with
    dtype is the data type they submitted data for
    submissionid is self explanatory
    tables is the list of all tables they submitted data to
    eng is the database connection to confirm the records were loaded
    mailserver is the server that will be used to send the email
    """

    email_subject = f"Successful Data Load - {dtype} -- Submission ID#: {submissionid}"
    email_body = f"SCCWRP has received a successful {dtype} data submission from {login_email}\n"
    email_body += f"Submission ID: {submissionid}\n"
    email_body += f"Date Received: {pd.Timestamp(submissionid, unit = 's').strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    email_body += "Session Login Information:\n\t"
    for k,v in login_info.items():
        email_body += f"{k}: {v}\n\t"
    email_body += "\n\n"
    email_body += "\n".join(
        [
            f"""{pd.read_sql(f'SELECT COUNT(*) AS n_records FROM "{tbl}" WHERE submissionid = {submissionid};', eng).n_records.values[0]} records loaded to {tbl}"""
            for tbl in tables 
        ]
    )

    send_to = [*always_send_to, login_email]
    if cc is not None:
        assert isinstance(cc, str), f'Invalid email address: {cc}'
        send_to.append(cc)
   
    send_mail(send_from, send_to, email_subject, email_body, files = [originalfile])



