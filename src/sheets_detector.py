"""
Google Sheets 시트명 자동 감지 및 매핑 모듈
"""

import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# 기존 sheets_client import
from sheets_client import GoogleSheetsClient

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()


class SheetsDetector:
    """Google Sheets 시트명 자동 감지 클래스"""

    def __init__(self, web_app_url: str = None, sheet_id: str = None):
        """
        Args:
            web_app_url: Apps Script 웹 앱 URL
            sheet_id: Google Sheets ID
        """
        self.web_app_url = web_app_url or os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
        self.sheet_id = sheet_id or os.getenv('GOOGLE_SHEETS_SHEET_ID')

        if not self.web_app_url or not self.sheet_id:
            raise ValueError("웹 앱 URL과 시트 ID가 필요합니다.")

        self.client = GoogleSheetsClient(self.web_app_url)
        self.available_sheets = []
        self.sheet_mapping = {}

    def get_available_sheets(self) -> List[str]:
        """
        Google Sheets에서 사용 가능한 시트명 목록을 가져옵니다.

        Note: Google Apps Script의 제한으로 인해 직접적인 시트 목록 조회는 어렵습니다.
        대신 일반적인 시트명들을 테스트해서 존재 여부를 확인합니다.
        """
        # 우선순위가 높은 시트명들 (가장 가능성이 높은 것부터)
        priority_sheet_names = [
            '시트1', 'Sheet1', 'Sheet 1'
        ]

        # 추가로 확인할 시트명들
        additional_sheet_names = [
            'Main', '메인', 'Data', '데이터',
            'Summary', '요약', '분석',
            '메인데이터', '상위성과', '피벗테이블'
        ]

        available_sheets = []

        logger.info("사용 가능한 시트명 검색 중...")

        # 먼저 우선순위 높은 시트들 확인
        for sheet_name in priority_sheet_names:
            try:
                # 시트에 읽기 시도
                result = self.client.read_sheet(self.sheet_id, sheet_name)

                if result.get('success') or 'Worksheet not found' not in result.get('error', ''):
                    available_sheets.append(sheet_name)
                    logger.info(f"  ✅ 발견: '{sheet_name}'")
                    # 첫 번째 시트를 찾으면 빠르게 종료 (기본 시트가 있다면 충분)
                    if len(available_sheets) >= 1:
                        break
                else:
                    logger.debug(f"  ❌ 없음: '{sheet_name}'")

            except Exception as e:
                logger.debug(f"  ❌ 오류: '{sheet_name}' - {str(e)}")
                continue

        # 기본 시트를 찾지 못했을 경우에만 추가 시트들 확인
        if not available_sheets:
            logger.info("기본 시트를 찾지 못했습니다. 추가 시트명 확인 중...")
            for sheet_name in additional_sheet_names:
                try:
                    result = self.client.read_sheet(self.sheet_id, sheet_name)

                    if result.get('success') or 'Worksheet not found' not in result.get('error', ''):
                        available_sheets.append(sheet_name)
                        logger.info(f"  ✅ 발견: '{sheet_name}'")
                    else:
                        logger.debug(f"  ❌ 없음: '{sheet_name}'")

                except Exception as e:
                    logger.debug(f"  ❌ 오류: '{sheet_name}' - {str(e)}")
                    continue

        self.available_sheets = available_sheets
        logger.info(f"총 {len(available_sheets)}개 시트 발견: {available_sheets}")

        return available_sheets

    def create_smart_mapping(self) -> Dict[str, str]:
        """
        발견된 시트들을 기반으로 스마트 매핑 생성

        Returns:
            시트 용도별 매핑 딕셔너리
        """
        if not self.available_sheets:
            self.get_available_sheets()

        mapping = {
            'main_data': None,
            'summary': None,
            'top_performers': None,
            'pivot_table': None
        }

        # 우선순위 기반 매핑
        for sheet_name in self.available_sheets:
            sheet_lower = sheet_name.lower()

            # 메인 데이터 시트 매핑
            if mapping['main_data'] is None:
                if any(keyword in sheet_lower for keyword in ['sheet1', '시트1', 'main', '메인', 'data', '데이터', '메인데이터']):
                    mapping['main_data'] = sheet_name

            # 요약 시트 매핑
            if mapping['summary'] is None:
                if any(keyword in sheet_lower for keyword in ['summary', '요약', '분석']):
                    mapping['summary'] = sheet_name

            # 상위 성과 시트 매핑
            if mapping['top_performers'] is None:
                if any(keyword in sheet_lower for keyword in ['top', '상위', '성과', 'performer', 'ranking', '랭킹']):
                    mapping['top_performers'] = sheet_name

            # 피벗 테이블 시트 매핑
            if mapping['pivot_table'] is None:
                if any(keyword in sheet_lower for keyword in ['pivot', '피벗', 'table', '테이블']):
                    mapping['pivot_table'] = sheet_name

        # 매핑되지 않은 용도에 대해 기본값 설정
        main_sheet = self.available_sheets[0] if self.available_sheets else 'Sheet1'

        for purpose, sheet_name in mapping.items():
            if sheet_name is None:
                mapping[purpose] = main_sheet
                logger.info(f"'{purpose}' 용도를 기본 시트 '{main_sheet}'에 매핑")

        self.sheet_mapping = mapping

        logger.info("시트 매핑 완료:")
        for purpose, sheet_name in mapping.items():
            logger.info(f"  {purpose}: '{sheet_name}'")

        return mapping

    def test_sheet_access(self, sheet_name: str) -> Dict[str, any]:
        """
        특정 시트에 대한 접근 테스트

        Args:
            sheet_name: 테스트할 시트명

        Returns:
            테스트 결과
        """
        logger.info(f"시트 접근 테스트: '{sheet_name}'")

        try:
            # 읽기 테스트
            read_result = self.client.read_sheet(self.sheet_id, sheet_name)

            if read_result.get('success'):
                # 쓰기 테스트 (빈 데이터로)
                test_data = [['테스트', '데이터']]
                write_result = self.client.append_rows(self.sheet_id, test_data, sheet_name)

                return {
                    'exists': True,
                    'readable': True,
                    'writable': write_result.get('success', False),
                    'rows': read_result.get('rows', 0),
                    'columns': read_result.get('columns', 0),
                    'error': None
                }
            else:
                error_msg = read_result.get('error', '')
                if 'Worksheet not found' in error_msg:
                    return {
                        'exists': False,
                        'readable': False,
                        'writable': False,
                        'error': 'Sheet not found'
                    }
                else:
                    return {
                        'exists': True,
                        'readable': False,
                        'writable': False,
                        'error': error_msg
                    }

        except Exception as e:
            return {
                'exists': False,
                'readable': False,
                'writable': False,
                'error': str(e)
            }

    def create_missing_sheets(self, required_sheets: List[str]) -> Dict[str, bool]:
        """
        필요한 시트들을 생성 시도

        Note: Google Apps Script의 제한으로 인해 새 시트 생성은 어렵습니다.
        대신 사용자에게 수동 생성을 안내합니다.

        Args:
            required_sheets: 필요한 시트명 목록

        Returns:
            생성 결과 (실제로는 안내 메시지)
        """
        missing_sheets = []

        for sheet_name in required_sheets:
            test_result = self.test_sheet_access(sheet_name)
            if not test_result['exists']:
                missing_sheets.append(sheet_name)

        if missing_sheets:
            logger.warning(f"다음 시트들이 존재하지 않습니다: {missing_sheets}")
            logger.info("해결 방법:")
            logger.info("1. Google Sheets에서 수동으로 시트 생성")
            logger.info("2. 기존 시트 사용 (자동 매핑)")

            return {sheet: False for sheet in missing_sheets}

        return {sheet: True for sheet in required_sheets}

    def get_recommended_config(self) -> Dict[str, str]:
        """
        추천 시트 설정 반환

        Returns:
            추천 설정 딕셔너리
        """
        self.get_available_sheets()
        mapping = self.create_smart_mapping()

        # 사용자 친화적인 설정 생성
        config = {
            'main_data_sheet': mapping['main_data'],
            'summary_sheet': mapping['summary'] if mapping['summary'] != mapping['main_data'] else f"{mapping['main_data']}_요약",
            'top_performers_sheet': mapping['top_performers'] if mapping['top_performers'] != mapping['main_data'] else f"{mapping['main_data']}_상위성과",
            'pivot_table_sheet': mapping['pivot_table'] if mapping['pivot_table'] != mapping['main_data'] else f"{mapping['main_data']}_피벗"
        }

        return config

    def print_sheet_status(self):
        """시트 상태 출력"""
        print("\n📊 Google Sheets 상태 분석")
        print("=" * 50)

        available_sheets = self.get_available_sheets()

        if available_sheets:
            print(f"✅ 발견된 시트 ({len(available_sheets)}개):")
            for sheet_name in available_sheets:
                test_result = self.test_sheet_access(sheet_name)
                status = "✅ 읽기/쓰기 가능" if test_result['writable'] else "⚠️ 읽기만 가능"
                rows = test_result.get('rows', 0)
                cols = test_result.get('columns', 0)
                print(f"  - '{sheet_name}': {status} ({rows}행 × {cols}열)")
        else:
            print("❌ 접근 가능한 시트를 찾을 수 없습니다.")

        print("\n🎯 추천 설정:")
        config = self.get_recommended_config()
        for purpose, sheet_name in config.items():
            print(f"  {purpose}: '{sheet_name}'")


def detect_sheets_auto() -> Dict[str, str]:
    """
    자동으로 시트 감지하고 설정 반환하는 헬퍼 함수

    Returns:
        시트 설정 딕셔너리
    """
    try:
        detector = SheetsDetector()
        return detector.get_recommended_config()
    except Exception as e:
        logger.error(f"시트 자동 감지 실패: {str(e)}")
        # 기본값 반환
        return {
            'main_data_sheet': 'Sheet1',
            'summary_sheet': 'Sheet1',
            'top_performers_sheet': 'Sheet1',
            'pivot_table_sheet': 'Sheet1'
        }