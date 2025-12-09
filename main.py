import argparse
import importlib
import pkgutil
import csv
import os

import datetime

from config import MODULE_PATH, RESULT_CSV_PATH
from utils.logger import log

RESULT_CSV_PATH += f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"


def load_modules():
    """modules 폴더의 모든 분석 모듈 자동 로딩"""
    modules = []

    for _, module_name, _ in pkgutil.iter_modules([MODULE_PATH]):
        full_name = f"modules.{module_name}"
        print(full_name)
        module = importlib.import_module(full_name)

        # run() 함수 포함된 모듈만 등록
        if hasattr(module, "run"):
            modules.append(module)

    return modules


def execute_modules(modules, fix_mode=False):
    """모듈 실행 및 결과 수집"""
    results = []

    for module in modules:
        try:
            output = module.run(fix_mode=fix_mode)
            results.append(output)
        except Exception as e:
            results.append(f"{module} ERROR: {e}")

    log(f"모듈 실행 완료: {len(results)}개 모듈 처리됨")
    return results


def save_as_csv(results):
    """CSV 저장"""
    os.makedirs(os.path.dirname(RESULT_CSV_PATH), exist_ok=True)

    with open(RESULT_CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=['점검 코드', '점검 항목', '점검 내용', '상태', '중요도', '발견 사항', '사용 명령어', '권고 사항'])
        writer.writeheader()
        writer.writerows(results)

    print(f"[+] CSV 저장 완료: {RESULT_CSV_PATH}")


def main():
    parser = argparse.ArgumentParser()
    # 실행할 때 추가: sudo python3 main.py --fix
    parser.add_argument("--fix", action="store_true", help="권고 사항 적용")
    args = parser.parse_args()

    print("\n=== Module Loader ===")

    modules = load_modules()
    print(f"[+] {len(modules)}개 모듈 로딩 완료")

    print("\n=== Module Execution ===")
    results = execute_modules(modules, fix_mode=args.fix)

    print("\n=== CSV Export ===")
    save_as_csv(results)

    print("\n=== Done ===")


if __name__ == "__main__":
    main()
