# U-68 (하) 3. 서비스 관리 > 3.32 로그온 시 경고 메시지 제공
####
# 점검 내용: 서버 및 서비스에 로그온 시 불필요한 정보 차단 설정 및 불법적인 사용에 대한 경고 메시지 출력 여부 점검
# 점검 목적: 비인가자들에게 서버에 대한 불필요한 정보를 제공하지 않고, 서버 접속 시 관계자만 접속해야 한다는 경각심을 심어 주기위해 경고 메시지 설정이 필 요함
####

import subprocess
import os
from utils.logger import log

TARGET_FILES = ["/etc/motd", "/etc/issue.net", "/etc/vsftpd/vsftpd.conf", "/etc/mail/sendmail.cf", "/etc/named.conf"]

def check():

    result = {
        "점검 코드": "U-68",
        "점검 항목": "로그온 시 경고 메시지 제공",
        "점검 내용": "서버 및 서비스에 로그온 시 불필요한 정보 차단 설정 및 불법적인 사용에 대한 경고 메시지 출력 여부 점검",
        "상태": "",
        "중요도": "하",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }
        
    missing = []
    for path in TARGET_FILES:
        if not os.path.exists(path) or len(open(path).read().strip()) == 0:
            missing.append(path)

    found = f"로그인 경고 메시지 점검 결과: 비어 있거나 없는 파일 - {', '.join(missing) if missing else '없음'}"
    result["발견 사항"] = found

    log(f"[U68] {found}")

    if not missing:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "Telnet, FTP, SMTP, DNS 서비스를 사용할 경우 설정파일 조치 후 inetd 데몬 재시작"
     
    return result

def fix():
    """
    ■ LINUX
    Step 1) 서버 로그온 메시지 설정: vi 편집기로 "/etc/motd" 파일을 연 후 로그온 메시지 입력
    #vi /etc/motd
    경고 메시지 입력
    Step 2) Telnet 배너 설정: vi 편집기로 "/etc/issue.net" 파일을 연 후 로그온 메시지 입력
    #vi /etc/issue.net
    경고 메시지 입력
    Step 3) FTP 배너 설정: vi 편집기로 "/etc/vsftpd/vsftpd.conf" 파일을 연 후 로그인 메시지 입
    력
    #vi /etc/vsftpd/vsftpd.conf ftpd_banner="경고 메시지 입력"
    Step 4) SMTP 배너 설정: vi 편집기로 "/etc/mail/sendmail.cf" 파일을 연 후 로그인 메시지 입 력
    #vi /etc/mail/sendmail.cf
    O Smtp GreetingMessage="경고 메시지 입력"
    Step 5) DNS 배너 설정: vi 편집기로 "/etc/named.conf" 파일을 연 후 로그인 메시지 입력 #vi /etc/named.conf
    경고 메시지 입력
    """
    caution = "경고: 본 시스템은 권한 있는 사용자만 접근할 수 있습니다."

    for path in TARGET_FILES:
        with open(path, "w") as f:
            f.write(caution + "\n")

    return "로그온 경고 메시지를 모든 대상 파일에 적용함"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
