"""
Google Sheets 기본 사용 예제
"""

import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sheets_client import GoogleSheetsClient, RobustGoogleSheetsClient, extract_sheet_id_from_url

# 환경변수 로드
load_dotenv()


def main():
    """기본 사용 예제"""

    # 환경변수에서 설정값 가져오기
    WEB_APP_URL = os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
    SHEET_ID = os.getenv('GOOGLE_SHEETS_SHEET_ID')

    # 설정값 확인
    if not WEB_APP_URL:
        print("❌ GOOGLE_SHEETS_WEB_APP_URL 환경변수가 설정되지 않았습니다.")
        print("   .env 파일에 실제 Google Apps Script 웹 앱 URL을 설정하세요.")
        return

    if not SHEET_ID:
        print("❌ GOOGLE_SHEETS_SHEET_ID 환경변수가 설정되지 않았습니다.")
        print("   .env 파일에 실제 Google Sheets ID를 설정하세요.")
        return

    print(f"🔗 웹 앱 URL: {WEB_APP_URL[:50]}...")
    print(f"📊 시트 ID: {SHEET_ID}")

    # 클라이언트 생성
    client = GoogleSheetsClient(WEB_APP_URL)

    # 1. 데이터 읽기
    print("=== 데이터 읽기 ===")
    result = client.read_sheet(SHEET_ID, '시트1')
    if 'error' not in result:
        print(f"성공: {result['rows']}행, {result['columns']}열")
        print("첫 3행:", result['data'][:3] if result['data'] else "데이터 없음")
    else:
        print(f"오류: {result['error']}")

    # 2. 새 데이터 추가
    print("\n=== 행 추가 ===")
    new_data = [
        ['이름', '나이', '도시'],
        ['김철수', 25, '서울'],
        ['이영희', 30, '부산']
    ]

    result = client.append_rows(SHEET_ID, new_data, '시트1')
    if result.get('success'):
        print(f"성공: {result['rows']}행 추가됨")
    else:
        print(f"오류: {result.get('error', '알 수 없는 오류')}")

    # 3. 특정 범위 업데이트
    print("\n=== 범위 업데이트 ===")
    update_data = [
        ['업데이트된 데이터', '새로운 값'],
        ['테스트', '성공']
    ]

    result = client.update_range(SHEET_ID, 'D1:E2', update_data, '시트1')
    if result.get('success'):
        print(f"성공: {result['range']} 범위 업데이트됨")
    else:
        print(f"오류: {result.get('error', '알 수 없는 오류')}")

    # 4. 전체 시트 덮어쓰기
    print("\n=== 시트 덮어쓰기 ===")
    overwrite_data = [
        ['제품명', '가격', '재고'],
        ['노트북', 1000000, 50],
        ['마우스', 30000, 200],
        ['키보드', 80000, 100]
    ]

    result = client.overwrite_sheet(SHEET_ID, overwrite_data, '시트1')
    if result.get('success'):
        print(f"성공: {result['rows']}행으로 덮어쓰기 완료")
    else:
        print(f"오류: {result.get('error', '알 수 없는 오류')}")


def robust_client_example():
    """재시도 기능이 있는 클라이언트 예제"""

    WEB_APP_URL = os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
    SHEET_ID = os.getenv('GOOGLE_SHEETS_SHEET_ID')

    if not WEB_APP_URL or not SHEET_ID:
        print("❌ 환경변수가 설정되지 않아 안정적인 클라이언트 테스트를 건너뜁니다.")
        return

    # 안정적인 클라이언트 생성 (재시도 기능 포함)
    robust_client = RobustGoogleSheetsClient(WEB_APP_URL)

    print("=== 안정적인 클라이언트로 데이터 읽기 ===")
    result = robust_client.read_sheet(SHEET_ID, '시트1')
    if 'error' not in result:
        print(f"성공: {result['rows']}행 데이터 읽기 완료")
    else:
        print(f"최종 실패: {result['error']}")


def url_extraction_example():
    """URL에서 스프레드시트 ID 추출 예제"""

    sheet_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
    sheet_id = extract_sheet_id_from_url(sheet_url)
    print(f"스프레드시트 ID: {sheet_id}")


if __name__ == "__main__":
    print("Google Sheets 기본 사용 예제")
    print("=" * 50)

    # URL에서 ID 추출 예제
    url_extraction_example()
    print()

    # 기본 사용 예제
    main()
    print()

    # 안정적인 클라이언트 예제
    robust_client_example()