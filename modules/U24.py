# U-24 NFS 서비스 비활성화
import subprocess
from utils.logger import log

def check():
    
    result = {
        "점검 코드": "U-24",
        "점검 항목": "NFS 서비스 비활성화",
        "점검 내용": "불필요한 NFS 서비스 사용여부 점검",
        "상태": "",
        "중요도": "상",
        "발견 사항": "",
        "사용 명령어": "",
        "권고 사항": "",
    }
    
    service = "nfs-server"
    
    cmd = f'systemctl is-active {service}'
    
    result["사용 명령어"] = cmd
    
    output = subprocess.getoutput(cmd)

    log(f"[U24] NFS 서비스 상태 점검 결과: {service} {output}")
    
    result["발견 사항"] = f"{service} 서비스 상태 점검 결과: {output}"
    
    if "inactive" in output:
        result["상태"] = "양호"
        result["권고 사항"] = "조치 불필요"
    else:
        result["상태"] = "취약"
        result["권고 사항"] = "사용하지 않는다면 NFS 서비스 중지 \n 아래의 방법으로 NFS 서비스를 제거한 후 시스템 부팅 시, 스크립트 실행 방지 가능 \n 1. /etc/dfs/dfstab(또는 /etx/exports)의 모든 공유 제거 \n 2. NFS 데몬(nfsd, statd, mountd) 중지 \n 3. 시동 스크립트 삭제 또는, 스크립트 이름 변경"
    
    return result

def fix():
    ## step1. NFS 데몬 중지
    ## step2. 시동 스크립트 삭제 또는, 스크립트 이름 변경
    ## step2.1. ls -al /etc/rc.d/rc*.d/* | grep nfs
    ## step2.2. mv /etc/rc.d/rc2.d/S60nfs /etc/rc.d/rc2.d/_S60nfs
    return "NFS 서비스를 비활성화함"

## FIXME:
def run(fix_mode=False):
    """통합 실행 함수"""
    result = check()

    if fix_mode:
        patch = fix()
        result["원본파일"] = patch["원본 파일"]

    return result
