#!/usr/bin/env python3
"""
토큰 인증 테스트
"""

import os
import sys
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# src 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from token_sheets_client import create_secure_client


def test_token_authentication():
    """토큰 인증 테스트"""
    print("🔐 토큰 인증 테스트")
    print("=" * 50)

    try:
        # 보안 클라이언트 생성
        client = create_secure_client()

        sheet_id = os.getenv('GOOGLE_SHEETS_SHEET_ID')
        if not sheet_id:
            print("❌ GOOGLE_SHEETS_SHEET_ID 환경변수가 필요합니다.")
            return

        print(f"📊 시트 ID: {sheet_id}")
        print()

        # 1. 읽기 테스트
        print("1️⃣ 데이터 읽기 테스트")
        result = client.read_sheet(sheet_id, '시트1')

        if 'error' not in result:
            print(f"   ✅ 성공: {result['rows']}행 × {result['columns']}열")
            if result['data']:
                print(f"   📝 첫 번째 행: {result['data'][0]}")
        else:
            print(f"   ❌ 실패: {result['error']}")
            if 'invalid token' in result['error'].lower():
                print("   💡 토큰이 올바르지 않습니다. Apps Script와 .env 파일의 토큰을 확인하세요.")

        print()

        # 2. 쓰기 테스트
        print("2️⃣ 데이터 쓰기 테스트")
        test_data = [['토큰 인증', '테스트', '성공']]
        result = client.append_rows(sheet_id, test_data, '시트1')

        if 'error' not in result:
            print(f"   ✅ 성공: {result.get('rows', 0)}행 추가됨")
        else:
            print(f"   ❌ 실패: {result['error']}")

        print()

        # 3. 잘못된 토큰 테스트
        print("3️⃣ 잘못된 토큰 테스트")
        from token_sheets_client import TokenAuthSheetsClient

        wrong_client = TokenAuthSheetsClient(
            os.getenv('GOOGLE_SHEETS_WEB_APP_URL'),
            'WrongToken123'  # 잘못된 토큰
        )

        result = wrong_client.read_sheet(sheet_id, '시트1')
        if 'error' in result and 'unauthorized' in result['error'].lower():
            print("   ✅ 올바름: 잘못된 토큰이 차단됨")
        else:
            print("   ⚠️  경고: 잘못된 토큰이 통과함 - 보안 설정 확인 필요")

    except Exception as e:
        print(f"❌ 테스트 실행 오류: {str(e)}")

    print()
    print("💡 다음 단계:")
    print("1. Apps Script에서 'Code_Token.gs' 내용으로 코드 교체")
    print("2. Apps Script 권한을 '특정 사용자만'으로 변경")
    print("3. 이 테스트가 성공하면 안전하게 사용 가능")


if __name__ == "__main__":
    test_token_authentication()