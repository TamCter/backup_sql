import os
import shutil
import smtplib
import schedule
import time
from datetime import datetime
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SOURCE_FOLDER = "sql"
DEST_FOLDER = "backup_folder"
os.makedirs(DEST_FOLDER, exist_ok=True)

SENDER = os.getenv("MAIL_SENDER")
PASSWORD = os.getenv("MAIL_PASSWORD")
RECEIVER = os.getenv("MAIL_RECEIVER")

def backup_file():
    try:
        sql_files = [f for f in os.listdir(SOURCE_FOLDER) if f.endswith(".sql")]
        if not sql_files:
            raise Exception("Không tìm thấy file .sql trong thư mục nguồn.")

        latest_file = max(sql_files, key=lambda f: os.path.getmtime(os.path.join(SOURCE_FOLDER, f)))
        src_path = os.path.join(SOURCE_FOLDER, latest_file)

        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        dest_filename = f"backup_{timestamp}.sql"
        dest_path = os.path.join(DEST_FOLDER, dest_filename)

        shutil.copy2(src_path, dest_path)

        msg = f"Backup thành công: {dest_filename}"
        print(msg)
        send_email(True, msg)
    except Exception as e:
        err_msg = f"Backup thất bại: {str(e)}"
        print(err_msg)
        send_email(False, err_msg)

def send_email(success, message):
    subject = "Backup Thành Công" if success else "Backup Thất Bại"
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = SENDER
    msg["To"] = RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECEIVER, msg.as_string())
        print("Đã gửi email thông báo.")
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")

schedule.every().day.at("00:00").do(backup_file)

print("waiting...")

while True:
    schedule.run_pending()
    time.sleep(30)
