"""
Appsflyer Raw Data CSV 처리기
requirements.md 기반 데이터 가공 및 분석
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppsflyerDataProcessor:
    """Appsflyer Raw Data 처리 클래스"""

    # 지원 매체 정의
    SUPPORTED_MEDIA = {
        'tiktok': ['tiktokads_int', 'tiktok', 'bytedanceglobal_int'],
        'meta': ['facebook', 'facebook_int', 'instagram', 'instagram_int']
    }

    # 주요 KPI 컬럼 정의
    KPI_COLUMNS = {
        'cost': 'cost',
        'installs': 'installs',
        'clicks': 'clicks',
        'impressions': 'impressions',
        'd1_retained_users': 'd1_retained_users',
        'campaign_name': 'campaign_name',
        'adset_name': 'adset_name',
        'ad_name': 'ad_name',
        'media_source': 'media_source',
        'platform': 'platform',
        'date': 'date'
    }

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

            # 다양한 인코딩으로 시도
            encodings = ['utf-8', 'cp949', 'euc-kr', 'iso-8859-1']

            for encoding in encodings:
                try:
                    self.raw_data = pd.read_csv(self.csv_file_path, encoding=encoding)
                    logger.info(f"CSV 로드 성공 (인코딩: {encoding})")
                    logger.info(f"데이터 크기: {self.raw_data.shape}")
                    logger.info(f"컬럼 목록: {list(self.raw_data.columns)}")
                    return self.raw_data
                except UnicodeDecodeError:
                    continue

            raise ValueError("지원하는 인코딩으로 CSV를 읽을 수 없습니다.")

        except Exception as e:
            logger.error(f"CSV 파일 로드 실패: {str(e)}")
            raise

    def validate_data(self) -> bool:
        """데이터 유효성 검증"""
        if self.raw_data is None:
            logger.error("데이터가 로드되지 않았습니다.")
            return False

        # 필수 컬럼 확인
        required_columns = ['media_source', 'cost', 'installs']
        missing_columns = [col for col in required_columns if col not in self.raw_data.columns]

        if missing_columns:
            logger.warning(f"누락된 필수 컬럼: {missing_columns}")
            # 컬럼명 매핑 시도
            self._map_column_names()

        return True

    def _map_column_names(self):
        """컬럼명 매핑 (다양한 Appsflyer 컬럼명 대응)"""
        column_mapping = {
            'media source': 'media_source',
            'Media Source': 'media_source',
            'Cost': 'cost',
            'Installs': 'installs',
            'Clicks': 'clicks',
            'Impressions': 'impressions',
            'Campaign': 'campaign_name',
            'Campaign Name': 'campaign_name',
            'Adset': 'adset_name',
            'Adset Name': 'adset_name',
            'Ad': 'ad_name',
            'Ad Name': 'ad_name',
            'Platform': 'platform',
            'Date': 'date',
            'D1 Retained Users': 'd1_retained_users',
            'Retained Day 1': 'd1_retained_users'
        }

        # 컬럼명 변경
        for old_name, new_name in column_mapping.items():
            if old_name in self.raw_data.columns:
                self.raw_data = self.raw_data.rename(columns={old_name: new_name})
                logger.info(f"컬럼명 매핑: {old_name} -> {new_name}")

    def filter_target_media(self) -> pd.DataFrame:
        """타겟 매체 필터링 (TikTok, Meta)"""
        if self.raw_data is None:
            raise ValueError("데이터가 로드되지 않았습니다.")

        # 매체 소스 정규화
        self.raw_data['media_source_normalized'] = self.raw_data['media_source'].str.lower()

        # 타겟 매체 필터링
        target_sources = []
        for media_type, sources in self.SUPPORTED_MEDIA.items():
            target_sources.extend(sources)

        filtered_data = self.raw_data[
            self.raw_data['media_source_normalized'].isin(target_sources)
        ].copy()

        # 매체 타입 추가
        def get_media_type(source):
            source = source.lower()
            for media_type, sources in self.SUPPORTED_MEDIA.items():
                if any(s in source for s in sources):
                    return media_type
            return 'other'

        filtered_data['media_type'] = filtered_data['media_source_normalized'].apply(get_media_type)

        logger.info(f"매체 필터링 완료: {len(self.raw_data)} -> {len(filtered_data)} 행")
        logger.info(f"매체별 분포: {filtered_data['media_type'].value_counts().to_dict()}")

        return filtered_data

    def calculate_kpis(self, data: pd.DataFrame) -> pd.DataFrame:
        """KPI 계산"""
        processed_data = data.copy()

        # 숫자형 컬럼 변환
        numeric_columns = ['cost', 'installs', 'clicks', 'impressions', 'd1_retained_users']
        for col in numeric_columns:
            if col in processed_data.columns:
                processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce').fillna(0)

        # KPI 계산
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

        logger.info("KPI 계산 완료")
        return processed_data

    def create_content_mapping(self, data: pd.DataFrame) -> pd.DataFrame:
        """콘텐츠명 매핑 및 정리"""
        processed_data = data.copy()

        # 콘텐츠명 생성 (Campaign + Adset + Ad 조합)
        processed_data['content_name'] = (
            processed_data.get('campaign_name', '').astype(str) + '_' +
            processed_data.get('adset_name', '').astype(str) + '_' +
            processed_data.get('ad_name', '').astype(str)
        ).str.replace('nan_', '').str.replace('_nan', '').str.strip('_')

        # 플랫폼 정보 정리 (AOS/iOS)
        if 'platform' not in processed_data.columns:
            # 캠페인명이나 다른 필드에서 플랫폼 정보 추출 시도
            processed_data['platform'] = processed_data.get('campaign_name', '').str.extract(
                r'(android|ios|aos)', flags=re.IGNORECASE
            )[0].fillna('unknown')

        # 플랫폼명 표준화
        platform_mapping = {
            'android': 'AOS',
            'aos': 'AOS',
            'ios': 'iOS'
        }

        if 'platform' in processed_data.columns:
            processed_data['platform_normalized'] = processed_data['platform'].str.lower().map(
                platform_mapping
            ).fillna('Unknown')

        logger.info("콘텐츠 매핑 완료")
        return processed_data

    def aggregate_by_content(self, data: pd.DataFrame) -> pd.DataFrame:
        """콘텐츠별 데이터 집계"""

        # 집계할 컬럼 정의
        sum_columns = ['cost', 'installs', 'clicks', 'impressions', 'd1_retained_users']

        # 그룹화 컬럼
        group_columns = ['content_name', 'media_type', 'platform_normalized']

        # 존재하는 컬럼만 필터링
        available_sum_columns = [col for col in sum_columns if col in data.columns]
        available_group_columns = [col for col in group_columns if col in data.columns]

        if not available_sum_columns or not available_group_columns:
            logger.warning("집계에 필요한 컬럼이 부족합니다.")
            return data

        # 집계 수행
        aggregated = data.groupby(available_group_columns)[available_sum_columns].sum().reset_index()

        # 집계된 데이터로 KPI 재계산
        aggregated = self.calculate_kpis(aggregated)

        # 캠페인 기간 추가 (날짜 정보가 있는 경우)
        if 'date' in data.columns:
            date_info = data.groupby(available_group_columns)['date'].agg(['min', 'max']).reset_index()
            date_info = date_info.rename(columns={'min': 'start_date', 'max': 'end_date'})
            aggregated = aggregated.merge(date_info, on=available_group_columns, how='left')

            # 캠페인 기간 계산
            if 'start_date' in aggregated.columns and 'end_date' in aggregated.columns:
                aggregated['campaign_duration'] = pd.to_datetime(aggregated['end_date']) - pd.to_datetime(aggregated['start_date'])
                aggregated['campaign_days'] = aggregated['campaign_duration'].dt.days + 1

        logger.info(f"콘텐츠별 집계 완료: {len(aggregated)}개 콘텐츠")
        return aggregated

    def rank_content_performance(self, data: pd.DataFrame) -> pd.DataFrame:
        """콘텐츠 성과 순위 매기기"""
        ranked_data = data.copy()

        # D1 Retained CAC 기준 순위 (낮을수록 좋음)
        # 무한대 값을 큰 수로 대체
        ranked_data['d1_retained_cac_for_rank'] = ranked_data['d1_retained_cac'].replace([np.inf, -np.inf], 9999999)

        # 매체별, 플랫폼별 순위
        if 'media_type' in ranked_data.columns and 'platform_normalized' in ranked_data.columns:
            ranked_data['rank_d1_cac'] = ranked_data.groupby(['media_type', 'platform_normalized'])['d1_retained_cac_for_rank'].rank(ascending=True)
        else:
            ranked_data['rank_d1_cac'] = ranked_data['d1_retained_cac_for_rank'].rank(ascending=True)

        # 보조 KPI 순위
        if 'cpi' in ranked_data.columns:
            ranked_data['rank_cpi'] = ranked_data['cpi'].rank(ascending=True)
        if 'cpc' in ranked_data.columns:
            ranked_data['rank_cpc'] = ranked_data['cpc'].rank(ascending=True)
        if 'ctr' in ranked_data.columns:
            ranked_data['rank_ctr'] = ranked_data['ctr'].rank(ascending=False)  # 높을수록 좋음

        # 종합 점수 계산 (가중 평균)
        weights = {
            'rank_d1_cac': 0.5,  # 주요 KPI
            'rank_cpi': 0.2,
            'rank_cpc': 0.15,
            'rank_ctr': 0.15
        }

        # 존재하는 순위 컬럼만 사용
        available_ranks = {k: v for k, v in weights.items() if k in ranked_data.columns}

        if available_ranks:
            # 가중 평균 계산
            total_weight = sum(available_ranks.values())
            ranked_data['composite_score'] = sum(
                ranked_data[col] * weight for col, weight in available_ranks.items()
            ) / total_weight

            ranked_data['overall_rank'] = ranked_data['composite_score'].rank(ascending=True)

        # 성과 등급 부여
        if 'overall_rank' in ranked_data.columns:
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

        # 2. 데이터 유효성 검증
        self.validate_data()

        # 3. 타겟 매체 필터링
        filtered_data = self.filter_target_media()

        # 4. 콘텐츠 매핑
        mapped_data = self.create_content_mapping(filtered_data)

        # 5. 콘텐츠별 집계
        aggregated_data = self.aggregate_by_content(mapped_data)

        # 6. KPI 계산 (이미 집계에서 수행됨)

        # 7. 성과 순위 매기기
        self.processed_data = self.rank_content_performance(aggregated_data)

        logger.info(f"데이터 처리 완료: {len(self.processed_data)}개 콘텐츠")
        return self.processed_data

    def get_summary_stats(self) -> Dict:
        """처리 결과 요약 통계"""
        if self.processed_data is None:
            return {}

        stats = {
            'total_contents': len(self.processed_data),
            'total_cost': self.processed_data['cost'].sum(),
            'total_installs': self.processed_data['installs'].sum(),
            'avg_d1_retained_cac': self.processed_data[
                self.processed_data['d1_retained_cac'] != np.inf
            ]['d1_retained_cac'].mean(),
            'media_distribution': self.processed_data['media_type'].value_counts().to_dict(),
            'platform_distribution': self.processed_data.get('platform_normalized', pd.Series()).value_counts().to_dict(),
            'top_performers': self.processed_data.nsmallest(5, 'overall_rank')[
                ['content_name', 'media_type', 'platform_normalized', 'performance_grade', 'd1_retained_cac']
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


# 유틸리티 함수
import re

def create_sample_data(output_path: str = "sample_appsflyer_data.csv"):
    """샘플 Appsflyer 데이터 생성 (테스트용)"""
    sample_data = {
        'Date': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02'] * 10,
        'Media Source': ['tiktokads_int', 'facebook', 'tiktokads_int', 'facebook'] * 10,
        'Campaign Name': [
            'TikTok_Game_AOS_Creative1', 'Meta_Game_iOS_Video2',
            'TikTok_Game_iOS_Banner3', 'Meta_Game_AOS_Story4'
        ] * 10,
        'Adset Name': ['Adset_001', 'Adset_002', 'Adset_003', 'Adset_004'] * 10,
        'Ad Name': ['Ad_A', 'Ad_B', 'Ad_C', 'Ad_D'] * 10,
        'Platform': ['android', 'ios', 'ios', 'android'] * 10,
        'Cost': np.random.uniform(100, 1000, 40),
        'Installs': np.random.randint(50, 500, 40),
        'Clicks': np.random.randint(500, 5000, 40),
        'Impressions': np.random.randint(5000, 50000, 40),
        'D1 Retained Users': np.random.randint(20, 200, 40)
    }

    df = pd.DataFrame(sample_data)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"샘플 데이터 생성 완료: {output_path}")
    return output_path