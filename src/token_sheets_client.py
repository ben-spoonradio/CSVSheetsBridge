"""
토큰 인증을 사용하는 Google Sheets 클라이언트
"""

import os
import requests
import json
from typing import List, Dict, Any, Optional


class TokenAuthSheetsClient:
    """토큰 인증을 사용하는 Google Sheets 클라이언트"""

    def __init__(self, web_app_url: str, access_token: str):
        """
        Args:
            web_app_url: Apps Script 웹 앱 URL
            access_token: 접근 토큰
        """
        self.web_app_url = web_app_url
        self.access_token = access_token
        self.session = requests.Session()

    def read_sheet(self, sheet_id: str, sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """스프레드시트 데이터 읽기"""
        params = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'token': self.access_token  # 토큰 추가
        }

        try:
            response = self.session.get(self.web_app_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON response: {str(e)}'}

    def append_rows(self, sheet_id: str, data: List[List],
                   sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """행 추가"""
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'append',
            'data': data,
            'token': self.access_token  # 토큰 추가
        }

        return self._post_request(payload)

    def update_range(self, sheet_id: str, range_str: str, data: List[List],
                    sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """특정 범위 업데이트"""
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'update',
            'range': range_str,
            'data': data,
            'token': self.access_token  # 토큰 추가
        }

        return self._post_request(payload)

    def overwrite_sheet(self, sheet_id: str, data: List[List],
                       sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """시트 전체 내용 덮어쓰기"""
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'overwrite',
            'data': data,
            'token': self.access_token  # 토큰 추가
        }

        return self._post_request(payload)

    def clear_sheet(self, sheet_id: str, range_str: Optional[str] = None,
                   sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """시트 내용 지우기"""
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'clear',
            'token': self.access_token  # 토큰 추가
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


def create_secure_client() -> TokenAuthSheetsClient:
    """환경변수를 사용하여 보안 클라이언트 생성"""
    from dotenv import load_dotenv
    load_dotenv()

    web_app_url = os.getenv('GOOGLE_SHEETS_WEB_APP_URL')
    access_token = os.getenv('GOOGLE_SHEETS_ACCESS_TOKEN')

    if not web_app_url:
        raise ValueError("GOOGLE_SHEETS_WEB_APP_URL 환경변수가 필요합니다.")

    if not access_token:
        raise ValueError("GOOGLE_SHEETS_ACCESS_TOKEN 환경변수가 필요합니다.")

    return TokenAuthSheetsClient(web_app_url, access_token)