#!/bin/bash
# setup_insecure_full.sh
# 완전 통합형: OS 감지, RHEL subscription 체크, 패키지 자동 조정,
# jq 설치/폴백, 설치 성공/실패 JSON 로그, xinetd 취약 설정 적용,
# 안전 정책 유지 (/etc/passwd, /etc/ssh/sshd_config 미수정), 백업 + 롤백 생성
#
# 사용: sudo bash setup_insecure_full.sh
set -euo pipefail
IFS=$'\n\t'

# -------------------------
# 기본 설정
# -------------------------
TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
BASE_DIR="/etc/insecure-configs"
BACKUP_DIR="${BASE_DIR}/backup_${TIMESTAMP}"
XINETD_DIR="/etc/xinetd.d"
ROLLBACK_SCRIPT="${BASE_DIR}/rollback_insecure.sh"
LOG_FN="/var/log/pkg_install_${TIMESTAMP}.json"
LOG_PREFIX() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

# 안전: 절대 건드리지 않을 파일
IMMUTABLE_FILES=( "/etc/passwd" "/etc/ssh/sshd_config" )

# 사용자 요청한 전체 패키지 목록 (기본 후보)
REQUESTED_PACKAGES=(
  xinetd
  rsh-server
  rsh
  finger
  tftp-server
  talk-server
  rpcbind
  nfs-utils
  net-snmp
  net-snmp-utils
  vsftpd
  at
  autofs
  ypserv
  ypbind
  yp-tools
)

# 바이너리 후보 맵 (xinetd 서비스 파일 생성용)
declare -A SERVICE_BIN_CANDIDATES=(
  [finger]="/usr/sbin/in.fingerd /usr/libexec/in.fingerd /usr/sbin/fingerd"
  [tftp]="/usr/sbin/in.tftpd /usr/sbin/tftpd /usr/libexec/in.tftpd"
  [rsh]="/usr/sbin/in.rshd /usr/libexec/in.rshd"
  [rlogin]="/usr/sbin/in.rlogind /usr/libexec/in.rlogind"
  [rexec]="/usr/sbin/in.rexecd /usr/libexec/in.rexecd"
)

INTERNAL_SERVICES=( echo chargen )

# -------------------------
# 헬퍼: OS 감지
# -------------------------
detect_os() {
  local os_id=""
  if [ -f /etc/os-release ]; then
    . /etc/os-release
    os_id="$ID"
    os_name="$NAME"
  else
    os_id="$(uname -s)"
    os_name="$os_id"
  fi

  case "$os_id" in
    amzn*) echo "Amazon Linux";;
    rhel)  echo "RHEL";;
    centos) echo "CentOS";;
    rocky) echo "Rocky";;
    alma)  echo "AlmaLinux";;
    *) echo "$os_name";;
  esac
}

OS="$(detect_os)"
LOG_PREFIX "Detected OS: $OS"

# -------------------------
# 헬퍼: JSON 로그 (jq 우선, 실패하면 Python 폴백)
# -------------------------
USE_PY_JSON=0
ensure_json_tool() {
  if command -v jq >/dev/null 2>&1; then
    LOG_PREFIX "jq found"
    USE_PY_JSON=0
  else
    LOG_PREFIX "jq not found, trying to install jq via yum..."
    if sudo yum install -y jq >/dev/null 2>&1; then
      LOG_PREFIX "jq installed"
      USE_PY_JSON=0
    else
      LOG_PREFIX "jq install failed or not available. Will fallback to Python for JSON writes."
      if command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
        USE_PY_JSON=1
      else
        LOG_PREFIX "ERROR: Neither jq nor python available — cannot write JSON logs."
        exit 1
      fi
    fi
  fi
}

# Initialize empty JSON array file
init_log_file() {
  if [ "$USE_PY_JSON" -eq 0 ]; then
    echo "[]" > "$LOG_FN"
  else
    # minimal json init
    echo "[]" > "$LOG_FN"
  fi
}

