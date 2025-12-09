# U-23 (상) 3. 서비스 관리 > 3.5 DoS 공격에 취약한 서비스 비활성화
# 점검 내용: 사용하지 않은 DoS 공격에 취약한 서비스의 실행 여부
# 점검 목적: 시스템 보안성을 높이기 위해 취약점이 많이 발표된 echo, discard, daytime, chargen, ntp, snmp 서비스 비활성화
# 보안 위협: 해당 서비스가 활성화되어 있는 경우 시스템 정보 유출 및 DoS(서비스 거부 공격)의 대상이 될 수 있음
# 참고: Denial of Service attack 시스템을 악의적으로 공격, 해당 시스템의 자원을 부족하게 해 원래 의도된 용도로 사용하지 못하게 하는 공격

## 조치 방법: echo, discard, daytime, charge, ntp, dns, snmp 아래의 서비스 중지
####


from utils.executor import run_cmd
from utils.logger import log

## 취약 서비스 목록:
## echo, discard, daytime, chargen (xinetd 기반)

conf = "/etc/xinetd.d/"
SERVICES = ["echo", "discard", "daytime", "chargen"]
SUB = ["-dgram", "-stream"]

def check():
    
    result = {
        "점검 코드": "U-23",
        "점검 항목": "DoS 공격에 취약한 서비스 비활성화",
        "점검 내용": "사용하지 않은 DoS 공격에 취약한 서비스의 실행 여부",
        "상태": "",
        "중요도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }
    
    exsits = []
    origin_files = []
    
    SERVICE_LIST = [s + sub for s in SERVICES for sub in SUB]

    cmd = f'sudo grep -R "disable" /etc/xinetd.d/ | egrep "echo-|discard-|daytime-|chargen-"'
    grep = run_cmd(cmd)

    result["사용 명령어"] = cmd
    

    log(f"[U23] xinetd 기반 DoS 위험 서비스 disable 설정 점검 결과: {grep if grep else '설정 없음'}")
        
    targets = {}
    for line in grep.strip().split("\n"):
        line = line.strip()

        target = line.split("/")[-1].split(":")[0]

        status = "yes" if "yes" in line else "no"

        targets[target] = status
            
    yes_list = [name for name, status in targets.items() if status == "yes"]
    no_list = [name for name, status in targets.items() if status == "no"]
    
    log(f"[U23] xinetd 기반 DoS 위험 서비스 disable 설정 점검 결과: disable=yes: {', '.join(yes_list) if yes_list else '없음'}, disable=no: {', '.join(no_list) if no_list else '없음'}")
    
    for s in no_list: 
        cat = run_cmd(f"cat {conf}{s}")
        if cat:
            exsits.append(s)
            origin_files.append((s, cat))

        log(f"[U23] xinetd 기반 DoS 위험 서비스 점검 결과: {', '.join(exsits) if exsits else '존재 안 함'}")

    if exsits:
        result["상태"] = "취약"
        result["발견 사항"] = origin_files
        result["권고 사항"] = "Net Backup 등 특별한 용도로 사용하지 않는다면 shell, login, exec 서비스 중지"
    else:
        result["상태"] = "양호"
        result["발견 사항"] = f'{yes_list} "DoS 공격에 취약한 서비스 비활성화 상태"'
        result["권고 사항"] = "조치 불필요"

    return result


def fix():
    # for s in SERVICES:
    #     run_cmd(f"systemctl disable --now {s}.socket 2>/dev/null")
    return "DoS 위험 서비스 비활성화 완료"

def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
