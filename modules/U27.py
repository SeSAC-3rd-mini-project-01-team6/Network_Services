# U-27 (상) 3. 서비스 관리 > 3.9 RPC 서비스 확인
# 점검 내용: 불필요한 RPC 서비스의 실행 여부 점검
# 점검 목적:
# 조치 방법: 일반적으로 사용하지 않는 RPC 서비스들은 주석처리한 후 xinetd 재시동

import subprocess
from utils.executor import run_cmd
from utils.logger import log

def check():

    result = {
        "점검 코드": "U-27",
        "점검 항목": "RPC 서비스 확인",
        "점검 내용": "불필요한 RPC 서비스의 실행 여부 점검",
        "상태": "",
        "심각도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    exsits = []
    origin_files = []

    conf = "/etc/xinetd.d/"
    service_name = ['rpc.cmsd', 'rpc.ttdbserverd', 'sadmind', 'rusersd', 'walld', 'sprayd', 'rstatd', 'rpc.nisd', 'rexd', 'rpc.pcnfsd', 'rpc.statd', 'rpc.ypupdated', 'rpc.rquotad', 'kcms_server', 'cachefsd']
    services = '|'.join(service_name)

    cmd = f'sudo grep -R "disable" {conf} | egrep "{services}"'
    grep = run_cmd(cmd)

    result["사용 명령어"] = cmd
 
    log(f"[U27] 서비스 상태 점검 결과: {grep if grep else '설정 없음'}")
    
    targets = {}
    for line in grep.strip().split("\n"):
        line = line.strip()

        target = line.split("/")[-1].split(":")[0]

        status = "yes" if "yes" in line else "no"

        targets[target] = status
            
    yes_list = [name for name, status in targets.items() if status == "yes"]
    no_list = [name for name, status in targets.items() if status == "no"]
    
    log(f"[U27] 서비스 상태 점검 disable 설정 점검 결과: disable=yes: {', '.join(yes_list) if yes_list else '없음'}, disable=no: {', '.join(no_list) if no_list else '없음'}")
    
    for s in no_list: 
        cat = run_cmd(f"cat {conf}{s}")
        if cat:
            exsits.append(s)
            origin_files.append((s, cat))

        log(f"[U27] 서비스 상태 점검 결과: {', '.join(exsits) if exsits else '존재 안 함'}")

    if exsits:
        result["상태"] = "취약"
        result["발견 사항"] = origin_files
        result["권고 사항"] = "일반적으로 사용하지 않는 RPC 서비스들은 주석처리한 후 xinetd 재시동"
    else:
        result["상태"] = "양호"
        result["발견 사항"] = f'{yes_list} "RPC 서비스 비활성화 상태"'
        result["권고 사항"] = "조치 불필요"

    return result

def fix():
    return "RPC 서비스 확인"

def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