# Append entry to JSON log
# args: package, status, message
log_json() {
  local pkg="$1"; local status="$2"; local msg="$3"; local ts
  ts="$(date +"%Y-%m-%d %H:%M:%S")"
  if [ "$USE_PY_JSON" -eq 0 ]; then
    tmp=$(mktemp)
    jq -c --arg pkg "$pkg" --arg status "$status" --arg msg "$msg" --arg ts "$ts" \
       '. += [{package:$pkg, status:$status, message:$msg, timestamp:$ts, os:$OS}]' "$LOG_FN" > "$tmp" && mv "$tmp" "$LOG_FN"
  else
    # python fallback: read file, append object, write
    if command -v python3 >/dev/null 2>&1; then
      python3 - <<PY >> /dev/null
import json,sys
fn="${LOG_FN}"
try:
    with open(fn,"r",encoding="utf-8") as f:
        data=json.load(f)
except Exception:
    data=[]
data.append({"package":"${pkg}","status":"${status}","message":"${msg}","timestamp":"${ts}","os":"${OS}"})
with open(fn,"w",encoding="utf-8") as f:
    json.dump(data,f,indent=2,ensure_ascii=False)
PY
    else
      python - <<PY >> /dev/null
import json,sys
fn="${LOG_FN}"
try:
    with open(fn,"r",encoding="utf-8") as f:
        data=json.load(f)
except Exception:
    data=[]
data.append({"package":"${pkg}","status":"${status}","message":"${msg}","timestamp":"${ts}","os":"${OS}"})
with open(fn,"w",encoding="utf-8") as f:
    json.dump(data,f,indent=2,ensure_ascii=False)
PY
    fi
  fi
}

# -------------------------
# 헬퍼: 바이너리 탐색 (서비스 파일 생성용)
# -------------------------
find_binary() {
  local candidates="$1"
  for p in $candidates; do
    if [ -x "$p" ]; then
      echo "$p"
      return 0
    fi
  done
  for name in $candidates; do
    local base
    base="$(basename "$name")"
    if command -v "$base" >/dev/null 2>&1; then
      command -v "$base"
      return 0
    fi
  done
  return 1
}

# -------------------------
# 1) 사전 안전 체크(immutable files)
# -------------------------
for f in "${IMMUTABLE_FILES[@]}"; do
  if [ ! -e "$f" ]; then
    LOG_PREFIX "WARNING: expected immutable file missing: $f (continue but please check)"
  fi
done

# -------------------------
# 2) 디렉토리 및 백업 준비
# -------------------------
LOG_PREFIX "Preparing directories: $BASE_DIR, backup -> $BACKUP_DIR"
sudo mkdir -p "$BASE_DIR"
sudo mkdir -p "$BACKUP_DIR"
# backup existing xinetd.d
if [ -d "$XINETD_DIR" ]; then
  sudo mkdir -p "$BACKUP_DIR/xinetd.d"
  sudo cp -a "${XINETD_DIR}/"* "$BACKUP_DIR/xinetd.d/" 2>/dev/null || true
  LOG_PREFIX "Backed up existing /etc/xinetd.d to $BACKUP_DIR/xinetd.d"
fi

# -------------------------
# 3) OS별 / RHEL subscription 체크 -> 패키지 목록 자동 조정
# -------------------------
subscription_ok=true
if [ "$OS" = "RHEL" ]; then
  LOG_PREFIX "Checking RHEL subscription status..."
  if command -v subscription-manager >/dev/null 2>&1; then
    sub_out="$(sudo subscription-manager status 2>&1 || true)"
    if echo "$sub_out" | grep -qiE "Unknown|Invalid|Overall Status: Unknown|Overall Status: Invalid|Not Registered"; then
      subscription_ok=false
      LOG_PREFIX "RHEL subscription NOT registered or invalid. Many packages may not be available."
    else
      LOG_PREFIX "RHEL subscription appears registered."
    fi
  else
    subscription_ok=false
    LOG_PREFIX "subscription-manager not found -> treating as no-subscription"
  fi
fi

# Build actual install list based on OS + subscription
PACKAGES=()
if [ "$OS" = "RHEL" ] && [ "$subscription_ok" = false ]; then
  LOG_PREFIX "RHEL w/o subscription -> restricting to core packages that might be available locally"
  # choose conservative subset likely available or harmless to attempt
  PACKAGES=( xinetd rpcbind nfs-utils net-snmp net-snmp-utils vsftpd at autofs )
  LOG_PREFIX "Adjusted package list: ${PACKAGES[*]}"
else
  # For Amazon Linux / CentOS / Rocky / Alma or RHEL+subscription: try requested set
  PACKAGES=( "${REQUESTED_PACKAGES[@]}" )
  LOG_PREFIX "Using full requested package list (will skip missing packages): ${PACKAGES[*]}"
fi

# -------------------------
# 4) Ensure JSON tool ready
# -------------------------
ensure_json_tool
init_log_file

# -------------------------
# 5) Package install loop (existence check -> install -> log)
#    - Do not allow single package failure to exit script
# -------------------------
for pkg in "${PACKAGES[@]}"; do
  LOG_PREFIX "Checking availability for package: $pkg"
  # try to see if package exists in repo OR already installed
  if yum list available "$pkg" >/dev/null 2>&1 || rpm -q "$pkg" >/dev/null 2>&1 ; then
    LOG_PREFIX "Package $pkg appears available (or already installed). Attempting install..."
    if sudo yum install -y "$pkg" >/dev/null 2>&1; then
      LOG_PREFIX "Installed: $pkg"
      log_json "$pkg" "success" "installed"
    else
      LOG_PREFIX "Install failed for: $pkg (logged and continuing)"
      log_json "$pkg" "failed" "yum install returned error"
    fi
  else
    LOG_PREFIX "Package not found in repos: $pkg -> skipping"
    log_json "$pkg" "not_found" "not found in repositories"
  fi
