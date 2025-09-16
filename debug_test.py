#!/usr/bin/env python3
"""
디버깅용 테스트 스크립트
"""

import os
import requests
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

def debug_webapp():
    """웹 앱 디버깅"""
    webapp_url = os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
    sheet_id = os.getenv('GOOGLE_SHEETS_SHEET_ID')

    if not webapp_url or not sheet_id:
        print("❌ 환경변수가 설정되지 않았습니다.")
        return

    print("🔍 Google Apps Script 웹 앱 디버깅")
    print("=" * 60)
    print(f"웹 앱 URL: {webapp_url}")
    print(f"시트 ID: {sheet_id}")
    print()

    # 1. 기본 GET 요청
    print("1️⃣ 기본 GET 요청 테스트")
    try:
        response = requests.get(webapp_url, params={'sheetId': sheet_id}, timeout=30)
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답 헤더: {dict(response.headers)}")
        print(f"   응답 길이: {len(response.text)} 문자")

        if response.status_code == 200:
            print("   ✅ 요청 성공")
            try:
                data = response.json()
                print(f"   📊 JSON 파싱 성공: {type(data)}")
                if 'success' in data:
                    print(f"   📈 데이터: {data.get('rows', 0)}행 × {data.get('columns', 0)}열")
                else:
                    print(f"   ⚠️  응답 구조: {list(data.keys())}")
            except Exception as e:
                print(f"   ❌ JSON 파싱 실패: {e}")
                print(f"   📄 응답 내용 (처음 500자):")
                print(f"   {response.text[:500]}")
        else:
            print(f"   ❌ 요청 실패: {response.status_code}")
            print(f"   📄 응답 내용 (처음 500자):")
            print(f"   {response.text[:500]}")

    except Exception as e:
        print(f"   ❌ 요청 오류: {e}")

    print()

    # 2. 다양한 User-Agent로 테스트
    print("2️⃣ User-Agent 헤더 테스트")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(webapp_url, params={'sheetId': sheet_id},
                              headers=headers, timeout=30)
        print(f"   상태 코드: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ User-Agent 헤더로 성공")
        else:
            print(f"   ❌ User-Agent 헤더로도 실패: {response.status_code}")
    except Exception as e:
        print(f"   ❌ User-Agent 테스트 오류: {e}")

    print()

    # 3. 직접 브라우저 테스트 URL 제공
    test_url = f"{webapp_url}?sheetId={sheet_id}"
    print("3️⃣ 브라우저 직접 테스트")
    print("   다음 URL을 브라우저에서 직접 열어보세요:")
    print(f"   {test_url}")
    print()
    print("   기대 결과: JSON 형태의 데이터")
    print("   실제 결과가 로그인 페이지면 → 권한 설정 문제")
    print("   실제 결과가 오류 페이지면 → Apps Script 코드 문제")
    print()

    # 4. 권한 설정 가이드
    print("4️⃣ 권한 설정 해결방법")
    print("   Google Apps Script 편집기에서:")
    print("   1. 배포 > 배포 관리 클릭")
    print("   2. 현재 배포의 편집 버튼 클릭")
    print("   3. 액세스 권한을 '모든 사용자'로 변경")
    print("   4. 배포 버튼 클릭")
    print("   5. 새 웹 앱 URL로 .env 파일 업데이트")


if __name__ == "__main__":
    debug_webapp()