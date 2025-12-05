import subprocess
from utils.logger import log

def run_cmd(cmd):
    try:
        
        result = subprocess.run(f"{cmd}", shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        log(f"명령어 실행 오류: {e}")
        return str(e)
