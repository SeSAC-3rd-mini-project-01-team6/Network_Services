# U-19 (상): 3. 서비스 관리 > 3.1 Finger 서비스 비활성화
#### FIXME: 주어진 step대로
# 점검 내용: finger 서비스 비활성화 여부 점검
# 점검 목적: Finger(사용자 정보 확인 서비스)를 통해서 네트워크 외부에서 해당 시스템에 등록된 사용자 정보 확인 가능
#          > 비인가자에게 사용자 정보가 조회되는 것을 차단
# 보안 위협: 비인가자에게 사용자 정보가 조회되어 패스워드 공격을 통한 시스템 권한 탈취 가능성, 사용하지 않는다면 해당 서비스 중지 필요.
# 참고: who 명령어: 현재 사용 중인 사용자들에 대한 간단한 정보만 제공
## cf. finger 명령어: 등록된 사용자뿐만 아니라 네트워크를 통하여 연결되어 있는 다른 시스템에 등록된 사용자들에 대한 자세한 정보를 보여줌

# | 항목       | 설명                                        |
# | -------- | ----------------------------------------- |
# | finger란? | 사용자 정보 조회 명령 및 서비스                        |
# | 주요 기능    | 유저 정보, 로그인 상태, 홈 디렉토리 등 확인                |
# | 보안 위험    | 계정 노출, 시스템 정보 노출, 원격 조회 위험, 과거 서비스 취약점 존재 |
# | 현재 상태    | 대부분 리눅스에서 기본 비활성화 또는 설치되지 않음              |
####

from utils.executor import run_cmd
from utils.logger import log

conf = "/etc/xinetd.d/*"
service_name = "finger"

## TODO: 전체적으로 - check(conf, service_name) 형태
def check():

    ## TODO: 전체적으로 - result json 포맷 기본 값 불러와서 쓰기
    result = {
        "점검 코드": "U-19",
        "점검 항목": "Finger 서비스 비활성화",
        "점검 내용": "finger 서비스 비활성화 여부 점검",
        "상태": "",
        "심각도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    cmd = f"ls -alL {conf} | egrep '{service_name}'"
    evidence = run_cmd(cmd)
    
    result["사용 명령어"] = cmd

    log(f"[U19] finger 결과: {evidence if evidence else '결과 없음'}")

    if evidence:
        result["상태"] = "취약"
        result["발견 사항"] = evidence
        result["권고 사항"] = "Finger 서비스 비활성화"
    else:
        result["상태"] = "양호"
        result["발견 사항"] = "Finger 서비스 비활성화 상태"
        result["권고 사항"] = "조치 불필요"

    return result


def fix():
    cmd = f"cat /etc/xinetd.d/finger"
    origin = run_cmd(cmd)
    log(f"[U19] finger 원본 파일 내용: {origin if origin else '파일 없음'}")
    
    ## Step1. vi로 /etc/xinetd.d/finger 파일 열기
    ## Step2. Disable = yes 로 변경
    ## Step3. xinetd 재시작
    
    return {
        "원본 파일": origin,
        "조치 방법": "vi로 /etc/xinetd.d/finger 파일 열기 -> Disable = yes 로 변경 -> xinetd 재시작",
        "조치 결과": "실제로 진행하진 않았음"
    }
    


def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
