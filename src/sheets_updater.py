"""
Google Sheets 업데이터
Appsflyer 처리된 데이터를 Google Sheets에 자동 업로드
"""

import os
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from dotenv import load_dotenv

# 기존 sheets_client import
from sheets_client import GoogleSheetsClient

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()


class SheetsUpdater:
    """Google Sheets 업데이트 관리 클래스"""

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

        # 시트명 자동 감지
        self.sheet_config = self._detect_sheet_names()
        logger.info("Google Sheets 클라이언트 초기화 완료")
        logger.info(f"감지된 시트 설정: {self.sheet_config}")

    def _detect_sheet_names(self) -> Dict[str, str]:
        """시트명 자동 감지"""
        try:
            from sheets_detector import detect_sheets_auto
            return detect_sheets_auto()
        except Exception as e:
            logger.warning(f"시트 자동 감지 실패: {str(e)}, 기본값 사용")
            return {
                'main_data_sheet': 'Sheet1',
                'summary_sheet': 'Sheet1',
                'top_performers_sheet': 'Sheet1',
                'pivot_table_sheet': 'Sheet1'
            }

    def prepare_data_for_sheets(self, df: pd.DataFrame) -> List[List]:
        """DataFrame을 Google Sheets용 2차원 리스트로 변환"""
        if df.empty:
            return []

        # DataFrame 복사본 생성
        df_clean = df.copy()

        # Categorical 컬럼을 문자열로 변환
        for col in df_clean.columns:
            if pd.api.types.is_categorical_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].astype(str)

        # NaN 값을 빈 문자열로 변경
        df_clean = df_clean.fillna('')

        # 무한대 값을 'N/A'로 변경
        df_clean = df_clean.replace([float('inf'), float('-inf')], 'N/A')

        # 숫자를 문자열로 변환 (소수점 2자리까지)
        for col in df_clean.columns:
            if df_clean[col].dtype in ['float64', 'int64']:
                if col in ['cost', 'cpc', 'cpi', 'd1_retained_cac']:
                    # 비용 관련은 소수점 2자리
                    df_clean[col] = df_clean[col].apply(
                        lambda x: f"{float(x):.2f}" if str(x) not in ['N/A', ''] else x
                    )
                elif col in ['ctr', 'd1_retention_rate']:
                    # 퍼센트는 소수점 1자리
                    df_clean[col] = df_clean[col].apply(
                        lambda x: f"{float(x):.1f}%" if str(x) not in ['N/A', ''] else x
                    )
                else:
                    # 정수형은 소수점 없이
                    df_clean[col] = df_clean[col].apply(
                        lambda x: str(int(float(x))) if str(x) not in ['N/A', ''] else x
                    )

        # 헤더 + 데이터로 변환
        headers = list(df_clean.columns)
        data_rows = df_clean.values.tolist()

        return [headers] + data_rows

    def create_summary_sheet_data(self, stats: Dict) -> List[List]:
        """요약 통계를 시트용 데이터로 변환"""
        summary_data = [
            ['항목', '값'],
            ['총 콘텐츠 수', str(stats.get('total_contents', 0))],
            ['총 비용', f"${stats.get('total_cost', 0):,.2f}"],
            ['총 설치 수', f"{stats.get('total_installs', 0):,}"],
            ['평균 D1 Retained CAC', f"${stats.get('avg_d1_retained_cac', 0):.2f}"],
            ['업데이트 시간', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]

        # 매체별 분포
        summary_data.append(['', ''])  # 빈 줄
        summary_data.append(['매체별 분포', ''])
        media_dist = stats.get('media_distribution', {})
        for media, count in media_dist.items():
            summary_data.append([f'  {media}', str(count)])

        # 플랫폼별 분포
        summary_data.append(['', ''])  # 빈 줄
        summary_data.append(['플랫폼별 분포', ''])
        platform_dist = stats.get('platform_distribution', {})
        for platform, count in platform_dist.items():
            summary_data.append([f'  {platform}', str(count)])

        return summary_data

    def create_top_performers_data(self, stats: Dict) -> List[List]:
        """상위 성과 콘텐츠를 시트용 데이터로 변환"""
        top_performers = stats.get('top_performers', [])

        if not top_performers:
            return [['상위 성과 콘텐츠 없음']]

        headers = ['순위', '콘텐츠명', '매체', '플랫폼', '등급', 'D1 Retained CAC']
        data_rows = []

        for i, performer in enumerate(top_performers[:10], 1):  # 상위 10개만
            row = [
                str(i),
                performer.get('content_name', ''),
                performer.get('media_type', ''),
                performer.get('platform_normalized', ''),
                performer.get('performance_grade', ''),
                f"${performer.get('d1_retained_cac', 0):.2f}" if performer.get('d1_retained_cac') not in [float('inf'), 'N/A'] else 'N/A'
            ]
            data_rows.append(row)

        return [headers] + data_rows

    def update_main_data_sheet(self, df: pd.DataFrame, sheet_name: str = None) -> Dict[str, Any]:
        """메인 데이터를 Google Sheets에 업데이트"""
        if sheet_name is None:
            sheet_name = self.sheet_config['main_data_sheet']
        logger.info(f"메인 데이터 시트 업데이트 시작: {sheet_name}")

        # 데이터 준비
        sheet_data = self.prepare_data_for_sheets(df)

        if not sheet_data:
            logger.warning("업데이트할 데이터가 없습니다.")
            return {'success': False, 'error': '데이터 없음'}

        try:
            # 시트 덮어쓰기
            result = self.client.overwrite_sheet(self.sheet_id, sheet_data, sheet_name)

            if result.get('success'):
                logger.info(f"메인 데이터 업데이트 성공: {len(sheet_data)}행")
                return {'success': True, 'rows': len(sheet_data), 'columns': len(sheet_data[0])}
            else:
                logger.error(f"메인 데이터 업데이트 실패: {result.get('error')}")
                return result

        except Exception as e:
            logger.error(f"메인 데이터 업데이트 중 오류: {str(e)}")
            return {'success': False, 'error': str(e)}

    def update_summary_sheet(self, stats: Dict, sheet_name: str = None) -> Dict[str, Any]:
        """요약 통계를 Google Sheets에 업데이트"""
        if sheet_name is None:
            sheet_name = self.sheet_config.get('summary_sheet', '요약')
        logger.info(f"요약 시트 업데이트 시작: {sheet_name}")

        try:
            # 요약 데이터 생성
            summary_data = self.create_summary_sheet_data(stats)

            # 시트 덮어쓰기
            result = self.client.overwrite_sheet(self.sheet_id, summary_data, sheet_name)

            if result.get('success'):
                logger.info(f"요약 시트 업데이트 성공: {len(summary_data)}행")
                return {'success': True, 'rows': len(summary_data)}
            else:
                logger.error(f"요약 시트 업데이트 실패: {result.get('error')}")
                return result

        except Exception as e:
            logger.error(f"요약 시트 업데이트 중 오류: {str(e)}")
            return {'success': False, 'error': str(e)}

    def update_top_performers_sheet(self, stats: Dict, sheet_name: str = None) -> Dict[str, Any]:
        """상위 성과 콘텐츠를 Google Sheets에 업데이트"""
        if sheet_name is None:
            sheet_name = self.sheet_config.get('top_performers_sheet', '상위성과')
        logger.info(f"상위 성과 시트 업데이트 시작: {sheet_name}")

        try:
            # 상위 성과 데이터 생성
            top_data = self.create_top_performers_data(stats)

            # 시트 덮어쓰기
            result = self.client.overwrite_sheet(self.sheet_id, top_data, sheet_name)

            if result.get('success'):
                logger.info(f"상위 성과 시트 업데이트 성공: {len(top_data)}행")
                return {'success': True, 'rows': len(top_data)}
            else:
                logger.error(f"상위 성과 시트 업데이트 실패: {result.get('error')}")
                return result

        except Exception as e:
            logger.error(f"상위 성과 시트 업데이트 중 오류: {str(e)}")
            return {'success': False, 'error': str(e)}

    def create_pivot_table_data(self, df: pd.DataFrame) -> List[List]:
        """피벗 테이블 형태의 데이터 생성"""
        if df.empty:
            return []

        try:
            # 매체 × 플랫폼 피벗 테이블
            pivot_columns = ['media_type', 'platform_normalized']
            value_column = 'd1_retained_cac'

            # 존재하는 컬럼만 사용
            available_pivot_cols = [col for col in pivot_columns if col in df.columns]

            if not available_pivot_cols or value_column not in df.columns:
                logger.warning("피벗 테이블 생성에 필요한 컬럼이 부족합니다.")
                return [['피벗 테이블 생성 불가 - 필요한 컬럼 없음']]

            # 피벗 테이블 생성
            if len(available_pivot_cols) == 2:
                pivot_df = df.pivot_table(
                    values=value_column,
                    index=available_pivot_cols[0],
                    columns=available_pivot_cols[1],
                    aggfunc='mean',
                    fill_value=0
                )
            else:
                # 1차원 그룹화
                pivot_df = df.groupby(available_pivot_cols[0])[value_column].mean().to_frame()

            # 피벗 테이블을 리스트 형태로 변환
            pivot_data = []

            # 헤더 추가
            if isinstance(pivot_df.columns, pd.MultiIndex) or len(pivot_df.columns) > 1:
                header = ['매체/플랫폼'] + [str(col) for col in pivot_df.columns]
            else:
                header = ['매체', '평균 D1 Retained CAC']

            pivot_data.append(header)

            # 데이터 추가
            for index, row in pivot_df.iterrows():
                row_data = [str(index)]
                for value in row:
                    if value == 0:
                        row_data.append('N/A')
                    elif isinstance(value, (int, float)):
                        row_data.append(f"${value:.2f}")
                    else:
                        row_data.append(str(value))
                pivot_data.append(row_data)

            return pivot_data

        except Exception as e:
            logger.error(f"피벗 테이블 생성 중 오류: {str(e)}")
            return [['피벗 테이블 생성 중 오류 발생', str(e)]]

    def update_pivot_sheet(self, df: pd.DataFrame, sheet_name: str = None) -> Dict[str, Any]:
        """피벗 테이블을 Google Sheets에 업데이트"""
        if sheet_name is None:
            sheet_name = self.sheet_config.get('pivot_table_sheet', '피벗테이블')
        logger.info(f"피벗 테이블 시트 업데이트 시작: {sheet_name}")

        try:
            # 피벗 데이터 생성
            pivot_data = self.create_pivot_table_data(df)

            # 시트 덮어쓰기
            result = self.client.overwrite_sheet(self.sheet_id, pivot_data, sheet_name)

            if result.get('success'):
                logger.info(f"피벗 테이블 업데이트 성공: {len(pivot_data)}행")
                return {'success': True, 'rows': len(pivot_data)}
            else:
                logger.error(f"피벗 테이블 업데이트 실패: {result.get('error')}")
                return result

        except Exception as e:
            logger.error(f"피벗 테이블 업데이트 중 오류: {str(e)}")
            return {'success': False, 'error': str(e)}

    def update_all_sheets(self, df: pd.DataFrame, stats: Dict) -> Dict[str, Any]:
        """모든 시트를 일괄 업데이트"""
        logger.info("전체 시트 업데이트 시작")

        results = {}

        # 1. 메인 데이터 업데이트
        results['main_data'] = self.update_main_data_sheet(df)

        # 2. 요약 시트 업데이트
        results['summary'] = self.update_summary_sheet(stats)

        # 3. 상위 성과 시트 업데이트
        results['top_performers'] = self.update_top_performers_sheet(stats)

        # 4. 피벗 테이블 업데이트
        results['pivot_table'] = self.update_pivot_sheet(df)

        # 전체 성공 여부 판단
        all_success = all(result.get('success', False) for result in results.values())

        logger.info(f"전체 시트 업데이트 완료 - 성공: {all_success}")

        return {
            'overall_success': all_success,
            'individual_results': results,
            'summary': {
                'successful_sheets': sum(1 for r in results.values() if r.get('success')),
                'total_sheets': len(results),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }

    def backup_current_data(self, backup_sheet_name: str = None) -> Dict[str, Any]:
        """현재 시트 데이터 백업"""
        if not backup_sheet_name:
            backup_sheet_name = f"백업_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        logger.info(f"데이터 백업 시작: {backup_sheet_name}")

        try:
            # 현재 메인 시트 데이터 읽기
            main_sheet_name = self.sheet_config.get('main_data_sheet', '메인데이터')
            current_data = self.client.read_sheet(self.sheet_id, main_sheet_name)

            if not current_data.get('success'):
                logger.warning("백업할 현재 데이터를 읽을 수 없습니다.")
                return {'success': False, 'error': '현재 데이터 읽기 실패'}

            # 백업 시트에 저장
            backup_result = self.client.overwrite_sheet(
                self.sheet_id,
                current_data['data'],
                backup_sheet_name
            )

            if backup_result.get('success'):
                logger.info(f"백업 완료: {backup_sheet_name}")
                return {'success': True, 'backup_sheet': backup_sheet_name}
            else:
                logger.error(f"백업 실패: {backup_result.get('error')}")
                return backup_result

        except Exception as e:
            logger.error(f"백업 중 오류: {str(e)}")
            return {'success': False, 'error': str(e)}


def create_sheets_config_template():
    """시트 설정 템플릿 생성"""
    config = {
        'sheet_names': {
            'main_data': '메인데이터',
            'summary': '요약',
            'top_performers': '상위성과',
            'pivot_table': '피벗테이블'
        },
        'column_formats': {
            'cost': '${:,.2f}',
            'cpc': '${:.2f}',
            'cpi': '${:.2f}',
            'd1_retained_cac': '${:.2f}',
            'ctr': '{:.1f}%',
            'd1_retention_rate': '{:.1f}%'
        },
        'backup_settings': {
            'auto_backup': True,
            'backup_prefix': '백업_',
            'max_backups': 10
        }
    }

    return config