done

# -------------------------
# 6) xinetd service files creation (only /etc/xinetd.d/* are changed)
#    - Use find_binary results; fallback to defaults and warn
# -------------------------
LOG_PREFIX "Creating /etc/xinetd.d service files (finger, tftp, rsh, rlogin, rexec, echo, chargen)"

# finger
finger_bin="$(find_binary "${SERVICE_BIN_CANDIDATES[finger]}" || true)" || finger_bin=""
if [ -z "$finger_bin" ]; then
  LOG_PREFIX "finger binary not found. Using default /usr/sbin/in.fingerd (may not work)"
  finger_bin="/usr/sbin/in.fingerd"
else
  LOG_PREFIX "finger binary found: $finger_bin"
fi
sudo tee "${XINETD_DIR}/finger" > /dev/null <<EOF
service finger
{
    disable     = no
    socket_type = stream
    protocol    = tcp
    wait        = no
    user        = root
    server      = ${finger_bin}
    log_on_failure  += USERID
}
EOF

# tftp
tftp_bin="$(find_binary "${SERVICE_BIN_CANDIDATES[tftp]}" || true)" || tftp_bin=""
if [ -z "$tftp_bin" ]; then
  LOG_PREFIX "tftp binary not found. Using default /usr/sbin/in.tftpd (may not work)"
  tftp_bin="/usr/sbin/in.tftpd"
else
  LOG_PREFIX "tftp binary found: $tftp_bin"
fi
sudo tee "${XINETD_DIR}/tftp" > /dev/null <<EOF
service tftp
{
    disable     = no
    socket_type = dgram
    protocol    = udp
    wait        = yes
    user        = root
    server      = ${tftp_bin}
    server_args = /var/lib/tftpboot
}
EOF

# rsh
rsh_bin="$(find_binary "${SERVICE_BIN_CANDIDATES[rsh]}" || true)" || rsh_bin=""
if [ -z "$rsh_bin" ]; then
  LOG_PREFIX "rsh binary not found. Using default /usr/sbin/in.rshd (may not work)"
  rsh_bin="/usr/sbin/in.rshd"
else
  LOG_PREFIX "rsh binary found: $rsh_bin"
fi
sudo tee "${XINETD_DIR}/rsh" > /dev/null <<EOF
service shell
{
    disable     = no
    socket_type = stream
    protocol    = tcp
    wait        = no
    user        = root
    server      = ${rsh_bin}
}
EOF

# rlogin
rlogin_bin="$(find_binary "${SERVICE_BIN_CANDIDATES[rlogin]}" || true)" || rlogin_bin=""
if [ -z "$rlogin_bin" ]; then
  LOG_PREFIX "rlogin binary not found. Using default /usr/sbin/in.rlogind (may not work)"
  rlogin_bin="/usr/sbin/in.rlogind"
else
  LOG_PREFIX "rlogin binary found: $rlogin_bin"
fi
sudo tee "${XINETD_DIR}/rlogin" > /dev/null <<EOF
service login
{
    disable     = no
    socket_type = stream
    protocol    = tcp
    wait        = no
    user        = root
    server      = ${rlogin_bin}
}
EOF

# rexec
rexec_bin="$(find_binary "${SERVICE_BIN_CANDIDATES[rexec]}" || true)" || rexec_bin=""
if [ -z "$rexec_bin" ]; then
  LOG_PREFIX "rexec binary not found. Using default /usr/sbin/in.rexecd (may not work)"
  rexec_bin="/usr/sbin/in.rexecd"
else
  LOG_PREFIX "rexec binary found: $rexec_bin"
fi
sudo tee "${XINETD_DIR}/rexec" > /dev/null <<EOF
service exec
{
    disable     = no
    socket_type = stream
    protocol    = tcp
    wait        = no
    user        = root
    server      = ${rexec_bin}
}
EOF

# INTERNAL services
sudo tee "${XINETD_DIR}/echo" > /dev/null <<EOF
service echo
{
    disable     = no
    type        = INTERNAL
    socket_type = stream
    protocol    = tcp
    user        = root
}
EOF

sudo tee "${XINETD_DIR}/chargen" > /dev/null <<EOF
service chargen
{
    disable     = no
    type        = INTERNAL
    socket_type = stream
    protocol    = tcp
    user        = root
}
EOF

