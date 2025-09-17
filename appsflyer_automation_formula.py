#!/usr/bin/env python3
"""
수식 기반 Appsflyer 데이터 자동화 스크립트
- 메인 데이터: 실제 값으로 업데이트
- 요약/상위성과/피벗: 수식으로 메인 데이터 참조
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
        logging.FileHandler('appsflyer_automation_formula.log')
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


class AppsflyerFormulaAutomation:
    """수식 기반 Appsflyer 데이터 자동화 메인 클래스"""

    def __init__(self):
        """초기화"""
        self.processor = None
        self.updater = None
        self.setup_logging()

    def setup_logging(self):
        """로깅 설정"""
        # 결과 로그용 별도 로거
        self.result_logger = logging.getLogger('automation_results_formula')
        handler = logging.FileHandler('automation_results_formula.log')
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
            print("\\n.env 파일을 확인하거나 환경변수를 설정하세요.")
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
            print("\\n컬럼 목록:")
            for i, col in enumerate(df.columns, 1):
                print(f"  {i}. {col}")

            print("\\n샘플 데이터 (처음 3행):")
            for i, row in df.head(3).iterrows():
                print(f"  행 {i+2}: {row.iloc[0]} | ${row.iloc[1] if len(row) > 1 else 'N/A'}")

            print()

        except Exception as e:
            print(f"⚠️ CSV 구조 분석 중 오류: {str(e)}")

    def process_data(self, csv_path: str) -> tuple:
        """데이터 처리"""
        logger.info(f"데이터 처리 시작: {csv_path}")
        print(f"📊 수식 기반 Appsflyer 데이터 처리 시작: {csv_path}")

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

    def create_formula_based_updater(self):
        """수식 기반 업데이터 생성"""
        from sheets_client import GoogleSheetsClient

        class FormulaBasedSheetsUpdater(SheetsUpdater):
            """수식 기반 시트 업데이터"""

            def create_summary_formula_data(self, main_sheet_name: str = "메인데이터") -> list:
                """요약 시트용 수식 데이터 생성"""
                return [
                    ['항목', '값'],
                    ['총 콘텐츠 수', f'=COUNTA({main_sheet_name}!A:A)-1'],
                    ['총 비용', f'=SUM({main_sheet_name}!B:B)'],
                    ['총 설치 수', f'=SUM({main_sheet_name}!E:E)'],
                    ['총 D1 유지 유저', f'=SUM({main_sheet_name}!G:G)'],
                    ['평균 D1 Retained CAC', f'=AVERAGE({main_sheet_name}!P:P)'],
                    ['평균 CPI', f'=AVERAGE({main_sheet_name}!N:N)'],
                    ['평균 CTR', f'=AVERAGE({main_sheet_name}!O:O)'],
                    ['업데이트 시간', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                    ['', ''],
                    ['📱 매체별 분포', ''],
                    ['Echo', f'=COUNTIF({main_sheet_name}!H:H,"echo")'],
                    ['TikTok', f'=COUNTIF({main_sheet_name}!H:H,"tiktok")'],
                    ['Innoceans', f'=COUNTIF({main_sheet_name}!H:H,"innoceans")'],
                    ['Spoon', f'=COUNTIF({main_sheet_name}!H:H,"spoon")'],
                    ['기타', f'=COUNTIF({main_sheet_name}!H:H,"unknown")'],
                    ['', ''],
                    ['🏆 성과 등급 분포', ''],
                    ['A등급', f'=COUNTIF({main_sheet_name}!Z:Z,"A")'],
                    ['B등급', f'=COUNTIF({main_sheet_name}!Z:Z,"B")'],
                    ['C등급', f'=COUNTIF({main_sheet_name}!Z:Z,"C")'],
                    ['D등급', f'=COUNTIF({main_sheet_name}!Z:Z,"D")']
                ]

            def create_top_performers_formula_data(self, main_sheet_name: str = "메인데이터") -> list:
                """상위 성과 시트용 수식 데이터 생성"""
                data = [
                    ['순위', '콘텐츠명', '매체', '테마', '등급', 'D1 Retained CAC', '비용', '설치 수', 'D1 유지 유저']
                ]

                # TOP 10 광고를 수식으로 생성
                for i in range(1, 11):
                    row_num = i + 1  # 헤더 제외
                    data.append([
                        str(i),
                        f'=INDEX(SORT({main_sheet_name}!A2:Z1000,{main_sheet_name}!Y2:Y1000,1),{i},1)',  # 콘텐츠명 (overall_rank 기준 정렬)
                        f'=INDEX(SORT({main_sheet_name}!A2:Z1000,{main_sheet_name}!Y2:Y1000,1),{i},8)',  # 매체
                        f'=INDEX(SORT({main_sheet_name}!A2:Z1000,{main_sheet_name}!Y2:Y1000,1),{i},9)',  # 테마
                        f'=INDEX(SORT({main_sheet_name}!A2:Z1000,{main_sheet_name}!Y2:Y1000,1),{i},26)', # 등급
                        f'=INDEX(SORT({main_sheet_name}!A2:Z1000,{main_sheet_name}!Y2:Y1000,1),{i},16)', # D1 CAC
                        f'=INDEX(SORT({main_sheet_name}!A2:Z1000,{main_sheet_name}!Y2:Y1000,1),{i},2)',  # 비용
                        f'=INDEX(SORT({main_sheet_name}!A2:Z1000,{main_sheet_name}!Y2:Y1000,1),{i},5)',  # 설치
                        f'=INDEX(SORT({main_sheet_name}!A2:Z1000,{main_sheet_name}!Y2:Y1000,1),{i},7)'   # D1 유지
                    ])

                return data

            def create_pivot_formula_data(self, main_sheet_name: str = "메인데이터") -> list:
                """피벗 테이블 수식 데이터 생성"""
                return [
                    ['매체별 성과 분석', '', '', ''],
                    ['매체', '평균 D1 CAC', '총 비용', '총 설치 수'],
                    ['Echo',
                     f'=AVERAGEIF({main_sheet_name}!H:H,"echo",{main_sheet_name}!P:P)',
                     f'=SUMIF({main_sheet_name}!H:H,"echo",{main_sheet_name}!B:B)',
                     f'=SUMIF({main_sheet_name}!H:H,"echo",{main_sheet_name}!E:E)'],
                    ['TikTok',
                     f'=AVERAGEIF({main_sheet_name}!H:H,"tiktok",{main_sheet_name}!P:P)',
                     f'=SUMIF({main_sheet_name}!H:H,"tiktok",{main_sheet_name}!B:B)',
                     f'=SUMIF({main_sheet_name}!H:H,"tiktok",{main_sheet_name}!E:E)'],
                    ['Innoceans',
                     f'=AVERAGEIF({main_sheet_name}!H:H,"innoceans",{main_sheet_name}!P:P)',
                     f'=SUMIF({main_sheet_name}!H:H,"innoceans",{main_sheet_name}!B:B)',
                     f'=SUMIF({main_sheet_name}!H:H,"innoceans",{main_sheet_name}!E:E)'],
                    ['Spoon',
                     f'=AVERAGEIF({main_sheet_name}!H:H,"spoon",{main_sheet_name}!P:P)',
                     f'=SUMIF({main_sheet_name}!H:H,"spoon",{main_sheet_name}!B:B)',
                     f'=SUMIF({main_sheet_name}!H:H,"spoon",{main_sheet_name}!E:E)'],
                    ['', '', '', ''],
                    ['테마별 성과 분석', '', '', ''],
                    ['테마', '평균 D1 CAC', '총 비용', '총 설치 수'],
                    ['Participation',
                     f'=AVERAGEIF({main_sheet_name}!I:I,"participation",{main_sheet_name}!P:P)',
                     f'=SUMIF({main_sheet_name}!I:I,"participation",{main_sheet_name}!B:B)',
                     f'=SUMIF({main_sheet_name}!I:I,"participation",{main_sheet_name}!E:E)'],
                    ['Blinddate',
                     f'=AVERAGEIF({main_sheet_name}!I:I,"blinddate",{main_sheet_name}!P:P)',
                     f'=SUMIF({main_sheet_name}!I:I,"blinddate",{main_sheet_name}!B:B)',
                     f'=SUMIF({main_sheet_name}!I:I,"blinddate",{main_sheet_name}!E:E)'],
                    ['Interest',
                     f'=AVERAGEIF({main_sheet_name}!I:I,"interest",{main_sheet_name}!P:P)',
                     f'=SUMIF({main_sheet_name}!I:I,"interest",{main_sheet_name}!B:B)',
                     f'=SUMIF({main_sheet_name}!I:I,"interest",{main_sheet_name}!E:E)'],
                    ['TPO',
                     f'=AVERAGEIF({main_sheet_name}!I:I,"tpo",{main_sheet_name}!P:P)',
                     f'=SUMIF({main_sheet_name}!I:I,"tpo",{main_sheet_name}!B:B)',
                     f'=SUMIF({main_sheet_name}!I:I,"tpo",{main_sheet_name}!E:E)']
                ]

            def update_summary_sheet_with_formulas(self, main_sheet_name: str = "메인데이터", sheet_name: str = None) -> dict:
                """수식 기반 요약 시트 업데이트"""
                if sheet_name is None:
                    sheet_name = self.sheet_config.get('summary_sheet', '요약')

                logger.info(f"수식 기반 요약 시트 업데이트 시작: {sheet_name}")

                # 시트 존재 확인 및 생성
                if not self.ensure_sheet_exists(sheet_name):
                    return {'success': False, 'error': f'시트 {sheet_name} 생성 실패'}

                try:
                    # 수식 데이터 생성
                    formula_data = self.create_summary_formula_data(main_sheet_name)

                    # 시트 덮어쓰기
                    result = self.client.overwrite_sheet(self.sheet_id, formula_data, sheet_name)

                    if result.get('success'):
                        logger.info(f"수식 기반 요약 시트 업데이트 성공: {len(formula_data)}행")
                        return {'success': True, 'rows': len(formula_data)}
                    else:
                        logger.error(f"요약 시트 업데이트 실패: {result.get('error')}")
                        return result

                except Exception as e:
                    logger.error(f"요약 시트 업데이트 중 오류: {str(e)}")
                    return {'success': False, 'error': str(e)}

            def update_top_performers_sheet_with_formulas(self, main_sheet_name: str = "메인데이터", sheet_name: str = None) -> dict:
                """수식 기반 상위 성과 시트 업데이트"""
                if sheet_name is None:
                    sheet_name = self.sheet_config.get('top_performers_sheet', '상위성과')

                logger.info(f"수식 기반 상위 성과 시트 업데이트 시작: {sheet_name}")

                # 시트 존재 확인 및 생성
                if not self.ensure_sheet_exists(sheet_name):
                    return {'success': False, 'error': f'시트 {sheet_name} 생성 실패'}

                try:
                    # 수식 데이터 생성
                    formula_data = self.create_top_performers_formula_data(main_sheet_name)

                    # 시트 덮어쓰기
                    result = self.client.overwrite_sheet(self.sheet_id, formula_data, sheet_name)

                    if result.get('success'):
                        logger.info(f"수식 기반 상위 성과 시트 업데이트 성공: {len(formula_data)}행")
                        return {'success': True, 'rows': len(formula_data)}
                    else:
                        logger.error(f"상위 성과 시트 업데이트 실패: {result.get('error')}")
                        return result

                except Exception as e:
                    logger.error(f"상위 성과 시트 업데이트 중 오류: {str(e)}")
                    return {'success': False, 'error': str(e)}

            def update_pivot_sheet_with_formulas(self, main_sheet_name: str = "메인데이터", sheet_name: str = None) -> dict:
                """수식 기반 피벗 테이블 시트 업데이트"""
                if sheet_name is None:
                    sheet_name = self.sheet_config.get('pivot_table_sheet', '피벗테이블')

                logger.info(f"수식 기반 피벗 테이블 시트 업데이트 시작: {sheet_name}")

                # 시트 존재 확인 및 생성
                if not self.ensure_sheet_exists(sheet_name):
                    return {'success': False, 'error': f'시트 {sheet_name} 생성 실패'}

                try:
                    # 수식 데이터 생성
                    formula_data = self.create_pivot_formula_data(main_sheet_name)

                    # 시트 덮어쓰기
                    result = self.client.overwrite_sheet(self.sheet_id, formula_data, sheet_name)

                    if result.get('success'):
                        logger.info(f"수식 기반 피벗 테이블 업데이트 성공: {len(formula_data)}행")
                        return {'success': True, 'rows': len(formula_data)}
                    else:
                        logger.error(f"피벗 테이블 업데이트 실패: {result.get('error')}")
                        return result

                except Exception as e:
                    logger.error(f"피벗 테이블 업데이트 중 오류: {str(e)}")
                    return {'success': False, 'error': str(e)}

            def update_all_sheets_with_formulas(self, df, stats, main_sheet_name: str = "메인데이터") -> dict:
                """모든 시트를 수식 기반으로 일괄 업데이트"""
                logger.info("수식 기반 전체 시트 업데이트 시작")

                results = {}

                # 1. 메인 데이터 업데이트 (실제 값)
                results['main_data'] = self.update_main_data_sheet(df, main_sheet_name)

                # 2. 요약 시트 업데이트 (수식)
                results['summary'] = self.update_summary_sheet_with_formulas(main_sheet_name)

                # 3. 상위 성과 시트 업데이트 (수식)
                results['top_performers'] = self.update_top_performers_sheet_with_formulas(main_sheet_name)

                # 4. 피벗 테이블 업데이트 (수식)
                results['pivot_table'] = self.update_pivot_sheet_with_formulas(main_sheet_name)

                # 전체 성공 여부 판단
                all_success = all(result.get('success', False) for result in results.values())

                logger.info(f"수식 기반 전체 시트 업데이트 완료 - 성공: {all_success}")

                return {
                    'overall_success': all_success,
                    'individual_results': results,
                    'summary': {
                        'successful_sheets': sum(1 for r in results.values() if r.get('success')),
                        'total_sheets': len(results),
                        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }

        return FormulaBasedSheetsUpdater()

    def update_sheets(self, processed_data, stats, backup=False):
        """Google Sheets 업데이트 (수식 기반)"""
        logger.info("수식 기반 Google Sheets 업데이트 시작")
        print("📤 수식 기반 Google Sheets 업데이트 시작...")

        try:
            # 수식 기반 Sheets 업데이터 초기화
            self.updater = self.create_formula_based_updater()

            # 백업 수행 (선택적)
            if backup:
                print("   💾 현재 데이터 백업 중...")
                backup_result = self.updater.backup_current_data()
                if backup_result.get('success'):
                    print(f"   ✅ 백업 완료: {backup_result['backup_sheet']}")
                else:
                    print(f"   ⚠️ 백업 실패: {backup_result.get('error', '알 수 없는 오류')}")

            # 메인 시트명 결정
            main_sheet_name = self.updater.sheet_config.get('main_data_sheet', '메인데이터')

            # 모든 시트 업데이트 (수식 기반)
            print("   🔄 시트 업데이트 중...")
            print(f"   📊 메인 데이터: 실제 값으로 업데이트")
            print(f"   📈 요약/성과/피벗: 수식으로 '{main_sheet_name}' 참조")

            update_results = self.updater.update_all_sheets_with_formulas(
                processed_data, stats, main_sheet_name
            )

            # 결과 출력
            if update_results['overall_success']:
                print("   ✅ 모든 시트 업데이트 성공!")
                success_count = update_results['summary']['successful_sheets']
                total_count = update_results['summary']['total_sheets']
                print(f"   📊 업데이트된 시트: {success_count}/{total_count}")
                print(f"   🔗 메인 데이터: 실제 값")
                print(f"   🔗 기타 시트: '{main_sheet_name}' 참조 수식")
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
            self.result_logger.info(f"Formula-based sheets update completed - Success: {update_results['overall_success']}")

            return update_results

        except Exception as e:
            logger.error(f"Google Sheets 업데이트 중 오류: {str(e)}")
            print(f"❌ Google Sheets 업데이트 실패: {str(e)}")
            raise

    def print_summary_stats(self, stats):
        """요약 통계 출력"""
        print("\\n📈 처리 결과 요약")
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
            print(f"\\n📱 매체별 분포:")
            for media, count in media_dist.items():
                print(f"  {media}: {count:,}개")

        # 성과 등급 분포
        grade_dist = stats.get('performance_grade_distribution', {})
        if grade_dist:
            print(f"\\n🏆 성과 등급 분포:")
            for grade, count in grade_dist.items():
                print(f"  {grade}등급: {count:,}개")

        print(f"\\n📊 업데이트 방식:")
        print(f"  - 메인 데이터: 실제 처리된 값으로 업데이트")
        print(f"  - 요약 시트: 수식으로 메인 데이터 참조")
        print(f"  - 상위 성과: 수식으로 자동 정렬 및 추출")
        print(f"  - 피벗 테이블: 수식으로 동적 집계")

    def run(self, csv_path: str, backup: bool = False, export_csv: bool = False):
        """메인 실행 함수"""
        start_time = datetime.now()

        print("🚀 수식 기반 Appsflyer 데이터 자동화 시작")
        print("=" * 70)

        try:
            # 1. 환경 검증
            if not self.validate_environment():
                return False

            # 2. 데이터 처리
            processed_data, stats = self.process_data(csv_path)

            # 3. Google Sheets 업데이트 (수식 기반)
            update_results = self.update_sheets(processed_data, stats, backup)

            # 4. CSV 내보내기 (선택적)
            if export_csv:
                output_path = f"processed_data_formula_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                self.processor.export_to_csv(output_path)
                print(f"📄 처리된 데이터 CSV 저장: {output_path}")

            # 5. 결과 요약 출력
            self.print_summary_stats(stats)

            # 실행 시간 계산
            end_time = datetime.now()
            duration = end_time - start_time

            print(f"\\n⏱️ 실행 시간: {duration.total_seconds():.1f}초")
            print(f"🔗 Google Sheets: https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEETS_SHEET_ID')}")

            print(f"\\n🎉 수식 기반 자동화 완료!")
            print("📊 생성된 시트들:")
            print("   - 메인데이터: 실제 처리된 데이터 (값)")
            print("   - 요약: 메인데이터 참조 수식")
            print("   - 상위성과: 자동 정렬 수식")
            print("   - 피벗테이블: 동적 집계 수식")
            print("\\n✨ 메인 데이터가 변경되면 다른 시트들이 자동으로 업데이트됩니다!")

            # 최종 결과 로깅
            self.result_logger.info(
                f"Formula automation completed successfully - Duration: {duration.total_seconds():.1f}s, "
                f"Contents: {stats.get('total_contents', 0)}, "
                f"Sheets updated: {update_results['overall_success']}"
            )

            return True

        except Exception as e:
            logger.error(f"자동화 실행 중 오류: {str(e)}")
            print(f"\\n❌ 자동화 실행 실패: {str(e)}")

            # 실행 시간 계산
            end_time = datetime.now()
            duration = end_time - start_time
            print(f"⏱️ 실행 시간: {duration.total_seconds():.1f}초")

            # 오류 로깅
            self.result_logger.error(f"Formula automation failed - Error: {str(e)}, Duration: {duration.total_seconds():.1f}s")

            return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='수식 기반 Appsflyer 데이터 자동화 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python appsflyer_automation_formula.py --csv Data_dua.csv
  python appsflyer_automation_formula.py --csv Data_dua.csv --backup --export

특징:
  - 메인 데이터: 실제 값으로 업데이트
  - 요약/성과/피벗: 수식으로 메인 데이터 참조
  - 메인 데이터 변경 시 다른 시트들 자동 업데이트
        """
    )

    parser.add_argument(
        '--csv',
        type=str,
        help='처리할 Data_dua.csv 파일 경로',
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
    automation = AppsflyerFormulaAutomation()
    success = automation.run(
        csv_path=args.csv,
        backup=args.backup,
        export_csv=args.export
    )

    # 종료 코드 설정
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()