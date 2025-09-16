#!/usr/bin/env python3
"""
Google Sheets의 모든 시트 이름을 찾는 스크립트
"""

import os
import requests
from urllib.parse import quote
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def find_sheet_names():
    """가능한 시트 이름들을 테스트"""
    webapp_url = os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
    sheet_id = os.getenv('GOOGLE_SHEETS_SHEET_ID')

    if not webapp_url or not sheet_id:
        print("❌ 환경변수가 설정되지 않았습니다.")
        return

    print("🔍 시트 이름 찾기")
    print("=" * 50)
    print(f"스프레드시트 ID: {sheet_id}")
    print()

    # 일반적인 시트 이름들
    possible_names = [
        'Sheet1',      # 영어 기본값
        'Sheet 1',     # 공백 포함
        '시트1',       # 한국어 기본값
        'Main',        # 자주 사용되는 이름들
        'Data',
        'Dashboard',
        'Sheet',
        '데이터',
        '메인'
    ]

    successful_names = []

    for name in possible_names:
        print(f"테스트 중: '{name}'...", end=' ')

        try:
            # URL 인코딩된 시트 이름으로 요청
            encoded_name = quote(name)
            response = requests.get(
                webapp_url,
                params={'sheetId': sheet_id, 'sheetName': encoded_name},
                timeout=10
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ 성공! ({data.get('rows', 0)}행 × {data.get('columns', 0)}열)")
                        successful_names.append(name)
                    elif 'Worksheet not found' in data.get('error', ''):
                        print("❌ 시트 없음")
                    else:
                        print(f"⚠️  오류: {data.get('error', '알 수 없는 오류')[:50]}")
                except:
                    print("❌ JSON 파싱 실패")
            else:
                print(f"❌ HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ 요청 실패: {str(e)[:30]}")

    print()

    if successful_names:
        print("🎉 찾은 시트 이름들:")
        for name in successful_names:
            print(f"   ✅ '{name}'")
        print()
        print("💡 이 중 하나를 사용하여 테스트하세요:")
        for name in successful_names[:1]:  # 첫 번째 것만 예시로
            print(f"   python -c \"")
            print(f"import sys; sys.path.append('src')")
            print(f"from sheets_client import GoogleSheetsClient")
            print(f"client = GoogleSheetsClient('{webapp_url}')")
            print(f"result = client.read_sheet('{sheet_id}', '{name}')")
            print(f"print(result)")
            print(f"   \"")
    else:
        print("❌ 올바른 시트 이름을 찾지 못했습니다.")
        print()
        print("💡 해결 방법:")
        print("1. Google Sheets에서 실제 시트 이름 확인")
        print("2. 스프레드시트에 최소 1개 이상의 시트가 있는지 확인")
        print("3. Apps Script에 스프레드시트 접근 권한이 있는지 확인")

if __name__ == "__main__":
    find_sheet_names()