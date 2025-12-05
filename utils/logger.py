import datetime
import os
import json

hostname = os.uname().nodename if hasattr(os, 'uname') else "unknown"

def log(msg):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    date = datetime.datetime.now().strftime("%Y%m%d_%H")
    output_file = f"{log_dir}/log_{hostname}_{date}.json"

    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": msg
    }

    try:
        if not os.path.exists(output_file):
            data = [log_entry]
        else:
            with open(output_file, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        data = []
                except json.JSONDecodeError:
                    data = []

            data.append(log_entry)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"[!] 파일 저장 실패: {e}")
