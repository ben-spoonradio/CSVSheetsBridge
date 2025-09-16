import requests
import json
import time
from typing import List, Dict, Any, Optional
from functools import wraps


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """실패 시 재시도 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                result = func(*args, **kwargs)

                if 'error' not in result:
                    return result

                if attempt < max_retries - 1:
                    print(f"재시도 {attempt + 1}/{max_retries}: {result.get('error')}")
                    time.sleep(delay * (2 ** attempt))
                else:
                    print(f"최종 실패: {result.get('error')}")
                    return result

            return result
        return wrapper
    return decorator


class GoogleSheetsClient:
    """Google Apps Script 웹 앱을 통한 Google Sheets 클라이언트"""

    def __init__(self, web_app_url: str):
        """
        Args:
            web_app_url: Apps Script 웹 앱 URL
        """
        self.web_app_url = web_app_url
        self.session = requests.Session()

    def read_sheet(self, sheet_id: str, sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """
        스프레드시트 데이터 읽기

        Args:
            sheet_id: 스프레드시트 ID
            sheet_name: 시트 이름 (기본값: 'Sheet1')

        Returns:
            응답 데이터 딕셔너리
        """
        params = {
            'sheetId': sheet_id,
            'sheetName': sheet_name
        }

        try:
            response = self.session.get(self.web_app_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON response: {str(e)}'}

    def update_range(self, sheet_id: str, range_str: str, data: List[List],
                    sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """
        특정 범위 업데이트

        Args:
            sheet_id: 스프레드시트 ID
            range_str: 범위 (예: 'A1:C3')
            data: 2차원 리스트 데이터
            sheet_name: 시트 이름
        """
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'update',
            'range': range_str,
            'data': data
        }

        return self._post_request(payload)

    def append_rows(self, sheet_id: str, data: List[List],
                   sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """
        행 추가

        Args:
            sheet_id: 스프레드시트 ID
            data: 추가할 데이터 (2차원 리스트)
            sheet_name: 시트 이름
        """
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'append',
            'data': data
        }

        return self._post_request(payload)

    def overwrite_sheet(self, sheet_id: str, data: List[List],
                       sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """
        시트 전체 내용 덮어쓰기

        Args:
            sheet_id: 스프레드시트 ID
            data: 새로운 데이터 (2차원 리스트)
            sheet_name: 시트 이름
        """
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'overwrite',
            'data': data
        }

        return self._post_request(payload)

    def clear_sheet(self, sheet_id: str, range_str: Optional[str] = None,
                   sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """
        시트 내용 지우기

        Args:
            sheet_id: 스프레드시트 ID
            range_str: 지울 범위 (None이면 전체)
            sheet_name: 시트 이름
        """
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'clear'
        }

        if range_str:
            payload['range'] = range_str

        return self._post_request(payload)

    def _post_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST 요청 헬퍼 메서드"""
        try:
            response = self.session.post(
                self.web_app_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON response: {str(e)}'}


class RobustGoogleSheetsClient(GoogleSheetsClient):
    """재시도 기능이 포함된 안정적인 Google Sheets 클라이언트"""

    @retry_on_failure(max_retries=3, delay=1.0)
    def read_sheet(self, sheet_id: str, sheet_name: str = 'Sheet1'):
        return super().read_sheet(sheet_id, sheet_name)

    @retry_on_failure(max_retries=3, delay=1.0)
    def update_range(self, sheet_id: str, range_str: str, data: List[List],
                    sheet_name: str = 'Sheet1'):
        return super().update_range(sheet_id, range_str, data, sheet_name)

    @retry_on_failure(max_retries=3, delay=1.0)
    def append_rows(self, sheet_id: str, data: List[List],
                   sheet_name: str = 'Sheet1'):
        return super().append_rows(sheet_id, data, sheet_name)

    @retry_on_failure(max_retries=3, delay=1.0)
    def overwrite_sheet(self, sheet_id: str, data: List[List],
                       sheet_name: str = 'Sheet1'):
        return super().overwrite_sheet(sheet_id, data, sheet_name)

    @retry_on_failure(max_retries=3, delay=1.0)
    def clear_sheet(self, sheet_id: str, range_str: Optional[str] = None,
                   sheet_name: str = 'Sheet1'):
        return super().clear_sheet(sheet_id, range_str, sheet_name)


def extract_sheet_id_from_url(url: str) -> str:
    """
    Google Sheets URL에서 스프레드시트 ID 추출

    Args:
        url: Google Sheets URL

    Returns:
        스프레드시트 ID
    """
    if '/d/' in url:
        return url.split('/d/')[1].split('/')[0]
    return url