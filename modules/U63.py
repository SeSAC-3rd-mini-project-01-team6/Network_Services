# U-63 (하) 3. 서비스 관리 > 3.27 ftpusers 파일 소유자 및 권한 설정
####
# 점검 내용: FTP 접근제어 설정파일에 관리자 외 비인가자들이 수정 제한 여부 점검
# 점검 목적: 비인가자들의 ftp 접속을 차단하기 위해 ftpusers 파일 소유자 및 권한을 관리해야함
####

import os
import subprocess
from utils.logger import log

conf = "/etc/vsftpd/ftpusers"

def check():

    result = {
        "점검 코드": "U-63",
        "점검 항목": "ftpusers 파일 소유자 및 권한 설정",
        "점검 내용": "FTP 접근제어 설정파일에 관리자 외 비인가자들이 수정 제한 여부 점검",
        "상태": "",
        "심각도": "하",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    if not os.path.exists(conf):
        result["상태"] = "취약"
        result["발견 사항"] = f"{conf} 파일 없음"
        result["권고 사항"] = f"FTP 접근제어 {conf} 파일 생성"
        return result

    stat = os.stat(conf)

    result["사용 명령어"] = f"stat {conf}"

    stat_part = f"ftpusers 파일 소유자: {stat.st_uid}, 권한: {oct(stat.st_mode)[-3:]}"
    log(f"[U63] {stat_part}")

    result["발견 사항"] = stat_part

    if stat.st_uid != 0 or oct(stat.st_mode)[-3:] > "640":
        result["상태"] = "취약"
        result["권고 사항"] = "FTP 접근제어 파일의 소유자 및 권한 변경 (소유자 root, 권한 640 이하)"
    else:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"

    return result

def fix():
    """
    ※ vsFTP를 사용할 경우 FTP 접근제어 파일
    (1) vsftpd.conf 파일에서 userlist_enable=YES인 경우: vsftpd.ftpusers, vsftpd.user_list 또는 ftpusers, user_list 파일의 소유자 및 권한 확인 후 변경
        (ftpusers, user_list 파일에 등록된 모든 계정의 접속이 차단됨)
    (2) vsftpd.conf 파일에서 userlist_enable=NO 또는, 옵션 설정이 없는 경우: vsftpd.ftpusers
        또는 ftpusers 파일의 소유자 및 권한 확인 후 변경 (ftpusers 파일에 등록된 계정들만 접속이 차단됨)
    """
    subprocess.call(f"touch {conf}", shell=True)
    subprocess.call(f"chown root:root {conf}", shell=True)
    subprocess.call(f"chmod 600 {conf}", shell=True)
    return "ftpusers 파일의 권한 및 소유자 설정 완료"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
