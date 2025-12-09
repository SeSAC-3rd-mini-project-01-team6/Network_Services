# U-66 (중) 3. 서비스 관리 > 3.30 SNMP 서비스 구동 점검
####
# 점검 내용: SNMP 서비스 활성화 여부 점검
# 점검 목적: 불필요한 SNMP 서비스 활성화로 인해 필요 이상의 정보가 노출되는 것을 막기 위해 SNMP 서비스를 중지해야함
####

import subprocess
from utils.logger import log

def check():

    result = {
        "점검 코드": "U-66",
        "점검 항목": "SNMP 서비스 구동 점검",
        "점검 내용": "SNMP 서비스 활성화 여부 점검",
        "상태": "",
        "심각도": "중",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    service = "snmpd",

    cmd = f"systemctl is-active {service}"

    result["사용 명령어"] = cmd

    status = subprocess.getoutput(f"systemctl is-active {service}")

    result["발견 사항"] = f"{service} 서비스 상태 점검 결과: {status}"
    
    log(f"[U66] {result['발견 사항']}")

    if "inactive" in status:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "SNMP 서비스를 사용하지 않는 경우 서비스 중지 후 시작 스크립트 변경"
        

    return result

def fix():
    subprocess.call("systemctl stop snmpd", shell=True)
    subprocess.call("systemctl disable snmpd", shell=True)
    return "snmpd 서비스 비활성화"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
