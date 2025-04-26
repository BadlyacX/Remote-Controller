import time
import subprocess
import webbrowser
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'

POLL_INTERVAL = 10
MAX_INTERVAL = 60

REMOTE_CONTROLLER_FOLDER_NAME = "RemoteController"

def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def find_remote_controller_folder(service):
    query = f"name='{REMOTE_CONTROLLER_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields="files(id, name)",
        pageSize=1
    ).execute()
    folders = results.get('files', [])

    if not folders:
        raise Exception(f"找不到名為「{REMOTE_CONTROLLER_FOLDER_NAME}」的資料夾！請先建立它！")

    return folders[0]['id']

def handle_file(service, file):
    filename = file['name']
    file_id = file['id']

    if filename == 'hello.re':
        print("偵測到 hello.re，開啟記事本！")
        subprocess.run(["notepad.exe"])
    elif filename == 'rickroll.re':
        print("偵測到 rickroll.re，準備 Rickroll 他！")
        webbrowser.open("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    service.files().delete(fileId=file_id).execute()
    print(f"已刪除檔案：{filename}")

def check_and_act(service, folder_id):
    query = f"('{folder_id}' in parents) and (name='hello.re' or name='rickroll.re')"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields="files(id, name)"
    ).execute()

    items = results.get('files', [])
    for file in items:
        handle_file(service, file)

def main():
    global POLL_INTERVAL
    service = authenticate()

    try:
        folder_id = find_remote_controller_folder(service)
        print(f"✅ 找到 RemoteController 資料夾，ID: {folder_id}")
    except Exception as e:
        print(f"❌ 錯誤：{e}")
        return

    while True:
        try:
            print(f"[{time.strftime('%H:%M:%S')}] 檢查 RemoteController 中的檔案...（間隔：{POLL_INTERVAL}s）")
            check_and_act(service, folder_id)
            time.sleep(POLL_INTERVAL)

            if POLL_INTERVAL > 10:
                POLL_INTERVAL = max(10, POLL_INTERVAL // 2)

        except HttpError as error:
            if error.resp.status in [403, 429]:
                print("API 頻率限制！啟動智慧調頻模式...")
                POLL_INTERVAL = min(POLL_INTERVAL * 2, MAX_INTERVAL)
                print(f"目前輪詢間隔已調整為 {POLL_INTERVAL} 秒")
                time.sleep(POLL_INTERVAL)
            else:
                raise

if __name__ == '__main__':
    main()
