#!/usr/bin/env python3
"""
Appsflyer 데이터 자동화 스크립트
requirements.md 기반 완전 자동화 파이프라인

사용법:
    python appsflyer_automation.py --csv Data_dua.csv
    python appsflyer_automation.py --csv Data_dua.csv --backup
    python appsflyer_automation.py --sample  # 샘플 데이터로 테스트
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
        logging.FileHandler('appsflyer_automation.log')
    ]
)
logger = logging.getLogger(__name__)

# 모듈 import
try:
    from appsflyer_processor import AppsflyerDataProcessor, create_sample_data
    from sheets_updater import SheetsUpdater
    from dotenv import load_dotenv
except ImportError as e:
    logger.error(f"필수 모듈 import 실패: {e}")
    print("❌ 필수 모듈을 찾을 수 없습니다. src/ 디렉토리와 파일들이 올바른지 확인하세요.")
    sys.exit(1)

# 환경변수 로드
load_dotenv()


class AppsflyerAutomation:
    """Appsflyer 데이터 자동화 메인 클래스"""

    def __init__(self):
        """초기화"""
        self.processor = None
        self.updater = None
        self.setup_logging()

    def setup_logging(self):
        """로깅 설정"""
        # 결과 로그용 별도 로거
        self.result_logger = logging.getLogger('automation_results')
        handler = logging.FileHandler('automation_results.log')
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

    def create_sample_data_if_needed(self, csv_path: str) -> str:
        """필요시 샘플 데이터 생성"""
        if csv_path == '--sample':
            logger.info("샘플 데이터 생성 중...")
            sample_path = 'sample_appsflyer_data.csv'
            create_sample_data(sample_path)
            print(f"📝 샘플 데이터 생성 완료: {sample_path}")
            return sample_path
        return csv_path

    def process_data(self, csv_path: str) -> tuple:
        """데이터 처리"""
        logger.info(f"데이터 처리 시작: {csv_path}")
        print(f"📊 Appsflyer 데이터 처리 시작: {csv_path}")

        try:
            # CSV 파일 존재 확인
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")

            # 데이터 처리기 초기화
            self.processor = AppsflyerDataProcessor(csv_path)

            # 데이터 처리 실행
            print("   🔄 데이터 로딩 중...")
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
                    print(f"     {status} {sheet_type}: {result.get('error', 'Success')}")

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
        print("=" * 50)

        print(f"총 콘텐츠 수: {stats.get('total_contents', 0):,}개")
        print(f"총 비용: ${stats.get('total_cost', 0):,.2f}")
        print(f"총 설치 수: {stats.get('total_installs', 0):,}개")
        avg_cac = stats.get('avg_d1_retained_cac', 0)
        if avg_cac and avg_cac != float('inf'):
            print(f"평균 D1 Retained CAC: ${avg_cac:.2f}")

        # 매체별 분포
        media_dist = stats.get('media_distribution', {})
        if media_dist:
            print("\n📱 매체별 분포:")
            for media, count in media_dist.items():
                print(f"  {media}: {count:,}개")

        # 플랫폼별 분포
        platform_dist = stats.get('platform_distribution', {})
        if platform_dist:
            print("\n📱 플랫폼별 분포:")
            for platform, count in platform_dist.items():
                print(f"  {platform}: {count:,}개")

        # 상위 성과자
        top_performers = stats.get('top_performers', [])
        if top_performers:
            print("\n🏆 상위 성과 콘텐츠 (Top 3):")
            for i, performer in enumerate(top_performers[:3], 1):
                cac = performer.get('d1_retained_cac', 0)
                cac_str = f"${cac:.2f}" if cac != float('inf') else "N/A"
                print(f"  {i}. {performer.get('content_name', 'N/A')[:50]}... "
                      f"({performer.get('media_type', 'N/A')}/{performer.get('platform_normalized', 'N/A')}) "
                      f"- D1 CAC: {cac_str}")

    def run(self, csv_path: str, backup: bool = False, export_csv: bool = False):
        """메인 실행 함수"""
        start_time = datetime.now()

        print("🚀 Appsflyer 데이터 자동화 시작")
        print("=" * 60)

        try:
            # 1. 환경 검증
            if not self.validate_environment():
                return False

            # 2. 샘플 데이터 생성 (필요시)
            csv_path = self.create_sample_data_if_needed(csv_path)

            # 3. 데이터 처리
            processed_data, stats = self.process_data(csv_path)

            # 4. Google Sheets 업데이트
            update_results = self.update_sheets(processed_data, stats, backup)

            # 5. CSV 내보내기 (선택적)
            if export_csv:
                output_path = f"processed_appsflyer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                self.processor.export_to_csv(output_path)
                print(f"📄 처리된 데이터 CSV 저장: {output_path}")

            # 6. 결과 요약 출력
            self.print_summary_stats(stats)

            # 실행 시간 계산
            end_time = datetime.now()
            duration = end_time - start_time

            print(f"\n⏱️ 실행 시간: {duration.total_seconds():.1f}초")
            print(f"🔗 Google Sheets: https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEETS_SHEET_ID')}")

            print("\n🎉 자동화 완료!")

            # 최종 결과 로깅
            self.result_logger.info(
                f"Automation completed successfully - Duration: {duration.total_seconds():.1f}s, "
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
            self.result_logger.error(f"Automation failed - Error: {str(e)}, Duration: {duration.total_seconds():.1f}s")

            return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='Appsflyer 데이터 자동화 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python appsflyer_automation.py --csv Data_dua.csv
  python appsflyer_automation.py --csv Data_dua.csv --backup --export
  python appsflyer_automation.py --sample
        """
    )

    parser.add_argument(
        '--csv',
        type=str,
        help='Appsflyer CSV 파일 경로 (또는 --sample로 샘플 데이터 사용)',
        default='Data_dua.csv'
    )

    parser.add_argument(
        '--sample',
        action='store_true',
        help='샘플 데이터로 테스트 실행'
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

    # CSV 경로 설정
    csv_path = '--sample' if args.sample else args.csv

    # 자동화 실행
    automation = AppsflyerAutomation()
    success = automation.run(
        csv_path=csv_path,
        backup=args.backup,
        export_csv=args.export
    )

    # 종료 코드 설정
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()