#!/usr/bin/env python3
"""
Google Sheets 연동 설정 도우미
"""

import os
import re
from urllib.parse import urlparse


def extract_script_id_from_url(url):
    """웹 앱 URL에서 스크립트 ID 추출"""
    pattern = r'/macros/s/([a-zA-Z0-9-_]+)/exec'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def validate_webapp_url(url):
    """웹 앱 URL 유효성 검사"""
    if not url.startswith('https://script.google.com/macros/s/'):
        return False, "URL은 'https://script.google.com/macros/s/'로 시작해야 합니다."

    if not url.endswith('/exec'):
        return False, "URL은 '/exec'로 끝나야 합니다."

    script_id = extract_script_id_from_url(url)
    if not script_id:
        return False, "올바른 스크립트 ID를 찾을 수 없습니다."

    return True, f"✅ 스크립트 ID: {script_id}"


def validate_sheet_id(sheet_id):
    """스프레드시트 ID 유효성 검사"""
    # Google Sheets ID는 보통 44자 길이의 알파벳, 숫자, 하이픈, 언더스코어로 구성
    if len(sheet_id) < 20:
        return False, "스프레드시트 ID가 너무 짧습니다."

    if not re.match(r'^[a-zA-Z0-9-_]+$', sheet_id):
        return False, "스프레드시트 ID는 알파벳, 숫자, 하이픈, 언더스코어만 포함해야 합니다."

    return True, f"✅ 스프레드시트 ID: {sheet_id[:20]}..."


def extract_sheet_id_from_url(url):
    """Google Sheets URL에서 스프레드시트 ID 추출"""
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    return None


def setup_env_file():
    """대화형 .env 파일 설정"""
    print("🚀 Google Sheets 연동 설정을 시작합니다!")
    print("=" * 60)

    # 1. Google Apps Script 웹 앱 URL 설정
    print("\n1️⃣ Google Apps Script 웹 앱 URL 설정")
    print("   Google Apps Script에서 배포한 웹 앱 URL을 입력하세요.")
    print("   예: https://script.google.com/macros/s/SCRIPT_ID/exec")

    while True:
        webapp_url = input("\n웹 앱 URL: ").strip()
        if not webapp_url:
            print("❌ URL을 입력해주세요.")
            continue

        is_valid, message = validate_webapp_url(webapp_url)
        print(message)

        if is_valid:
            break
        print("다시 입력해주세요.")

    # 2. Google Sheets ID 설정
    print("\n2️⃣ Google Sheets ID 설정")
    print("   스프레드시트 URL 또는 스프레드시트 ID를 입력하세요.")
    print("   URL 예: https://docs.google.com/spreadsheets/d/SHEET_ID/edit")
    print("   ID 예: 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms")

    while True:
        sheet_input = input("\n스프레드시트 URL 또는 ID: ").strip()
        if not sheet_input:
            print("❌ 스프레드시트 URL 또는 ID를 입력해주세요.")
            continue

        # URL인지 ID인지 판단
        if sheet_input.startswith('https://'):
            sheet_id = extract_sheet_id_from_url(sheet_input)
            if not sheet_id:
                print("❌ URL에서 스프레드시트 ID를 추출할 수 없습니다.")
                continue
            print(f"✅ URL에서 추출된 스프레드시트 ID: {sheet_id}")
        else:
            sheet_id = sheet_input

        is_valid, message = validate_sheet_id(sheet_id)
        print(message)

        if is_valid:
            break
        print("다시 입력해주세요.")

    # 3. .env 파일 생성
    print("\n3️⃣ .env 파일 생성")
    env_content = f"""# Google Sheets Apps Script 웹 앱 URL
GOOGLE_SHEETS_WEB_APP_URL={webapp_url}

# 기본 스프레드시트 ID
GOOGLE_SHEETS_SHEET_ID={sheet_id}
"""

    env_file_path = '.env'

    # 기존 .env 파일이 있으면 백업
    if os.path.exists(env_file_path):
        backup_path = '.env.backup'
        os.rename(env_file_path, backup_path)
        print(f"📁 기존 .env 파일을 {backup_path}로 백업했습니다.")

    # 새 .env 파일 생성
    with open(env_file_path, 'w', encoding='utf-8') as f:
        f.write(env_content)

    print(f"✅ .env 파일이 생성되었습니다!")
    print(f"📄 파일 위치: {os.path.abspath(env_file_path)}")

    # 4. 연결 테스트 제안
    print("\n4️⃣ 연결 테스트")
    test_now = input("지금 연결 테스트를 실행하시겠습니까? (y/n): ").strip().lower()

    if test_now in ['y', 'yes', '예', 'ㅇ']:
        print("\n🧪 연결 테스트를 실행합니다...")
        test_connection(webapp_url, sheet_id)

    print("\n🎉 설정이 완료되었습니다!")
    print("다음 명령어로 예제를 실행할 수 있습니다:")
    print("  python examples/basic_usage.py")


