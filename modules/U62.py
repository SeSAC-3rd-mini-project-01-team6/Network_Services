# U-62 (중) 3. 서비스 관리 > 3.26 ftp 계정 shell 제한
####
# 점검 내용: ftp 기본 계정에 쉘 설정 여부 점검
# 점검 목적: FTP 서비스 설치 시 기본으로 생성되는 ftp 계정은 로그인이 필요하지 않은 계정으로 쉘을 제한하여 해당 계정으로의 시스템 접근을 차단하기 위함
####

import subprocess
from utils.executor import run_cmd

import os
from utils.logger import log

FTP_ACCOUNTS = ["ftp", "anonymous"]

def check():

    result = {
        "점검 코드": "U-62",
        "점검 항목": "ftp 계정 shell 제한",
        "점검 내용": "ftp 기본 계정에 쉘 설정 여부 점검",
        "상태": "",
        "심각도": "중",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    conf = "/etc/passwd"
    service = "ftp"

    cmd = f"cat {conf} | grep {service}"

    result["사용 명령어"] = cmd

    evidence = run_cmd(cmd)

    log(f"[U62] FTP 계정 쉘 제한 점검 결과: {evidence if evidence else '미설치'}")

    if "/bin/false" in evidence:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "ftp 계정에 /bin/false 쉘 부여"

    return result

def fix():
    for user in FTP_ACCOUNTS:
        subprocess.call(f"usermod -s /bin/false {user}", shell=True)
    return "FTP 계정의 로그인 쉘을 /bin/false 으로 변경함"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
