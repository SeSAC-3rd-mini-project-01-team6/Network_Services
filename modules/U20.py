# U-20 (상) 3. 서비스 관리 > 3.2 Anonymous FTP 비활성화
# 점검 내용: 익명 FTP 접속 허용 여부 점검
# 점검 목적: 실행 중인 FTP 서비스에 익명 FTP 접속이 허용되고 있는지 확인, 접속 허용 차단을 목적으로 함
# 보안 위협: 익명 FTP 사용 시 anonymous 계정으로 로그인 후 디렉터리에 쓰기 권한이 설정되어 있다면 악의적인 사용자가 local exploit을 사용해 시스템에 대한 공격을 가능하게 함
# 참고: Anonymous FTP: 파일 전송을 위해서는 원칙적으로 상대방 컴퓨터를 사용할 수 있는 계정이 필요하나,
#                > 누구든지 계정 없이도 anonymous 또는 ftp라는 로그인명과 임의의 비밀번호를 사용해 FTP를 실행할 수 있음
####

from utils.executor import run_cmd
from utils.logger import log


def check():
    
    result = {
        "점검 코드": "U-20",
        "점검 항목": "Anonymous FTP 비활성화",
        "점검 내용": "익명 FTP 접속 허용 여부 점검",
        "상태": "",
        "중요도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }
    conf = "/etc/passwd"
    service_name = "ftp"
    cmd = f"cat {conf} | grep '{service_name}'"
    evidence = run_cmd(cmd)
    
    result["사용 명령어"] = cmd

    log(f"[U20] Anonymous FTP 비활성화 점검 결과: {evidence if evidence else '결과 없음'}")
    
    if evidence:
        result["상태"] = "취약"
        result["발견 사항"] = evidence
        result["권고 사항"] = "Anonymous FTP를 사용하지 않는 경우 Anonymous FTP 접속 차단 설정 적용"
    else:
        result["상태"] = "양호"
        result["발견 사항"] = "Anonymous FTP 비활성화 상태"
        result["권고 사항"] = "조치 불필요"

    return result

def fix():
    ## case1. /etc/passwd 파일에서 ftp, 또는 anonymous 계정 주석 처리 또는 삭제
    ### userdel ftp : 사용자(ftp) 제거
    case1_cmd = f"sudo userdel ftp"
    ## 실제로 진행하지 않아요
    # case1_result = run_cmd(case1_cmd)
    
    ## case2. ProFTP - Anonymous FTP 접속 제한 설정 방법
    ### 만약 ProFTP를 사용 중이라면
    ### /etc/proftpd/proftpd.conf 파일 중에서
    ### anonymous_enable = NO 설정
    
    ## case3. vsFTP - Anonymous FTP 접속 제한 설정 방법
    ### 만약 vsFTP를 사용 중이라면
    ### /etc/vsftpd/vsftpd.conf 파일 중에서
    ### anonymous_enable = NO 설정
    case3_conf = "/etc/vsftpd/vsftpd.conf"
    case3_cmd = f"cat {case3_conf}"
    case3_origin = run_cmd(case3_cmd)
    log(f"[U20] vsftpd 원본 파일 내용: {case3_origin if case3_origin else '파일 없음'}")
    
    return {
        "원본 파일": case3_origin,
        "조치 방법": "vi로 /etc/vsftpd/vsftpd.conf 파일 열기 -> anonymous_enable=NO 로 변경 -> vsftpd 재시작",
        "조치 결과": "실제로 진행하진 않았음"
    }



def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
