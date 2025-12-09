# U-65 (중) 3. 서비스 관리 > 3.29 at 파일(at.allow, at.deny) 권한 및 소유자 설정
####
# 점검 내용: 관리자(root)만 at.allow파일과 at.deny 파일을 제어할 수 있는지 점검
# 점검 목적: 관리자외 at 서비스를 사용할 수 없도록 설정하고 있는지 점검하는 것을 목 적으로 함
####

import os
import subprocess
from utils.logger import log

AT_ALLOW = "/etc/at.allow"
AT_DENY = "/etc/at.deny"

def check_file_status(path):
    if not os.path.exists(path):
        return False, f"{path} 없음"

    stat = os.stat(path)
    mode_ok = (oct(stat.st_mode)[-3:] == "600")
    owner_ok = (stat.st_uid == 0)

    if mode_ok and owner_ok:
        return True, "정상"

    return False, "권한 또는 소유자 설정이 부적절함"


def check():

    result = {
        "점검 코드": "U-65",
        "점검 항목": "at 파일(at.allow, at.deny) 권한 및 소유자 설정",
        "점검 내용": "관리자(root)만 at.allow파일과 at.deny 파일을 제어할 수 있는지 점검",
        "상태": "",
        "심각도": "중",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }
        
    allow_ok, allow_info = check_file_status(AT_ALLOW)
    deny_ok, deny_info = check_file_status(AT_DENY)

    result["사용 명령어"] = [f"stat {AT_ALLOW}", f"stat {AT_DENY}"]

    result["발견 사항"] = f"at.allow 점검 결과: {allow_info}, at.deny 점검 결과: {deny_info}"
    log(f"[U65] {result['발견 사항']}")

    if allow_ok and deny_ok:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "crontab 명령어 750 이하, cron 관련 파일 소유자 및 권한 변경(소유자 root, 권한 640 이하)"

    return result

def fix():
    for path in [AT_ALLOW, AT_DENY]:
        subprocess.call(f"touch {path}", shell=True)
        subprocess.call(f"chown root:root {path}", shell=True)
        subprocess.call(f"chmod 600 {path}", shell=True)

    return "at.allow 및 at.deny 파일의 권한/소유자 재설정 완료"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
