# Appsflyer 데이터 자동화 시스템

requirements.md 기반으로 구축된 **Appsflyer Raw Data 자동 처리 및 Google Sheets 업데이트** 시스템입니다.

## 🎯 주요 기능

### ✅ 완전 자동화된 기능들
- **CSV 데이터 자동 처리**: Appsflyer Raw Data 로드 및 정제
- **매체별 필터링**: TikTok (AOS/iOS), Meta (AOS/iOS) 자동 분류
- **KPI 자동 계산**: D1 Retained CAC, CPC, CPI, CTR
- **콘텐츠 자동 매핑**: Campaign + Adset + Ad 조합으로 콘텐츠명 생성
- **성과 순위 매기기**: 주요 KPI 기반 자동 랭킹
- **Google Sheets 자동 업데이트**: 4개 시트 동시 업데이트
- **피벗 테이블 자동 생성**: 매체 × 플랫폼 분석 테이블

### 📊 분석 결과물
1. **메인데이터**: 전체 처리된 데이터
2. **요약**: 통계 요약 및 분포 현황
3. **상위성과**: Top 10 콘텐츠 랭킹
4. **피벗테이블**: 매체별/플랫폼별 교차 분석

## 🚀 사용법

### 1. 기본 실행
```bash
# Appsflyer CSV 파일로 실행
python appsflyer_automation.py --csv Data_dua.csv

# 샘플 데이터로 테스트
python appsflyer_automation.py --sample
```

### 2. 고급 옵션
```bash
# 백업 포함 실행
python appsflyer_automation.py --csv Data_dua.csv --backup

# 처리된 데이터 CSV 내보내기 포함
python appsflyer_automation.py --csv Data_dua.csv --export

# 모든 옵션 포함
python appsflyer_automation.py --csv Data_dua.csv --backup --export --verbose
```

### 3. 명령어 옵션
- `--csv PATH`: Appsflyer CSV 파일 경로
- `--sample`: 샘플 데이터로 테스트 실행
- `--backup`: 업데이트 전 현재 데이터 백업
- `--export`: 처리된 데이터를 CSV로 내보내기
- `--verbose`: 상세 로그 출력

## 📋 사전 준비

### 1. 환경변수 설정 (.env 파일)
```env
GOOGLE_SHEETS_WEB_APP_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
GOOGLE_SHEETS_SHEET_ID=YOUR_SHEET_ID
```

### 2. 필수 패키지 설치
```bash
pip install pandas numpy python-dotenv requests
```

### 3. Appsflyer CSV 파일 형식
필수 컬럼:
- `Media Source`: 매체 정보
- `Cost`: 비용
- `Installs`: 설치 수
- `Clicks`: 클릭 수
- `Impressions`: 노출 수
- `D1 Retained Users`: D1 유지 유저 수
- `Campaign Name`, `Adset Name`, `Ad Name`: 캠페인 정보

## 🔍 처리 과정

### 1. 데이터 로딩 및 검증
```
📊 Appsflyer 데이터 처리 시작: Data_dua.csv
   🔄 데이터 로딩 중...
   ✅ 데이터 처리 완료
```

### 2. 매체 필터링
- **TikTok**: tiktokads_int, tiktok, bytedanceglobal_int
- **Meta**: facebook, facebook_int, instagram, instagram_int

### 3. KPI 자동 계산
```python
# 주요 KPI
D1 Retained CAC = Cost / D1 Retained Users  # 핵심 지표
CPC = Cost / Clicks
CPI = Cost / Installs
CTR = (Clicks / Impressions) × 100
D1 Retention Rate = (D1 Retained Users / Installs) × 100
```

### 4. 성과 등급 분류
- **A등급**: 상위 20%
- **B등급**: 21-50%
- **C등급**: 51-80%
- **D등급**: 하위 20%

### 5. Google Sheets 업데이트
```
📤 Google Sheets 업데이트 시작...
   🔄 시트 업데이트 중...
   ✅ 모든 시트 업데이트 성공!
   📊 업데이트된 시트: 4/4
```

## 📈 결과 예시

