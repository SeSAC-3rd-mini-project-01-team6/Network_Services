# U-21 (상) 3. 서비스 관리 > 3.2 r 계열 서비스 비활성화
# 점검 내용: r-command 서비스 비활성화 여부 점검
# 점검 목적: r-command 사용을 통한 원격 접속은 NET Backup 또는 클러스터링 등 용도로 사용되기도 하나, 인증 없이 관리자 원격접속이 가능해 이에 대한 보안 위협을 방지하고자 함
# 보안 위협: rsh, rlogin, rexec 등의 r command를 이용해 원격에서 인증 절차 없이 터미널 접속, 쉘 명령어 실행 가능
# 참고: r-command: 인증 없이 관리자의 원격 접속을 가능하게 하는 명령어들 rsh(remsh), rlogin, rexec, rsync 등

## 조치 방법: NET Backup 등 특별한 용도로 사용하지 않는다면 아래의 서비스 중지
## - shell(514)
## - login(513)
## - exec(512)
####

from utils.executor import run_cmd
from utils.logger import log


def check():

    result = {
        "점검 코드": "U-21",
        "점검 항목": "r 계열 서비스 비활성화",
        "점검 내용": "r-command 서비스 비활성화 여부 점검",
        "상태": "",
        "중요도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    conf = "/etc/xinetd.d/*"
    service_name = ['rsh', 'rlogin', 'rexec', 'klogin', 'kshell', 'kexec']
    cmd = f"ls -alL {conf} | egrep '{service_name[0]}|{service_name[1]}|{service_name[2]}' | egrep -v 'grep|{service_name[3]}|{service_name[4]}|{service_name[5]}'"
    evidence = run_cmd(cmd)
    
    log(f"[U21] r-command 패키지 점검 결과: {evidence if evidence else '미설치'}")

    if evidence:
        result["상태"] = "취약"
        result["발견 사항"] = evidence
        result["권고 사항"] = "Net Backup 등 특별한 용도로 사용하지 않는다면 shell, login, exec 서비스 중지"
    else:
        result["상태"] = "양호"
        result["발견 사항"] = "r 계열 서비스 비활성화 상태"
        result["권고 사항"] = "조치 불필요"

    return result


def fix():
    ## step1. /etc/xinetd.d/ 내 rsh, rlogin, rexec 파일 열기
    conf1 = "/etc/xinetd.d/rsh"
    conf2 = "/etc/xinetd.d/rlogin"
    conf3 = "/etc/xinetd.d/rexec"
    origin1 = run_cmd(f"cat {conf1}")
    origin2 = run_cmd(f"cat {conf2}")
    origin3 = run_cmd(f"cat {conf3}")
    
    log(f"[U21] rsh 원본 파일 내용: {origin1 if origin1 else '파일 없음'}")
    log(f"[U21] rlogin 원본 파일 내용: {origin2 if origin2 else '파일 없음'}")
    log(f"[U21] rexec 원본 파일 내용: {origin3 if origin3 else '파일 없음'}")
    
    ## step2. Disable = yes 로 변경
    ## step3. xinetd 재시작
    
    
    return {
        "원본 파일": {
            "rsh": origin1,
            "rlogin": origin2,
            "rexec": origin3
        },
        "조치 방법": "/etc/xinetd.d/ 내 rsh, rlogin, rexec 파일 열기 -> Disable = yes 로 변경 -> xinetd 재시작",
        "조치 결과": "실제로 진행하진 않았음"
    }



def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result