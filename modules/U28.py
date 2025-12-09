# U-28 (상) 3. 서비스 관리 > 3.10 NIS, NIS+ 점검
####
# 점검 내용: 안전하지 않은 NIS 서비스의 비활성화, 안전한 NIS+ 서비스의 활성화 여부 점검
# 점검 목적: 안전하지 않은 NIS 서비스를 비활성화 하고 안전한 NIS+ 서비스를 활성화 하여 시스템 보안수준을 향상하고자 함
####

import subprocess
from utils.logger import log 

def check():

    result = {
        "점검 코드": "U-28",
        "점검 항목": "NIS, NIS+ 점검",
        "점검 내용": "안전하지 않은 NIS 서비스의 비활성화, 안전한 NIS+ 서비스의 활성화 여부 점검",
        "상태": "",
        "중요도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    service = "ypserv"

    cmd = f"systemctl is-active {service}"

    result["사용 명령어"] = cmd

    status = subprocess.getoutput(cmd)

    result["발견 사항"] = f"[U28] NIS/YP 서비스 상태 점검 결과: {status}"
    
    log(f"[U28] {result['발견 사항']}")

    if "inactive" in status:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "NIS 관련 서비스 비활성화"
     
    return result

def fix():
    subprocess.call("systemctl stop ypserv", shell=True)
    subprocess.call("systemctl disable ypserv", shell=True)
    return "NIS/YP 비활성화"

 ## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
