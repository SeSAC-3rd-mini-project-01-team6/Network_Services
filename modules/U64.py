# U-64 3. 서비스 관리 > 3.28 ftpusers 파일 설정(FTP 서비스 root 계정 접근제한)
####
# 점검 내용: FTP 서비스를 사용할 경우 ftpusers 파일 root 계정이 포함 여부 점검
# 점검 목적: root의 FTP 직접 접속을 방지하여 root 패스워드 정보를 노출되지 않도록 하기 위함
####

####
#※ vsFTP를 사용할 경우 FTP 접근제어 파일
#(1) vsftpd.conf 파일에서 userlist_enable=YES인 경우: vsftpd.ftpusers, vsftpd.user_list 또는
#ftpusers, user_list
#(ftpusers, user_list 파일에 등록된 모든 계정의 접속이 차단됨)
#(2) vsftpd.conf 파일에서 userlist_enable=NO 또는, 옵션 설정이 없는 경우: vsftpd.ftpusers
#또는 ftpusers
#(ftpusers 파일에 등록된 계정들만 접속이 차단됨)
####

import os
from utils.logger import log

## /etc/vsftpd/ftpusers 에 root 추가하기
conf = "/etc/vsftpd/ftpusers"
ESSENTIAL_BLOCKED = ["root"]

def check():
    result = {
        "점검 코드": "U-64",
        "점검 항목": "ftpusers 파일 설정(FTP 서비스 root 계정 접근제한)",
        "점검 내용": "FTP 서비스를 사용할 경우 ftpusers 파일 root 계정이 포함 여부 점검",
        "상태": "",
        "심각도": "중",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }

    if not os.path.exists(conf):
        result["상태"] = "취약"
        result["발견 사항"] = "c 파일 없음"
        result["권고 사항"] = "FTP 접근제어 파일 생성하기"
        return result

    content = open(conf).read().splitlines()

    missing = [user for user in ESSENTIAL_BLOCKED if user not in content]

    result["발견 사항"] = ', '.join(missing) if missing else f'/etc/vsftpd/ftpusers에 {missing} 없음'
    log(f"[U64] /etc/vsftpd/ftpusers 설정 점검 결과: - {result['발견 사항']}")


    if not missing:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "FTP 접속 시 root 계정으로 직접 접속 할 수 없도록 설정파일 수정(접속 차단 계정을 등록하는 ftpusers 파일에 root 계정 추가)"

    return result

def fix():
    with open(conf, "a") as f:
        for u in ESSENTIAL_BLOCKED:
            f.write(u + "\n")
    return "필수 계정들의 FTP 차단 규칙 추가 완료"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