### 처리 결과 요약
```
📈 처리 결과 요약
==================================================
총 콘텐츠 수: 145개
총 비용: $12,450.30
총 설치 수: 8,920개
평균 D1 Retained CAC: $3.45

📱 매체별 분포:
  tiktok: 78개
  meta: 67개

📱 플랫폼별 분포:
  AOS: 89개
  iOS: 56개

🏆 상위 성과 콘텐츠 (Top 3):
  1. TikTok_Game_AOS_Creative1_Adset_001_Ad_A... (tiktok/AOS) - D1 CAC: $1.23
  2. Meta_Game_iOS_Video2_Adset_002_Ad_B... (meta/iOS) - D1 CAC: $1.45
  3. TikTok_Game_iOS_Banner3_Adset_003_Ad_C... (tiktok/iOS) - D1 CAC: $1.67
```

## 🔧 시스템 구조

```
appsflyer_automation.py          # 메인 실행 스크립트
├── src/
│   ├── appsflyer_processor.py   # 데이터 처리 로직
│   ├── sheets_updater.py        # Google Sheets 업데이트
│   └── sheets_client.py         # Google Sheets API 클라이언트
├── apps_script/
│   └── Code.gs                  # Google Apps Script 코드
└── requirements.md              # 요구사항 정의
```

## 📊 생성되는 시트들

### 1. 메인데이터 시트
| content_name | media_type | platform | cost | installs | d1_retained_cac | performance_grade |
|--------------|------------|----------|------|----------|-----------------|-------------------|
| Campaign_Adset_Ad | tiktok | AOS | $500.00 | 200 | $2.50 | B |

### 2. 요약 시트
| 항목 | 값 |
|------|-----|
| 총 콘텐츠 수 | 145 |
| 총 비용 | $12,450.30 |
| 평균 D1 Retained CAC | $3.45 |

### 3. 상위성과 시트
| 순위 | 콘텐츠명 | 매체 | 플랫폼 | 등급 | D1 Retained CAC |
|------|----------|------|--------|------|-----------------|
| 1 | Best_Campaign... | tiktok | AOS | A | $1.23 |

### 4. 피벗테이블 시트
| 매체/플랫폼 | AOS | iOS |
|-------------|-----|-----|
| tiktok | $2.30 | $2.45 |
| meta | $2.80 | $2.65 |

## 🔍 로그 및 모니터링

### 생성되는 로그 파일
- `appsflyer_automation.log`: 상세 실행 로그
- `automation_results.log`: 결과 요약 로그

### 실시간 모니터링
```bash
# 실행 로그 실시간 확인
tail -f appsflyer_automation.log

# 결과 로그 확인
tail automation_results.log
```

## ⚠️ 문제 해결

### 일반적인 오류

#### "CSV 파일을 찾을 수 없습니다"
```bash
# 파일 경로 확인
python appsflyer_automation.py --csv /full/path/to/Data_dua.csv
```

#### "환경변수가 설정되지 않았습니다"
```bash
# .env 파일 확인
cat .env

# 환경변수 직접 설정
export GOOGLE_SHEETS_WEB_APP_URL="your_url_here"
```

#### "시트 업데이트 실패"
1. Google Apps Script 배포 상태 확인
2. 웹 앱 URL 유효성 확인
3. 시트 접근 권한 확인

### 디버깅 모드
```bash
# 상세 로그로 실행
python appsflyer_automation.py --csv Data_dua.csv --verbose
```

## 🚀 확장 가능성

### 향후 개선 방향 (requirements.md 기반)
1. **LLM 연동**: 콘텐츠 카피/비주얼 정성 분석
2. **실시간 API 연동**: Appsflyer API 직접 연결
3. **알림 시스템**: Slack, 이메일 알림
4. **대시보드**: 실시간 성과 모니터링
5. **예측 모델**: AI 기반 성과 예측

### 커스터마이징
```python
# 새로운 KPI 추가
def calculate_custom_kpi(self, data):
    data['custom_kpi'] = data['revenue'] / data['cost']
    return data

# 새로운 매체 추가
SUPPORTED_MEDIA = {
    'tiktok': [...],
    'meta': [...],
    'google': ['google_ads', 'google_uac']  # 추가
}
```

## 📞 지원

문제 발생 시:
1. 로그 파일 확인 (`appsflyer_automation.log`)
2. 환경변수 설정 검증
3. CSV 파일 형식 확인
4. Google Sheets 접근 권한 확인

---

**이 시스템으로 수동 작업을 완전히 자동화하여 시간을 절약하고 일관된 분석 결과를 얻을 수 있습니다!** 🎉