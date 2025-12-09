# U-69 (중) 3. 서비스 관리 > 3.33 NFS 설정파일 접근권한
####
# 점검 내용: NFS 접근제어 설정파일에 대한 비인가자들의 수정 제한 여부 점검
# 점검 목적: 비인가자에 의한 불법적인 외부 시스템 마운트를 차단하기 위해 NFS 접근 제어 파일의 소유자 및 파일 권한을 설정
####

import os
import subprocess
from utils.logger import log

conf = "/etc/exports"

def check():

    result = {
        "점검 코드": "U-69",
        "점검 항목": "NFS 설정파일 접근권한",
        "점검 내용": "NFS 접근제어 설정파일에 대한 비인가자들의 수정 제한 여부 점검",
        "상태": "",
        "심각도": "중",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    if not os.path.exists(conf):
        result["상태"] = "취약"
        result["발견 사항"] = f"{conf} 파일 없음"
        result["권고 사항"] = f"{conf} 파일 생성"
        return result

    stat = os.stat(conf)

    result["사용 명령어"] = f"stat {conf}"

    mode_ok = (oct(stat.st_mode)[-3:] == "600")
    owner_ok = (stat.st_uid == 0)

    result["발견 사항"] = f"{conf} 파일 소유자: {stat.st_uid}, 권한: {oct(stat.st_mode)[-3:]}"

    log(f"[U69] {result['발견 사항']}")

    if mode_ok and owner_ok:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = f'"{conf}" 파일의 소유자 및 권한 변경 (소유자 root, 권한 644)'

    return result

def fix():
    subprocess.call(f"chown root:root {conf}", shell=True)
    subprocess.call(f"chmod 600 {conf}", shell=True)
    return "/etc/exports 파일 권한 및 소유자 재설정 완료"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
