import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# -------------------------------------------------------------------
# [설정]
# 감시할 폴더 경로
WATCH_FOLDER = "/Users/kylechoi/Desktop/Ai_works/리서치본부/notebookLM_skills"

# 대상 노트북 ID (기본값: '테스트' 노트북의 ID)
# 다른 노트북으로 변경하려면 아래 ID를 수정하세요.
# (노트북 ID 확인 방법: 터미널에서 `nlm notebook list` 입력)
NOTEBOOK_ID = "d4f91849-91fe-4ecf-bbde-d1e6b9b5b6ad"
# -------------------------------------------------------------------

class NotebookLMUploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        # 폴더 생성이거나 이 파이썬 스크립트 자체인 경우는 무시합니다.
        if event.is_directory:
            return
            
        file_path = event.src_path
        filename = os.path.basename(file_path)
        
        # 임시 파일이나 스크립트 파일은 업로드하지 않음
        if filename.endswith(".py") or filename.startswith(".DS_Store"):
            return
            
        print(f"\n[+] 새로운 파일 감지됨: {filename}")
        print("파일 저장이 완료될 때까지 잠시 대기합니다 (2초)...")
        time.sleep(2)  # 시스템에서 파일 쓰기가 완전히 끝날 때까지 대기
        
        self.upload_to_notebooklm(file_path)
        
    def upload_to_notebooklm(self, file_path):
        print(f"[{os.path.basename(file_path)}] NotebookLM으로 업로드 중...")
        
        try:
            # nlm 명령어 실행 (소스 추가)
            # nlm source add <notebook_id> --file <file_path> --wait
            result = subprocess.run(
                ["nlm", "source", "add", NOTEBOOK_ID, "--file", file_path, "--wait"],
                capture_output=True,
                text=True,
                check=True
            )
            print("✅ 업로드 완료!")
            # 필요하다면 업로드 완료된 파일을 다른 폴더로 이동시키거나 삭제할 수도 있습니다.
            
        except subprocess.CalledProcessError as e:
            print("❌ 업로드 실패!")
            print(f"Error Output: {e.stderr}")
        except FileNotFoundError:
            print("❌ 오류: 'nlm' 명령어를 찾을 수 없습니다. (환경변수 문제일 수 있습니다)")

if __name__ == "__main__":
    # 폴더가 없으면 생성
    if not os.path.exists(WATCH_FOLDER):
        os.makedirs(WATCH_FOLDER)
        
    event_handler = NotebookLMUploadHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    
    print(f"🚀 폴더 감시를 시작합니다: {WATCH_FOLDER}")
    print(f"📁 이 폴더에 파일을 넣으면 자동으로 NotebookLM(노트북 ID: {NOTEBOOK_ID})에 동기화됩니다.")
    print("중지하려면 Ctrl+C 를 누르세요.\n")
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n감시를 종료합니다.")
        
    observer.join()