# enable & restart xinetd if unit exists
if systemctl list-unit-files | grep -q "^xinetd"; then
  LOG_PREFIX "Enabling and restarting xinetd"
  sudo systemctl enable xinetd >/dev/null 2>&1 || LOG_PREFIX "systemctl enable xinetd failed (check manually)"
  if sudo systemctl restart xinetd >/dev/null 2>&1; then
    LOG_PREFIX "xinetd restarted"
  else
    LOG_PREFIX "WARNING: xinetd restart failed - check 'systemctl status xinetd' and 'journalctl -u xinetd'"
  fi
else
  LOG_PREFIX "xinetd unit not found - ensure xinetd is installed and systemd unit exists"
fi

# -------------------------
# 7) /etc/insecure-configs/* 문서(비적용) 생성
# -------------------------
LOG_PREFIX "Creating insecure config files under $BASE_DIR (not applied to system)"

sudo mkdir -p "${BASE_DIR}/"{vsftpd,nfs,snmp,autofs,nis}

sudo tee "${BASE_DIR}/vsftpd/vsftpd.conf.insecure" > /dev/null <<EOF
anonymous_enable=YES
local_enable=YES
write_enable=YES
anon_upload_enable=YES
anon_mkdir_write_enable=YES
anon_root=/var/ftp
listen=YES
listen_ipv6=NO
EOF

sudo tee "${BASE_DIR}/nfs/exports.insecure" > /dev/null <<EOF
/tmp *(rw,no_root_squash)
/home *(rw,no_root_squash)
EOF

sudo tee "${BASE_DIR}/snmp/snmpd.conf.insecure" > /dev/null <<EOF
rocommunity public
syslocation "Test Lab"
syscontact test@example.com
EOF

sudo tee "${BASE_DIR}/autofs/auto.master.insecure" > /dev/null <<EOF
/mnt/auto /etc/auto.misc
EOF

sudo tee "${BASE_DIR}/autofs/auto.misc.insecure" > /dev/null <<EOF
tmp  -fstype=nfs,rw  localhost:/tmp
home -fstype=nfs,rw  localhost:/home
EOF

sudo tee "${BASE_DIR}/nis/securenets.insecure" > /dev/null <<EOF
0.0.0.0 0.0.0.0
EOF

sudo tee "${BASE_DIR}/nis/ypserv.conf.insecure" > /dev/null <<EOF
* : * : allow
EOF

# -------------------------
# 8) 롤백 스크립트 생성
# -------------------------
LOG_PREFIX "Generating rollback script at: $ROLLBACK_SCRIPT"
sudo tee "${ROLLBACK_SCRIPT}" > /dev/null <<'EOF'
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'
TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
BASE_DIR="/etc/insecure-configs"
BACKUP_DIR="$(ls -d ${BASE_DIR}/backup_* 2>/dev/null | tail -n1 || true)"
XINETD_DIR="/etc/xinetd.d"
log(){ echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"; }

if [ -z "$BACKUP_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
  log "Backup directory not found: $BACKUP_DIR. Manual restore required."
  exit 1
fi

log "Restoring from backup: $BACKUP_DIR"
if [ -d "${BACKUP_DIR}/xinetd.d" ]; then
  cp -a "${BACKUP_DIR}/xinetd.d/"* "${XINETD_DIR}/"
  log "Restored xinetd.d files"
else
  log "No xinetd.d backup found in $BACKUP_DIR"
fi

if systemctl restart xinetd >/dev/null 2>&1; then
  log "xinetd restarted"
else
  log "WARNING: xinetd restart failed after restore - check systemctl status"
fi

log "Rollback complete. Consider removing ${BASE_DIR} if you want to fully clean up."
EOF

sudo chmod +x "${ROLLBACK_SCRIPT}"

# -------------------------
# 마무리 출력
# -------------------------
LOG_PREFIX "=========================================="
LOG_PREFIX "  취약 환경 구성 완료 (통합 스크립트)"
LOG_PREFIX "  적용된 곳: /etc/xinetd.d/**/* ONLY (실제 반영)"
LOG_PREFIX "  비적용(생성만): ${BASE_DIR}/*"
LOG_PREFIX "  백업 위치: ${BACKUP_DIR}"
LOG_PREFIX "  롤백 스크립트: ${ROLLBACK_SCRIPT}"
LOG_PREFIX "  패키지 설치 로그 (JSON): ${LOG_FN}"
LOG_PREFIX "=========================================="

# 화면에도 JSON 로그 출력 요약(간단)
if [ -f "${LOG_FN}" ]; then
  LOG_PREFIX "Install log (first/last 10 lines):"
  sudo head -n 20 "${LOG_FN}" || true
fi

exit 0
