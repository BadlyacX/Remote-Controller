from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os

SCOPES = ['https://www.googleapis.com/auth/drive.file']


def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


def create_empty_file(filename):
    with open(filename, 'w') as f:
        pass
    print(f"📄 已在本地創建空檔案：{filename}")


def upload_file_to_folder(file_path, folder_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, resumable=True)

    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()
    print(f"✅ 成功上傳檔案！ID: {file.get('id')}")


if __name__ == '__main__':
    file_name = input("請輸入要創建並上傳的檔案名稱（例如 example.txt）： ").strip()
    if not file_name:
        print("⚠️ 錯誤：檔案名稱不可為空！")
        exit(1)

    folder_id = '1fZcPIlGD4as25m9tT1G_7-X27X3ZSJRY'

    create_empty_file(file_name)

    upload_file_to_folder(file_name, folder_id)
