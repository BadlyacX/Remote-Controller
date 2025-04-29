import time
import subprocess
import webbrowser
import os
import psutil
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

REMOTE_CONTROLLER_FOLDER_NAME = "RemoteController"

POLL_INTERVAL = 10
MAX_INTERVAL = 60

def authenticate():
    creds = None
    if os.path.exists(resource_path(TOKEN_FILE)):
        creds = Credentials.from_authorized_user_file(resource_path(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                resource_path(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(resource_path(TOKEN_FILE), 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)

def find_or_create_remote_controller_folder(service):
    query = f"name='{REMOTE_CONTROLLER_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields="files(id, name)",
        pageSize=1
    ).execute()
    folders = results.get('files', [])

    if folders:
        print(f"✅ 找到 RemoteController 資料夾")
        return folders[0]['id']
    else:
        print(f"⚠️ 找不到 RemoteController 資料夾，正在自動建立...")
        folder_metadata = {
            'name': REMOTE_CONTROLLER_FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        print(f"✅ RemoteController 資料夾已建立，ID: {folder.get('id')}")
        return folder.get('id') 

def handle_file(service, file):
    filename = file['name']
    file_id = file['id']

    if filename == 'hello.re':
        print("偵測到 hello.re，開啟記事本！")
        subprocess.run(["notepad.exe"])
    
    elif filename == 'boom.re':
        print("偵測到 boom.re，開啟 cmd 準備boom")
        while True:
            subprocess.run('start cmd /k', shell=True)

    elif filename == 'rick.re':
        print("偵測到 rick.re，準備 rick 他！")
        subprocess.run('start cmd /k "curl ascii.live/rick')

    elif filename == 'shutdown.re':
        print("偵測到 shutdown.re，將關閉主機...")
        subprocess.run('start cmd /c "shutdown /s /t 0"', shell=True)

    elif filename == 'restart.re':
        print("偵測到 restart.re，將重啟主機...")
        subprocess.run('start cmd /c "shutdown /r /t 0"', shell=True)

    elif filename == 'dir.re':
        print("偵測到 dir.re，開啟 cmd 並執行 color c + dir /s")
        subprocess.run('start cmd /c "color a && cd /d c: && dir/s"', shell=True)

    elif filename == 'parrot.re':
        print("偵測到 parrot.re，開啟 cmd 並執行 curl parrot.live")
        subprocess.run('start cmd /k "curl parrot.live"', shell=True)
    
    elif filename == 'killAllTask.re':
        print("偵測到 killAllTask.re，關閉所有運行程式（小心使用）")
        for proc in psutil.process_iter():
            try:
                proc.kill()
            except Exception as e:
                pass

    service.files().delete(fileId=file_id).execute()
    
    print(f"已刪除檔案：{filename}")

def check_and_act(service, folder_id):
    query = f"('{folder_id}' in parents) and (name='hello.re' or name='rick.re' or name='shutdown.re' or name='restart.re' or name='dir.re' or name='killAllTask.re' or name='parrot.re' or name = 'boom.re')"
    results = service.files().list(
        q=query,
        spaces='drive',
        fields="files(id, name)"
    ).execute()

    items = results.get('files', [])
    for file in items:
        handle_file(service, file)

def resource_path(relative_path):
    import sys, os
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def main():
    global POLL_INTERVAL
    service = authenticate()

    folder_id = find_or_create_remote_controller_folder(service)

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
