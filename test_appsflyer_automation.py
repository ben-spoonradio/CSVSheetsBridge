#!/usr/bin/env python3
"""
Appsflyer 자동화 시스템 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'src'))

def test_sample_automation():
    """샘플 데이터로 자동화 테스트"""
    print("🧪 Appsflyer 자동화 시스템 테스트")
    print("=" * 50)

    try:
        from appsflyer_automation import AppsflyerAutomation

        # 자동화 객체 생성
        automation = AppsflyerAutomation()

        # 샘플 데이터로 테스트 실행
        print("📝 샘플 데이터로 테스트 시작...")
        success = automation.run(
            csv_path='--sample',
            backup=True,
            export_csv=True
        )

        if success:
            print("\n✅ 테스트 성공! 시스템이 정상 작동합니다.")
            print("\n다음 단계:")
            print("1. 실제 Appsflyer CSV 파일 준비")
            print("2. python appsflyer_automation.py --csv Data_dua.csv 실행")
        else:
            print("\n❌ 테스트 실패. 로그를 확인하세요.")

        return success

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {str(e)}")
        print("\n문제 해결 방법:")
        print("1. pip install pandas numpy python-dotenv requests")
        print("2. .env 파일에 Google Sheets 설정 확인")
        return False

if __name__ == "__main__":
    test_sample_automation()