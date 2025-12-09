# U-25 (상) 3. 서비스 관리 > 3.7 NFS 접근 통제
# 점검 내용: NFS 사용 시 허가된 사용자만 접속할 수 있도록 접근 제한 설정 적용 여부 점검
# 점검 목적: 
# 보안 위협: 
# 참고:

import subprocess
from utils.logger import log

def check():
    
    result = {
        "점검 코드": "U-25",
        "점검 항목": "NFS 접근 통제",
        "점검 내용": "NFS 사용 시 허가된 사용자만 접속할 수 있도록 접근 제한 설정 적용 여부 점검",
        "상태": "",
        "중요도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }
    
    cmd = "cat /etc/exports"
    evidence = subprocess.getoutput(cmd)
    
    log(f"[U25] NFS 접근 통제 점검 결과: {evidence if evidence else '결과 없음'}")
    
    if evidence:
        result["상태"] = "취약"
        result["발견 사항"] = evidence
        result["권고 사항"] = "사용하지 않는다면 NFS 서비스 중지 \n NFS를 사용할 경우 /etc/exports everyone 공유 설정 제거"
    else:
        result["상태"] = "양호"
        result["발견 사항"] = "NFS 접근 통제 설정 적용 상태"
        result["권고 사항"] = "조치 불필요"

    return result

def fix():
    ## /etc/exports 파일에서 everyone 공유 설정 제거
    
    ## step1. /etc/exports 파일에 접근 가능한 호스트명 추가
    return "/etc/exports 파일에서 everyone 공유 설정 제거"

def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
