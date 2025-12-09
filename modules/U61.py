# U-61 (하)) 3. 서비스 관리 > 3.25 ftp 서비스 확인
####
# 점검 내용: FTP 서비스가 활성화 되어있는지 점검
# 점검 목적: 취약한 서비스인 FTP서비스를 가급적 제한함을 목적으로 함
####

import subprocess
from utils.logger import log

def check():

    result = {
        "점검 코드": "U-61",
        "점검 항목": "ftp 서비스 확인",
        "점검 내용": "FTP 서비스가 활성화 되어있는지 점검",
        "상태": "",
        "심각도": "하",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    service = "vsftpd"

    cmd = f"systemctl is-active {service}"
    
    result["사용 명령어"] = cmd
    
    status = subprocess.getoutput(cmd)

    log(f"[U61] ftp 서비스 상태 점검 결과: {status}")

    result["발견 사항"] = f"{service} 서비스 상태 점검 결과: {status}"

    if "inactive" in status:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "FTP 서비스 중지"
        
    return result

def fix():
    subprocess.call("systemctl enable vsftpd", shell=True)
    subprocess.call("systemctl start vsftpd", shell=True)
    return "vsftpd 서비스 활성화"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
