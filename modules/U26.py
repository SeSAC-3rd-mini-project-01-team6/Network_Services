# U-26 (상) 3. 서비스 관리 > 3.8 automountd 제거
####
# 점검 내용: automountd 서비스 데몬의 실행 여부 점검
# 점검 목적: 로컬 공격자가 automountd 데몬에 RPC를 보낼 수 있는 취약점이 존재하기 때문에 해당 서비스가 실행 중일 경우 서비스를 중지시키기 위함
####

import subprocess
from utils.logger import log

def check():
    
    result = {
        "점검 코드": "U-26",
        "점검 항목": "automountd 제거",
        "점검 내용": "automountd 서비스 데몬의 실행 여부 점검",
        "상태": "",
        "중요도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }
        
    service = "autofs"
    
    cmd = f'systemctl is-active {service}'
    
    result["사용 명령어"] = cmd
    
    status = subprocess.getoutput(cmd)
    
    log(f"[U26] automountfs 점검 결과: {service} {status}")
    
    result["발견 사항"] = f"{service} 서비스 상태 점검 결과: {status}"

    if "inactive" in status:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "automountd 서비스 비활성화"
        
    return result


def fix():
    return "automountd 서비스를 비활성화함"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
