"""
OAuth 인증을 사용하는 Google Sheets 클라이언트
"""

import os
import json
import requests
from typing import Dict, Any, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import google.auth

# Google Sheets API 스코프
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class OAuthGoogleSheetsClient:
    """OAuth 인증을 사용하는 Google Sheets 클라이언트"""

    def __init__(self, web_app_url: str, credentials_file: str = 'credentials.json'):
        """
        Args:
            web_app_url: Apps Script 웹 앱 URL
            credentials_file: Google OAuth 인증 파일 경로
        """
        self.web_app_url = web_app_url
        self.credentials_file = credentials_file
        self.creds = None
        self.session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        """OAuth 인증 수행"""
        token_file = 'token.json'

        # 기존 토큰이 있으면 로드
        if os.path.exists(token_file):
            self.creds = Credentials.from_authorized_user_file(token_file, SCOPES)

        # 토큰이 없거나 유효하지 않으면 새로 생성
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"OAuth 인증 파일이 필요합니다: {self.credentials_file}\n"
                        "Google Cloud Console에서 OAuth 클라이언트 ID를 생성하고 "
                        "credentials.json으로 저장하세요."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # 토큰 저장
            with open(token_file, 'w') as token:
                token.write(self.creds.to_json())

        print(f"✅ OAuth 인증 완료: {self.creds.service_account_email or '사용자 계정'}")

    def _make_authenticated_request(self, method: str, params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """인증된 요청 보내기"""
        # OAuth 토큰을 Authorization 헤더에 추가
        headers = {
            'Authorization': f'Bearer {self.creds.token}',
            'Content-Type': 'application/json'
        }

        try:
            if method.upper() == 'GET':
                response = self.session.get(self.web_app_url, params=params, headers=headers)
            else:  # POST
                response = self.session.post(self.web_app_url, json=data, headers=headers)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON response: {str(e)}'}

    def read_sheet(self, sheet_id: str, sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """스프레드시트 데이터 읽기 (OAuth 인증)"""
        params = {
            'sheetId': sheet_id,
            'sheetName': sheet_name
        }
        return self._make_authenticated_request('GET', params=params)

    def append_rows(self, sheet_id: str, data: List[List], sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """행 추가 (OAuth 인증)"""
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'append',
            'data': data
        }
        return self._make_authenticated_request('POST', data=payload)

    def update_range(self, sheet_id: str, range_str: str, data: List[List],
                    sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """범위 업데이트 (OAuth 인증)"""
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'update',
            'range': range_str,
            'data': data
        }
        return self._make_authenticated_request('POST', data=payload)

    def overwrite_sheet(self, sheet_id: str, data: List[List],
                       sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """시트 덮어쓰기 (OAuth 인증)"""
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'overwrite',
            'data': data
        }
        return self._make_authenticated_request('POST', data=payload)

    def clear_sheet(self, sheet_id: str, range_str: str = None,
                   sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        """시트 지우기 (OAuth 인증)"""
        payload = {
            'sheetId': sheet_id,
            'sheetName': sheet_name,
            'action': 'clear'
        }
        if range_str:
            payload['range'] = range_str

        return self._make_authenticated_request('POST', data=payload)


class ServiceAccountSheetsClient:
    """서비스 계정을 사용하는 Google Sheets 클라이언트"""

    def __init__(self, web_app_url: str, service_account_file: str = 'service-account.json'):
        """
        Args:
            web_app_url: Apps Script 웹 앱 URL
            service_account_file: 서비스 계정 JSON 파일 경로
        """
        self.web_app_url = web_app_url
        self.service_account_file = service_account_file
        self.creds = None
        self.session = requests.Session()
        self._authenticate()

    def _authenticate(self):
        """서비스 계정 인증"""
        if not os.path.exists(self.service_account_file):
            raise FileNotFoundError(
                f"서비스 계정 파일이 필요합니다: {self.service_account_file}\n"
                "Google Cloud Console에서 서비스 계정을 생성하고 "
                "키를 다운로드하여 service-account.json으로 저장하세요."
            )

        from google.oauth2 import service_account

        self.creds = service_account.Credentials.from_service_account_file(
            self.service_account_file, scopes=SCOPES)

        print(f"✅ 서비스 계정 인증 완료: {self.creds.service_account_email}")

    def _make_authenticated_request(self, method: str, params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """서비스 계정으로 인증된 요청"""
        # 서비스 계정 토큰 가져오기
        self.creds.refresh(Request())

        headers = {
            'Authorization': f'Bearer {self.creds.token}',
            'Content-Type': 'application/json'
        }

        try:
            if method.upper() == 'GET':
                response = self.session.get(self.web_app_url, params=params, headers=headers)
            else:  # POST
                response = self.session.post(self.web_app_url, json=data, headers=headers)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {'error': f'Request failed: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'error': f'Invalid JSON response: {str(e)}'}

    # 동일한 메서드들 (read_sheet, append_rows, etc.)
    def read_sheet(self, sheet_id: str, sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        params = {'sheetId': sheet_id, 'sheetName': sheet_name}
        return self._make_authenticated_request('GET', params=params)

    def append_rows(self, sheet_id: str, data: List[List], sheet_name: str = 'Sheet1') -> Dict[str, Any]:
        payload = {'sheetId': sheet_id, 'sheetName': sheet_name, 'action': 'append', 'data': data}
        return self._make_authenticated_request('POST', data=payload)