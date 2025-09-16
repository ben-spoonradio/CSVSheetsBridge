#!/usr/bin/env python3
"""
POST 요청 인증 테스트
"""

import os
import requests
import json
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def test_post_with_auth():
    """인증 헤더를 포함한 POST 요청 테스트"""
    webapp_url = os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
    sheet_id = os.getenv('GOOGLE_SHEETS_SHEET_ID')

    if not webapp_url or not sheet_id:
        print("❌ 환경변수가 설정되지 않았습니다.")
        return

    print("🧪 POST 요청 인증 테스트")
    print("=" * 50)

    # 테스트할 다양한 헤더 조합
    test_cases = [
        {
            "name": "기본 헤더",
            "headers": {
                'Content-Type': 'application/json'
            }
        },
        {
            "name": "User-Agent 추가",
            "headers": {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        },
        {
            "name": "추가 헤더들",
            "headers": {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Cache-Control': 'no-cache'
            }
        }
    ]

    payload = {
        'sheetId': sheet_id,
        'sheetName': '시트1',
        'action': 'append',
        'data': [['테스트', '데이터', '인증']]
    }

    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']} 테스트")

        try:
            response = requests.post(
                webapp_url,
                data=json.dumps(payload),
                headers=test_case['headers'],
                timeout=30,
                allow_redirects=True
            )

            print(f"   상태 코드: {response.status_code}")
            print(f"   응답 길이: {len(response.text)} 문자")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('success'):
                        print(f"   ✅ 성공: {data}")
                    else:
                        print(f"   ⚠️  응답 오류: {data.get('error', '알 수 없는 오류')}")
                except:
                    print(f"   ❌ JSON 파싱 실패")
                    print(f"   📄 응답 내용 (처음 200자): {response.text[:200]}")
            else:
                print(f"   ❌ HTTP 오류: {response.status_code}")
                print(f"   📄 응답 내용 (처음 200자): {response.text[:200]}")

        except Exception as e:
            print(f"   ❌ 요청 실패: {e}")

        print()

def test_get_vs_post():
    """GET과 POST 요청 비교"""
    webapp_url = os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
    sheet_id = os.getenv('GOOGLE_SHEETS_SHEET_ID')

    print("🔄 GET vs POST 비교 테스트")
    print("=" * 50)

    # GET 요청 테스트
    print("1. GET 요청 (읽기)")
    try:
        response = requests.get(
            webapp_url,
            params={'sheetId': sheet_id, 'sheetName': '시트1'},
            timeout=30
        )
        print(f"   GET 상태 코드: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   GET 성공: {data.get('success', False)}")
            except:
                print(f"   GET JSON 파싱 실패")
    except Exception as e:
        print(f"   GET 실패: {e}")

    print()

    # POST 요청 테스트
    print("2. POST 요청 (쓰기)")
    payload = {
        'sheetId': sheet_id,
        'sheetName': '시트1',
        'action': 'append',
        'data': [['POST', '테스트']]
    }

    try:
        response = requests.post(
            webapp_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        print(f"   POST 상태 코드: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   POST 성공: {data.get('success', False)}")
            except:
                print(f"   POST JSON 파싱 실패")
        else:
            print(f"   POST 응답 (처음 200자): {response.text[:200]}")
    except Exception as e:
        print(f"   POST 실패: {e}")

if __name__ == "__main__":
    test_get_vs_post()
    print()
    test_post_with_auth()