def test_connection(webapp_url, sheet_id):
    """연결 테스트"""
    try:
        import sys
        sys.path.append('src')
        from sheets_client import GoogleSheetsClient

        client = GoogleSheetsClient(webapp_url)
        result = client.read_sheet(sheet_id)

        if 'error' not in result:
            print("✅ 연결 테스트 성공!")
            print(f"   📊 시트 데이터: {result['rows']}행 × {result['columns']}열")
            if result['data']:
                print(f"   📝 첫 번째 행: {result['data'][0][:5]}...")  # 처음 5개 셀만 표시
        else:
            print("❌ 연결 테스트 실패!")
            print(f"   오류: {result['error']}")
            print("\n🔍 문제 해결 방법:")
            print("   1. Google Apps Script 웹 앱이 올바르게 배포되었는지 확인")
            print("   2. 웹 앱 접근 권한이 '모든 사용자'로 설정되었는지 확인")
            print("   3. 스프레드시트 ID가 올바른지 확인")
            print("   4. 스프레드시트에 읽기 권한이 있는지 확인")

    except ImportError as e:
        print("❌ 필요한 패키지가 설치되지 않았습니다.")
        print("다음 명령어로 설치하세요:")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 연결 테스트 중 오류 발생: {str(e)}")


def show_deployment_guide():
    """배포 가이드 표시"""
    print("\n📚 Google Apps Script 배포 가이드")
    print("=" * 60)
    print("1. https://script.google.com 접속")
    print("2. 새 프로젝트 생성")
    print("3. apps_script/Code.gs 파일 내용을 복사하여 붙여넣기")
    print("4. 배포 > 새 배포 > 웹 앱 선택")
    print("5. 실행 계정: '나', 액세스 권한: '모든 사용자'")
    print("6. 배포 후 웹 앱 URL 복사")
    print("\n자세한 가이드: apps_script/DEPLOYMENT.md 참조")


def main():
    """메인 함수"""
    print("🔧 Google Sheets 연동 설정 도우미")
    print("=" * 60)

    if not os.path.exists('apps_script/Code.gs'):
        print("❌ Google Apps Script 파일을 찾을 수 없습니다.")
        print("   현재 디렉토리가 CSVSheetsBridge 프로젝트 루트인지 확인하세요.")
        return

    print("다음 중 선택하세요:")
    print("1. .env 파일 설정 (권장)")
    print("2. Google Apps Script 배포 가이드 보기")
    print("3. 종료")

    while True:
        choice = input("\n선택 (1-3): ").strip()

        if choice == '1':
            setup_env_file()
            break
        elif choice == '2':
            show_deployment_guide()
            continue
        elif choice == '3':
            print("👋 설정을 종료합니다.")
            break
        else:
            print("❌ 1, 2, 또는 3을 입력해주세요.")


if __name__ == "__main__":
    main()