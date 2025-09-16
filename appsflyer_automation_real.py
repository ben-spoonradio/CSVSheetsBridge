#!/usr/bin/env python3
"""
실제 Data_dua.csv 형식에 맞춘 Appsflyer 데이터 자동화 스크립트
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# src 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('appsflyer_automation_real.log')
    ]
)
logger = logging.getLogger(__name__)

# 모듈 import
try:
    from appsflyer_processor_adapted import AppsflyerDataProcessorAdapted
    from sheets_updater import SheetsUpdater
    from dotenv import load_dotenv
except ImportError as e:
    logger.error(f"필수 모듈 import 실패: {e}")
    print("❌ 필수 모듈을 찾을 수 없습니다. src/ 디렉토리와 파일들이 올바른지 확인하세요.")
    sys.exit(1)

# 환경변수 로드
load_dotenv()


class AppsflyerRealDataAutomation:
    """실제 Data_dua.csv 형식용 Appsflyer 데이터 자동화 메인 클래스"""

    def __init__(self):
        """초기화"""
        self.processor = None
        self.updater = None
        self.setup_logging()

    def setup_logging(self):
        """로깅 설정"""
        # 결과 로그용 별도 로거
        self.result_logger = logging.getLogger('automation_results_real')
        handler = logging.FileHandler('automation_results_real.log')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        self.result_logger.addHandler(handler)
        self.result_logger.setLevel(logging.INFO)

    def validate_environment(self):
        """환경 설정 검증"""
        logger.info("환경 설정 검증 시작")

        required_env_vars = [
            'GOOGLE_SHEETS_WEB_APP_URL',
            'GOOGLE_SHEETS_SHEET_ID'
        ]

        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            logger.error(f"누락된 환경변수: {missing_vars}")
            print("❌ 다음 환경변수가 필요합니다:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n.env 파일을 확인하거나 환경변수를 설정하세요.")
            return False

        logger.info("환경 설정 검증 완료")
        return True

    def analyze_csv_structure(self, csv_path: str):
        """CSV 구조 분석 및 출력"""
        try:
            import pandas as pd
            df = pd.read_csv(csv_path, encoding='utf-8-sig', nrows=5)

            print("📊 CSV 파일 구조 분석")
            print("=" * 50)
            print(f"파일: {csv_path}")
            print(f"총 행 수: {len(pd.read_csv(csv_path, encoding='utf-8-sig'))} 행")
            print(f"컬럼 수: {len(df.columns)} 개")
            print("\n컬럼 목록:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")

            print("\n샘플 데이터 (처음 3행):")
            for i, row in df.head(3).iterrows():
                print(f"  행 {i+2}: {row.iloc[0]} | ${row.iloc[1] if len(row) > 1 else 'N/A'}")

            print()

        except Exception as e:
            print(f"⚠️ CSV 구조 분석 중 오류: {str(e)}")

    def process_data(self, csv_path: str) -> tuple:
        """데이터 처리"""
        logger.info(f"데이터 처리 시작: {csv_path}")
        print(f"📊 실제 Appsflyer 데이터 처리 시작: {csv_path}")

        try:
            # CSV 파일 존재 확인
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")

            # CSV 구조 분석
            self.analyze_csv_structure(csv_path)

            # 데이터 처리기 초기화
            self.processor = AppsflyerDataProcessorAdapted(csv_path)

            # 데이터 처리 실행
            print("   🔄 데이터 로딩 및 정제 중...")
            processed_data = self.processor.process()

            print("   ✅ 데이터 처리 완료")

            # 요약 통계 생성
            stats = self.processor.get_summary_stats()

            # 결과 로깅
            self.result_logger.info(f"Data processing completed - {stats.get('total_contents', 0)} contents processed")

            return processed_data, stats

        except Exception as e:
            logger.error(f"데이터 처리 중 오류: {str(e)}")
            print(f"❌ 데이터 처리 실패: {str(e)}")
            raise

    def update_sheets(self, processed_data, stats, backup=False):
        """Google Sheets 업데이트"""
        logger.info("Google Sheets 업데이트 시작")
        print("📤 Google Sheets 업데이트 시작...")

        try:
            # Sheets 업데이터 초기화
            self.updater = SheetsUpdater()

            # 백업 수행 (선택적)
            if backup:
                print("   💾 현재 데이터 백업 중...")
                backup_result = self.updater.backup_current_data()
                if backup_result.get('success'):
                    print(f"   ✅ 백업 완료: {backup_result['backup_sheet']}")
                else:
                    print(f"   ⚠️ 백업 실패: {backup_result.get('error', '알 수 없는 오류')}")

            # 모든 시트 업데이트
            print("   🔄 시트 업데이트 중...")
            update_results = self.updater.update_all_sheets(processed_data, stats)

            # 결과 출력
            if update_results['overall_success']:
                print("   ✅ 모든 시트 업데이트 성공!")
                success_count = update_results['summary']['successful_sheets']
                total_count = update_results['summary']['total_sheets']
                print(f"   📊 업데이트된 시트: {success_count}/{total_count}")
            else:
                print("   ⚠️ 일부 시트 업데이트 실패")
                # 개별 결과 출력
                for sheet_type, result in update_results['individual_results'].items():
                    status = "✅" if result.get('success') else "❌"
                    error_msg = result.get('error', 'Success')
                    if len(str(error_msg)) > 50:
                        error_msg = str(error_msg)[:47] + "..."
                    print(f"     {status} {sheet_type}: {error_msg}")

            # 결과 로깅
            self.result_logger.info(f"Sheets update completed - Success: {update_results['overall_success']}")

            return update_results

        except Exception as e:
            logger.error(f"Google Sheets 업데이트 중 오류: {str(e)}")
            print(f"❌ Google Sheets 업데이트 실패: {str(e)}")
            raise

    def print_summary_stats(self, stats):
        """요약 통계 출력"""
        print("\n📈 처리 결과 요약")
        print("=" * 60)

        print(f"총 광고 수: {stats.get('total_contents', 0):,}개")
        print(f"총 비용: ${stats.get('total_cost', 0):,.2f}")
        print(f"총 설치 수: {stats.get('total_installs', 0):,}개")
        print(f"총 D1 유지 유저: {stats.get('total_d1_retained_users', 0):,}명")

        # KPI 평균
        avg_cac = stats.get('avg_d1_retained_cac', 0)
        if avg_cac and avg_cac != float('inf'):
            print(f"평균 D1 Retained CAC: ${avg_cac:.2f}")

        avg_cpi = stats.get('avg_cpi', 0)
        if avg_cpi:
            print(f"평균 CPI: ${avg_cpi:.2f}")

        avg_ctr = stats.get('avg_ctr', 0)
        if avg_ctr:
            print(f"평균 CTR: {avg_ctr:.2f}%")

        # 매체별 분포
        media_dist = stats.get('media_distribution', {})
        if media_dist:
            print(f"\n📱 매체별 분포:")
            for media, count in media_dist.items():
                print(f"  {media}: {count:,}개")

        # 콘텐츠 테마별 분포
        theme_dist = stats.get('content_theme_distribution', {})
        if theme_dist:
            print(f"\n🎭 콘텐츠 테마별 분포:")
            for theme, count in theme_dist.items():
                print(f"  {theme}: {count:,}개")

        # 성과 등급 분포
        grade_dist = stats.get('performance_grade_distribution', {})
        if grade_dist:
            print(f"\n🏆 성과 등급 분포:")
            for grade, count in grade_dist.items():
                print(f"  {grade}등급: {count:,}개")

        # 상위 성과자
        top_performers = stats.get('top_performers', [])
        if top_performers:
            print(f"\n🥇 상위 성과 광고 (Top 5):")
            for i, performer in enumerate(top_performers[:5], 1):
                cac = performer.get('d1_retained_cac', 0)
                cac_str = f"${cac:.2f}" if cac != float('inf') else "N/A"
                cost = performer.get('cost', 0)
                installs = performer.get('installs', 0)
                d1_users = performer.get('d1_retained_users', 0)

                # 광고명 축약 (너무 길면)
                ad_name = performer.get('content_name', 'N/A')
                if len(ad_name) > 60:
                    ad_name = ad_name[:57] + "..."

                print(f"  {i}. {ad_name}")
                print(f"     매체: {performer.get('media_type', 'N/A')} | 테마: {performer.get('content_theme', 'N/A')} | 등급: {performer.get('performance_grade', 'N/A')}")
                print(f"     비용: ${cost:,.2f} | 설치: {installs:,}개 | D1유지: {d1_users:,}명 | D1 CAC: {cac_str}")
                print()

    def run(self, csv_path: str, backup: bool = False, export_csv: bool = False):
        """메인 실행 함수"""
        start_time = datetime.now()

        print("🚀 실제 Appsflyer 데이터 자동화 시작")
        print("=" * 70)

        try:
            # 1. 환경 검증
            if not self.validate_environment():
                return False

            # 2. 데이터 처리
            processed_data, stats = self.process_data(csv_path)

            # 3. Google Sheets 업데이트
            update_results = self.update_sheets(processed_data, stats, backup)

            # 4. CSV 내보내기 (선택적)
            if export_csv:
                output_path = f"processed_data_dua_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                self.processor.export_to_csv(output_path)
                print(f"📄 처리된 데이터 CSV 저장: {output_path}")

            # 5. 결과 요약 출력
            self.print_summary_stats(stats)

            # 실행 시간 계산
            end_time = datetime.now()
            duration = end_time - start_time

            print(f"\n⏱️ 실행 시간: {duration.total_seconds():.1f}초")
            print(f"🔗 Google Sheets: https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEETS_SHEET_ID')}")

            print(f"\n🎉 Data_dua.csv 자동화 완료!")
            print("📊 생성된 시트들:")
            print("   - 메인데이터: 전체 광고 데이터 및 KPI")
            print("   - 요약: 통계 요약 및 분포")
            print("   - 상위성과: Top 10 광고 랭킹")
            print("   - 피벗테이블: 매체별 성과 교차 분석")

            # 최종 결과 로깅
            self.result_logger.info(
                f"Real data automation completed successfully - Duration: {duration.total_seconds():.1f}s, "
                f"Contents: {stats.get('total_contents', 0)}, "
                f"Sheets updated: {update_results['overall_success']}"
            )

            return True

        except Exception as e:
            logger.error(f"자동화 실행 중 오류: {str(e)}")
            print(f"\n❌ 자동화 실행 실패: {str(e)}")

            # 실행 시간 계산
            end_time = datetime.now()
            duration = end_time - start_time
            print(f"⏱️ 실행 시간: {duration.total_seconds():.1f}초")

            # 오류 로깅
            self.result_logger.error(f"Real automation failed - Error: {str(e)}, Duration: {duration.total_seconds():.1f}s")

            return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='실제 Data_dua.csv 형식용 Appsflyer 데이터 자동화 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python appsflyer_automation_real.py --csv Data_dua.csv
  python appsflyer_automation_real.py --csv Data_dua.csv --backup --export
        """
    )

    parser.add_argument(
        '--csv',
        type=str,
        help='실제 Data_dua.csv 파일 경로',
        default='Data_dua.csv'
    )

    parser.add_argument(
        '--backup',
        action='store_true',
        help='업데이트 전 현재 데이터 백업'
    )

    parser.add_argument(
        '--export',
        action='store_true',
        help='처리된 데이터를 CSV로 내보내기'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='상세 로그 출력'
    )

    args = parser.parse_args()

    # 로깅 레벨 설정
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 자동화 실행
    automation = AppsflyerRealDataAutomation()
    success = automation.run(
        csv_path=args.csv,
        backup=args.backup,
        export_csv=args.export
    )

    # 종료 코드 설정
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()