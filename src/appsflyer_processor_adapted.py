"""
실제 Data_dua.csv 형식에 맞춘 Appsflyer 데이터 처리기
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import os
import logging
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppsflyerDataProcessorAdapted:
    """실제 Data_dua.csv 형식에 맞춘 Appsflyer Raw Data 처리 클래스"""

    def __init__(self, csv_file_path: str):
        """
        Args:
            csv_file_path: Appsflyer CSV 파일 경로
        """
        self.csv_file_path = csv_file_path
        self.raw_data = None
        self.processed_data = None

    def load_csv(self) -> pd.DataFrame:
        """CSV 파일 로드"""
        try:
            logger.info(f"CSV 파일 로드 시작: {self.csv_file_path}")

            # UTF-8 BOM 처리를 위해 encoding 설정
            self.raw_data = pd.read_csv(self.csv_file_path, encoding='utf-8-sig')

            logger.info(f"CSV 로드 성공")
            logger.info(f"데이터 크기: {self.raw_data.shape}")
            logger.info(f"컬럼 목록: {list(self.raw_data.columns)}")

            return self.raw_data

        except Exception as e:
            logger.error(f"CSV 파일 로드 실패: {str(e)}")
            raise

    def clean_and_normalize_columns(self) -> pd.DataFrame:
        """컬럼명 정규화 및 데이터 정제"""
        if self.raw_data is None:
            raise ValueError("데이터가 로드되지 않았습니다.")

        df = self.raw_data.copy()

        # 컬럼명 매핑
        column_mapping = {
            'Ad': 'ad_name',
            'Cost (sum)': 'cost',
            'Impressions (sum)': 'impressions',
            'Clicks (sum)': 'clicks',
            'Installs (sum)': 'installs',
            'Unique Users - etc_sign_up (sum)': 'signups',
            'Retention Day 01 (sum)': 'd1_retained_users'
        }

        # 컬럼명 변경
        df = df.rename(columns=column_mapping)
        logger.info("컬럼명 정규화 완료")

        # 숫자형 데이터 정제
        numeric_columns = ['cost', 'impressions', 'clicks', 'installs', 'signups', 'd1_retained_users']

        for col in numeric_columns:
            if col in df.columns:
                # $ 기호 및 콤마 제거
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '')

                # 숫자로 변환
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        logger.info("데이터 정제 완료")
        return df

    def extract_campaign_info_from_ad_name(self, df: pd.DataFrame) -> pd.DataFrame:
        """광고명에서 캠페인 정보 추출"""
        processed_df = df.copy()

        # 광고명 분석을 통한 정보 추출
        def extract_info(ad_name):
            if pd.isna(ad_name) or ad_name == '':
                return {
                    'media_type': 'unknown',
                    'content_theme': 'unknown',
                    'creative_type': 'unknown',
                    'platform': 'unknown'
                }

            ad_name_lower = str(ad_name).lower()

            # 매체 추출 (광고명에서 추론)
            media_type = 'unknown'
            if 'ttcx' in ad_name_lower or 'tiktok' in ad_name_lower:
                media_type = 'tiktok'
            elif 'meta' in ad_name_lower or 'facebook' in ad_name_lower or 'instagram' in ad_name_lower:
                media_type = 'meta'
            elif 'echo' in ad_name_lower:
                media_type = 'echo'  # Echo 매체로 추정
            elif 'spoon' in ad_name_lower:
                media_type = 'spoon'  # Spoon 매체로 추정
            elif 'innoceans' in ad_name_lower:
                media_type = 'innoceans'  # Innoceans 매체로 추정

            # 콘텐츠 테마 추출
            content_theme = 'general'
            if 'participation' in ad_name_lower:
                content_theme = 'participation'
            elif 'blinddate' in ad_name_lower:
                content_theme = 'blinddate'
            elif 'interest' in ad_name_lower:
                content_theme = 'interest'
            elif 'tpo' in ad_name_lower:
                content_theme = 'tpo'

            # 크리에이티브 타입 추출
            creative_type = 'video'
            if 'vdo' in ad_name_lower or 'video' in ad_name_lower:
                creative_type = 'video'
            elif 'img' in ad_name_lower or 'image' in ad_name_lower:
                creative_type = 'image'

            # 플랫폼 추출 (광고명에서 추론이 어려워 기본값 설정)
            platform = 'mixed'  # AOS/iOS 구분이 어려움

            return {
                'media_type': media_type,
                'content_theme': content_theme,
                'creative_type': creative_type,
                'platform': platform
            }

        # 각 광고명에 대해 정보 추출
        extracted_info = processed_df['ad_name'].apply(extract_info)

        # 추출된 정보를 별도 컬럼으로 분리
        for key in ['media_type', 'content_theme', 'creative_type', 'platform']:
            processed_df[key] = [info[key] for info in extracted_info]

        # 콘텐츠명 생성 (원본 ad_name 사용)
        processed_df['content_name'] = processed_df['ad_name']

        logger.info("광고명에서 캠페인 정보 추출 완료")
        logger.info(f"매체 분포: {processed_df['media_type'].value_counts().to_dict()}")

        return processed_df

    def calculate_kpis(self, data: pd.DataFrame) -> pd.DataFrame:
        """KPI 계산"""
        processed_data = data.copy()

        # CPC (Cost Per Click)
        processed_data['cpc'] = np.where(
            processed_data['clicks'] > 0,
            processed_data['cost'] / processed_data['clicks'],
            0
        )

        # CPI (Cost Per Install)
        processed_data['cpi'] = np.where(
            processed_data['installs'] > 0,
            processed_data['cost'] / processed_data['installs'],
            0
        )

        # CTR (Click Through Rate)
        processed_data['ctr'] = np.where(
            processed_data['impressions'] > 0,
            (processed_data['clicks'] / processed_data['impressions']) * 100,
            0
        )

        # D1 Retained CAC (주요 KPI)
        processed_data['d1_retained_cac'] = np.where(
            processed_data['d1_retained_users'] > 0,
            processed_data['cost'] / processed_data['d1_retained_users'],
            np.inf  # D1 유지 유저가 0인 경우 무한대
        )

        # D1 Retention Rate
        processed_data['d1_retention_rate'] = np.where(
            processed_data['installs'] > 0,
            (processed_data['d1_retained_users'] / processed_data['installs']) * 100,
            0
        )

        # Signup Rate (추가 KPI)
        processed_data['signup_rate'] = np.where(
            processed_data['installs'] > 0,
            (processed_data['signups'] / processed_data['installs']) * 100,
            0
        )

        # Cost per Signup
        processed_data['cost_per_signup'] = np.where(
            processed_data['signups'] > 0,
            processed_data['cost'] / processed_data['signups'],
            np.inf
        )

        logger.info("KPI 계산 완료")
        return processed_data

    def rank_content_performance(self, data: pd.DataFrame) -> pd.DataFrame:
        """콘텐츠 성과 순위 매기기"""
        ranked_data = data.copy()

        # D1 Retained CAC 기준 순위 (낮을수록 좋음)
        ranked_data['d1_retained_cac_for_rank'] = ranked_data['d1_retained_cac'].replace([np.inf, -np.inf], 9999999)

        # 전체 순위
        ranked_data['rank_d1_cac'] = ranked_data['d1_retained_cac_for_rank'].rank(ascending=True)

        # 보조 KPI 순위
        ranked_data['rank_cpi'] = ranked_data['cpi'].rank(ascending=True)
        ranked_data['rank_cpc'] = ranked_data['cpc'].rank(ascending=True)
        ranked_data['rank_ctr'] = ranked_data['ctr'].rank(ascending=False)  # 높을수록 좋음

        # 종합 점수 계산 (가중 평균)
        weights = {
            'rank_d1_cac': 0.4,    # 주요 KPI
            'rank_cpi': 0.25,
            'rank_cpc': 0.2,
            'rank_ctr': 0.15
        }

        # 가중 평균 계산
        ranked_data['composite_score'] = (
            ranked_data['rank_d1_cac'] * weights['rank_d1_cac'] +
            ranked_data['rank_cpi'] * weights['rank_cpi'] +
            ranked_data['rank_cpc'] * weights['rank_cpc'] +
            ranked_data['rank_ctr'] * weights['rank_ctr']
        )

        ranked_data['overall_rank'] = ranked_data['composite_score'].rank(ascending=True)

        # 성과 등급 부여
        total_contents = len(ranked_data)
        ranked_data['performance_grade'] = pd.cut(
            ranked_data['overall_rank'],
            bins=[0, total_contents*0.2, total_contents*0.5, total_contents*0.8, total_contents],
            labels=['A', 'B', 'C', 'D'],
            include_lowest=True
        )

        logger.info("성과 순위 매기기 완료")
        return ranked_data

    def process(self) -> pd.DataFrame:
        """전체 데이터 처리 파이프라인 실행"""
        logger.info("Appsflyer 데이터 처리 시작")

        # 1. 데이터 로드
        self.load_csv()

        # 2. 컬럼 정규화 및 데이터 정제
        cleaned_data = self.clean_and_normalize_columns()

        # 3. 광고명에서 캠페인 정보 추출
        campaign_data = self.extract_campaign_info_from_ad_name(cleaned_data)

        # 4. KPI 계산
        kpi_data = self.calculate_kpis(campaign_data)

        # 5. 성과 순위 매기기
        self.processed_data = self.rank_content_performance(kpi_data)

        logger.info(f"데이터 처리 완료: {len(self.processed_data)}개 콘텐츠")
        return self.processed_data

    def get_summary_stats(self) -> Dict:
        """처리 결과 요약 통계"""
        if self.processed_data is None:
            return {}

        # 유효한 D1 Retained CAC 값들만 계산
        valid_d1_cac = self.processed_data[
            (self.processed_data['d1_retained_cac'] != np.inf) &
            (self.processed_data['d1_retained_cac'] > 0)
        ]['d1_retained_cac']

        stats = {
            'total_contents': len(self.processed_data),
            'total_cost': self.processed_data['cost'].sum(),
            'total_installs': self.processed_data['installs'].sum(),
            'total_d1_retained_users': self.processed_data['d1_retained_users'].sum(),
            'avg_d1_retained_cac': valid_d1_cac.mean() if len(valid_d1_cac) > 0 else 0,
            'avg_cpi': self.processed_data['cpi'].mean(),
            'avg_ctr': self.processed_data['ctr'].mean(),
            'media_distribution': self.processed_data['media_type'].value_counts().to_dict(),
            'content_theme_distribution': self.processed_data['content_theme'].value_counts().to_dict(),
            'performance_grade_distribution': self.processed_data['performance_grade'].value_counts().to_dict(),
            'top_performers': self.processed_data.nsmallest(10, 'overall_rank')[
                ['content_name', 'media_type', 'content_theme', 'performance_grade',
                 'd1_retained_cac', 'cpi', 'ctr', 'cost', 'installs', 'd1_retained_users']
            ].to_dict('records')
        }

        return stats

    def export_to_csv(self, output_path: str) -> str:
        """처리된 데이터를 CSV로 내보내기"""
        if self.processed_data is None:
            raise ValueError("처리된 데이터가 없습니다. process() 메서드를 먼저 실행하세요.")

        self.processed_data.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"처리된 데이터 CSV 저장 완료: {output_path}")
        return output_path