# U-60 (중) 3. 서비스 관리 > 3.24 ssh 원격접속 허용
####
# 점검 내용: 원격 접속 시 SSH 프로토콜을 사용하는지 점검
# 점검 목적: 비교적 안전한 SSH 프로토콜을 사용함으로써 스니핑 등 아이디/패스워드의 누출의 방지를 목적으로 함
####

import subprocess
from utils.logger import log

def check():

    result = {
        "점검 코드": "U-60",
        "점검 항목": "RPC 서비스 확인",
        "점검 내용": "불필요한 RPC 서비스의 실행 여부 점검",
        "상태": "",
        "중요도": "중",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    service = "sshd"

    cmd = f"systemctl is-active {service}"
    
    result["사용 명령어"] = cmd
    
    status = subprocess.getoutput(cmd)

    log(f"[U60] sshd 서비스 상태 점검 결과: {status}")

    result["발견 사항"] = f"{service} 서비스 상태 점검 결과: {status}"

    if "inactive" in status:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "Telnet, FTP 등 안전하지 않은 서비스 사용을 중지하고, SSH 설치 및 사용"
    
    return result

def fix():
    subprocess.call("systemctl enable sshd", shell=True)
    subprocess.call("systemctl start sshd", shell=True)
    return "sshd 서비스를 활성화함"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
