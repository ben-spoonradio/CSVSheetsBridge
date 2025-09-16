"""
CSV 파일과 Google Sheets 연동 예제
"""

import csv
import sys
import os
from typing import List
from dotenv import load_dotenv
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from sheets_client import GoogleSheetsClient

# 환경변수 로드
load_dotenv()


def csv_to_sheets(csv_file_path: str, web_app_url: str, sheet_id: str, sheet_name: str = 'Sheet1'):
    """
    CSV 파일 내용을 Google Sheets로 업로드

    Args:
        csv_file_path: CSV 파일 경로
        web_app_url: Apps Script 웹 앱 URL
        sheet_id: 스프레드시트 ID
        sheet_name: 시트 이름
    """
    client = GoogleSheetsClient(web_app_url)

    # CSV 파일 읽기
    data = []
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                data.append(row)

        print(f"CSV 파일에서 {len(data)}행 읽기 완료")

        # Google Sheets에 덮어쓰기
        result = client.overwrite_sheet(sheet_id, data, sheet_name)

        if result.get('success'):
            print(f"Google Sheets 업로드 성공: {result['rows']}행")
        else:
            print(f"업로드 실패: {result.get('error')}")

    except FileNotFoundError:
        print(f"CSV 파일을 찾을 수 없음: {csv_file_path}")
    except Exception as e:
        print(f"CSV 읽기 오류: {str(e)}")


def sheets_to_csv(web_app_url: str, sheet_id: str, csv_file_path: str, sheet_name: str = 'Sheet1'):
    """
    Google Sheets 내용을 CSV 파일로 다운로드

    Args:
        web_app_url: Apps Script 웹 앱 URL
        sheet_id: 스프레드시트 ID
        csv_file_path: 저장할 CSV 파일 경로
        sheet_name: 시트 이름
    """
    client = GoogleSheetsClient(web_app_url)

    # Google Sheets에서 데이터 읽기
    result = client.read_sheet(sheet_id, sheet_name)

    if 'error' in result:
        print(f"Sheets 읽기 실패: {result['error']}")
        return

    data = result['data']
    print(f"Google Sheets에서 {len(data)}행 읽기 완료")

    # CSV 파일로 저장
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerows(data)

        print(f"CSV 파일 저장 완료: {csv_file_path}")

    except Exception as e:
        print(f"CSV 저장 오류: {str(e)}")


def create_sample_csv(file_path: str):
    """샘플 CSV 파일 생성"""
    sample_data = [
        ['이름', '나이', '도시', '직업'],
        ['김철수', '25', '서울', '개발자'],
        ['이영희', '30', '부산', '디자이너'],
        ['박민수', '28', '대구', '마케터'],
        ['정수진', '32', '인천', '기획자']
    ]

    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(sample_data)

    print(f"샘플 CSV 파일 생성 완료: {file_path}")


def sync_csv_sheets(csv_file_path: str, web_app_url: str, sheet_id: str,
                   sheet_name: str = 'Sheet1', direction: str = 'csv_to_sheets'):
    """
    CSV와 Google Sheets 동기화

    Args:
        csv_file_path: CSV 파일 경로
        web_app_url: Apps Script 웹 앱 URL
        sheet_id: 스프레드시트 ID
        sheet_name: 시트 이름
        direction: 동기화 방향 ('csv_to_sheets' 또는 'sheets_to_csv')
    """
    if direction == 'csv_to_sheets':
        print("CSV → Google Sheets 동기화")
        csv_to_sheets(csv_file_path, web_app_url, sheet_id, sheet_name)
    elif direction == 'sheets_to_csv':
        print("Google Sheets → CSV 동기화")
        sheets_to_csv(web_app_url, sheet_id, csv_file_path, sheet_name)
    else:
        print("유효하지 않은 동기화 방향. 'csv_to_sheets' 또는 'sheets_to_csv'를 사용하세요.")


def main():
    """메인 함수"""

    # 환경변수에서 설정값 가져오기
    WEB_APP_URL = os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
    SHEET_ID = os.getenv('GOOGLE_SHEETS_SHEET_ID')
    CSV_FILE = 'sample_data.csv'

    # 설정값 확인
    if not WEB_APP_URL:
        print("❌ GOOGLE_SHEETS_WEB_APP_URL 환경변수가 설정되지 않았습니다.")
        return

    if not SHEET_ID:
        print("❌ GOOGLE_SHEETS_SHEET_ID 환경변수가 설정되지 않았습니다.")
        return

    print("CSV와 Google Sheets 연동 예제")
    print("=" * 50)

    # 1. 샘플 CSV 파일 생성
    print("\n1. 샘플 CSV 파일 생성")
    create_sample_csv(CSV_FILE)

    # 2. CSV를 Google Sheets로 업로드
    print("\n2. CSV → Google Sheets")
    csv_to_sheets(CSV_FILE, WEB_APP_URL, SHEET_ID, '시트1')

    # 3. Google Sheets를 CSV로 다운로드
    print("\n3. Google Sheets → CSV")
    download_csv = 'downloaded_data.csv'
    sheets_to_csv(WEB_APP_URL, SHEET_ID, download_csv, '시트1')

    # 4. 동기화 함수 사용 예제
    print("\n4. 동기화 함수 사용")
    sync_csv_sheets(CSV_FILE, WEB_APP_URL, SHEET_ID, '시트1', direction='csv_to_sheets')

    print("\n모든 작업 완료!")


if __name__ == "__main__":
    main()