# U-67 (중) 3. 서비스 관리 > 3.31 SNMP 서비스 Community String의 복잡성 설정
####
# 점검 내용: SNMP Community String 복잡성 설정 여부 점검
# 점검 목적: Community String 기본 설정인 Public, Private는 공개된 내용으로 공격자가 이를 이용하여 SNMP 서비스를 통해 시스템 정보를 얻을 수 있기 때문에 Community String을 유추하지 못하도록 설정해야함
####

import subprocess
import os
from utils.logger import log

conf = "/etc/snmp/snmpd.conf"
WEAK_COMMUNITIES = ["public", "private"]

def check():

    result = {
        "점검 코드": "U-67",
        "점검 항목": "SNMP 서비스 Community String의 복잡성 설정",
        "점검 내용": "SNMP Community String 복잡성 설정 여부 점검",
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

    content = open(conf).read()

    result["사용 명령어"] = f"파이썬 내장 함수 사용: open({conf}).read()"

    weak_found = [c for c in WEAK_COMMUNITIES if c in content]

    result["발견 사항"] = weak_found

    log(f"[U67] SNMP Community String 점검 결과: 약한 문자열 발견 - {', '.join(weak_found) if weak_found else '없음'}")


    if not weak_found:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "snmpd.conf 파일에서 커뮤니티명을 확인한 후 디폴트 커뮤니티명인 “public, private”를 추측하기 어려운 커뮤니티명으로 변경"
        

    return result

def fix():
    """
    ■ LINUX
    Step 1) vi 편집기를 이용하여 SNMP 설정파일 열기
    #vi /etc/snmp/snmpd.conf
    Step 2) Community String 값 설정 변경 (추측하기 어려운 값으로 설정) (수정 전) com2sec notConfigUser default public
    (수정 후) com2sec notConfigUser default <변경 값>
    Step 3) 서비스 재구동
    # service snmpd rstart
    """

    return "NOT RECOMMENDED: SNMP Community String 변경은 수동으로 관리해야 함"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
