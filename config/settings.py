"""
설정 파일
Google Sheets 연동을 위한 기본 설정값들
"""

import os
from typing import Optional


class SheetsConfig:
    """Google Sheets 연동 설정 클래스"""

    def __init__(self, web_app_url: Optional[str] = None, sheet_id: Optional[str] = None):
        """
        Args:
            web_app_url: Apps Script 웹 앱 URL
            sheet_id: 기본 스프레드시트 ID
        """
        self.web_app_url = web_app_url or self._get_env_var('GOOGLE_SHEETS_WEB_APP_URL')
        self.sheet_id = sheet_id or self._get_env_var('GOOGLE_SHEETS_SHEET_ID')

    def _get_env_var(self, var_name: str) -> Optional[str]:
        """환경변수에서 값 가져오기"""
        return os.getenv(var_name)

    def is_configured(self) -> bool:
        """설정이 완료되었는지 확인"""
        return bool(self.web_app_url and self.sheet_id)

    def validate(self):
        """설정 유효성 검사"""
        if not self.web_app_url:
            raise ValueError("WEB_APP_URL이 설정되지 않았습니다.")

        if not self.sheet_id:
            raise ValueError("SHEET_ID가 설정되지 않았습니다.")

        if not self.web_app_url.startswith('https://'):
            raise ValueError("WEB_APP_URL은 HTTPS URL이어야 합니다.")

    def __str__(self):
        return f"SheetsConfig(web_app_url={'*' * 10 if self.web_app_url else None}, sheet_id={self.sheet_id[:10] + '...' if self.sheet_id else None})"


# 기본 설정 인스턴스
default_config = SheetsConfig()


# 환경변수 템플릿
ENV_TEMPLATE = """
# Google Sheets Apps Script 웹 앱 URL
# https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec 형태
GOOGLE_SHEETS_WEB_APP_URL=

# 기본 스프레드시트 ID
# Google Sheets URL에서 /d/ 다음에 나오는 ID 부분
GOOGLE_SHEETS_SHEET_ID=
"""