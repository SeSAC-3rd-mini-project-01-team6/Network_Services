# U-22 (상) 3. 서비스 관리 > 3.4 crond 파일 소유자 및 권한 설정
####
# 점검 내용: cron 관련 파일의 권한 적절성 점검
# 점검 목적: 관리자 외 cron 서비스를 사용할 수 없도록 설정하고 있는지 점검
# 보안 위협: root 외 일반 사용자에게도 crontab 명령어를 사용할 수 있도록 할 경우, 고의 또는 실수로 불법적인 예약 파일 실행으로 시스템 피해 발생 가능
# 참고:
## - Cron 시스템: 특정 작업을 정해진 시간에 주기적이고 반복적으로 실행하기 위한 데몬 및 설정
## - cron.allow: 사용자 ID를 등록하면 등록된 사용자는 crontab 명령어를 사용 가능
## - cron.deny: 사용자 ID를 등록하면 등록된 사용자는 crontab 명령어를 사용 불가능

#####
#기준
## 양호: crontab 명령어 일반 사용자 금지 및 cron 관련 파일 640 이하인 경우
## 취약: crontab 명령어 일반 사용자 허용 및 cron 관련 파일 640 초과인 경우
## 조치: crontab 명령어 750 이하, cron 관련 파일 소유자 및 권한 변경(소유자 root, 권한 640 이하)
#####
# crontab <- 예약작업을 등록하는 파일
# cron.houly <- 시간 단위 실행 스크립트 등록
# cron.daily <- 일 단위 실행 스크립트 등록
# cron.weekly <- 주 단위 실행 스크립트 등록
# cron.monthly <- 월 단위 실행 스크립트 등록
# cron.d <- 개별 크론 작업 파일들이 위치하는 디렉토리
# cron.allow <- crontab 명령어 허용 사용자
# cron.deny <- crontab 명령어 차단 사용자
# /var/spool/cron 또는 /var/spool/cron/crontabs <- 사용자별 crontab 파일이 위치하는 디렉토리
## /etc/crontab, /etc/cron.hourly, /etc/cron.daily
## owner = root
## permission = 600 또는 700
#####

from utils.executor import run_cmd
from utils.logger import log

TARGETS = [
    "/etc/crontab",
    "/etc/cron.hourly",
    "/etc/cron.daily",
    "/etc/cron.weekly",
    "/etc/cron.monthly",
    "/etc/cron.allow"
    "/etc/cron.deny"
]

def check():

    result = {
        "점검 코드": "U-22",
        "점검 항목": "crond 파일 소유자 및 권한 설정",
        "점검 내용": "cron 관련 파일의 권한 적절성 점검",
        "상태": "",
        "중요도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }
        
    vulnerable_list = []

    result["사용 명령어"] = f'stat {TARGETS}'

    for path in TARGETS:
        owner = run_cmd(f"stat -c %U {path}")
        perm = run_cmd(f"stat -c %a {path}")

        if owner != "root" or int(perm) > 700:
            vulnerable_list.append(f"{path} ({owner}:{perm})")

    found = f"cron 권한 점검 결과: {', '.join(vulnerable_list) if vulnerable_list else '모두 안전'}"

    log(f"[U22] {found}")

    if vulnerable_list:
        result["상태"] = "취약"
        result["권고 사항"] = f"권한 취약 파일: {', '.join(vulnerable_list)} 소유자 root, 권한 640 이하로 변경"

    return result


def fix():

    for path in TARGETS:
        run_cmd(f"chown root:root {path}")
        # 디렉토리는 700, 파일은 600
        run_cmd(f"chmod 600 {path} 2>/dev/null")
        run_cmd(f"chmod 700 {path} 2>/dev/null")

    """ +
    ■ crontab 명령어를 일반사용자에게 허용하는 경우
    Step 1) “/etc/cron.d/cron.allow” 및 “/etc/cron.d/cron.deny” 파일의 소유자 및 권한 변경
    #chown root /etc/cron.d/cron.allow #chmod 640 /etc/cron.d/cron.allow #chown root /etc/cron.d/cron.deny #chmod 640 /etc/cron.d/cron.deny
    Step 2) “/etc/cron.d/cron.allow” 및 “/etc/cron.d/cron.deny” 파일에 사용자 등록 # cat /etc/cron.allow (crontab 명령어 사용을 허용하는 사용자 등록)
    # cat /etc/cron.deny (crontabl 명령어 사용을 차단하는 사용자 등록)
    """
    return "cron 권한 안전하게 조정 완료"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
