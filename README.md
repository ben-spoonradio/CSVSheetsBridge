# 🚀 CSVSheetsBridge

Appsflyer CSV 데이터를 자동으로 처리하고 Google Sheets에 업데이트하는 완전 자동화 시스템

[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## ✨ 주요 기능

- 🔄 **완전 자동화**: CSV 파일을 읽어 KPI를 계산하고 Google Sheets에 자동 업데이트
- 🎯 **스마트 분석**: D1 Retained CAC, CPI, CTR 등 핵심 성과 지표 자동 계산
- 📊 **성과 등급**: A~D 등급 자동 부여로 광고 성과 한눈에 파악
- 🔍 **시트 자동 감지**: 기존 Google Sheets 시트명을 자동으로 찾아 활용
- ⚡ **수식 기반 업데이트**: 메인 데이터만 실제 값, 나머지는 수식으로 실시간 연동
- 🛡️ **OAuth 불필요**: Google Apps Script를 통한 간단한 인증 시스템

## 📋 처리 가능한 데이터

### 입력 형식 (Data_dua.csv)
```
Ad, Cost (sum), Impressions (sum), Clicks (sum), Installs (sum), Unique Users - etc_sign_up (sum), Retention Day 01 (sum)
```

### 출력 결과

#### 표준 방식
- **메인 데이터**: 전체 광고 데이터 + 계산된 KPI (실제 값)
- **요약 통계**: 매체별/테마별 분포 및 평균 지표 (실제 값)
- **상위 성과**: Top 10 광고 랭킹 (실제 값)
- **피벗 분석**: 매체별 교차 분석 테이블 (실제 값)

#### 수식 기반 방식 ⭐ 추천
- **메인 데이터**: 전체 광고 데이터 + 계산된 KPI (실제 값)
- **요약 통계**: 수식으로 메인 데이터 참조 (자동 계산)
- **상위 성과**: 수식으로 자동 정렬 TOP 10 (자동 업데이트)
- **피벗 분석**: 수식으로 동적 집계 (실시간 반영)

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/ben-spoonradio/CSVSheetsBridge.git
cd CSVSheetsBridge
```

### 2. Google Apps Script 설정

#### 2-1. Google Apps Script 프로젝트 생성
1. [Google Apps Script](https://script.google.com) 접속
2. Google 계정으로 로그인
3. "새 프로젝트" 클릭
4. 프로젝트 이름 변경 (예: "SheetsAPI")

#### 2-2. Apps Script 코드 복사
`apps_script/Code.gs` 파일의 내용을 Google Apps Script 편집기에 복사합니다.

#### 2-3. 웹 앱으로 배포
1. Apps Script 편집기에서 "배포" > "새 배포" 클릭
2. 유형 선택: "웹 앱"
3. 설정:
   - 설명: "Sheets API Web App"
   - 실행 계정: "나"
   - 액세스 권한: "모든 사용자" (또는 "Google 계정이 있는 모든 사용자")
4. "배포" 클릭
5. 웹 앱 URL 복사 (예: `https://script.google.com/macros/s/SCRIPT_ID/exec`)

### 3. 의존성 설치
```bash
pip install pandas numpy python-dotenv requests
```

### 4. 환경변수 설정

`.env` 파일 생성:
```env
# Google Apps Script 웹 앱 URL
GOOGLE_SHEETS_WEB_APP_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec

# Google Sheets ID (URL에서 /d/ 다음 부분)
GOOGLE_SHEETS_SHEET_ID=YOUR_SPREADSHEET_ID

# 접근 토큰 (선택사항)
GOOGLE_SHEETS_ACCESS_TOKEN=YourSecureToken
```

### 5. 실행

#### 표준 방식 (모든 데이터를 실제 값으로 업데이트)
```bash
# 기본 실행
python appsflyer_automation_real.py --csv Data_dua.csv

# 백업과 함께 실행
python appsflyer_automation_real.py --csv Data_dua.csv --backup

# 처리된 데이터 CSV로도 저장
python appsflyer_automation_real.py --csv Data_dua.csv --backup --export
```

#### 수식 기반 방식 (메인 데이터만 실제 값, 나머지는 수식으로 참조) ⭐ 추천
```bash
# 수식 기반 실행
python appsflyer_automation_formula.py --csv Data_dua.csv

# 백업과 함께 실행
python appsflyer_automation_formula.py --csv Data_dua.csv --backup

# 처리된 데이터 CSV로도 저장
python appsflyer_automation_formula.py --csv Data_dua.csv --backup --export
```

## 📊 사용 예시

### 실행 결과 예시
```
🚀 실제 Appsflyer 데이터 자동화 시작
======================================================================
📊 CSV 파일 구조 분석
파일: Data_dua.csv
총 행 수: 27 행
컬럼 수: 7 개

   🔄 데이터 로딩 및 정제 중...
   ✅ 데이터 처리 완료
📤 Google Sheets 업데이트 시작...
   ✅ 모든 시트 업데이트 성공!
   📊 업데이트된 시트: 4/4

📈 처리 결과 요약
======================================================================
총 광고 수: 27개
총 비용: $12,345.67
총 설치 수: 1,234개
평균 D1 Retained CAC: $45.67

📱 매체별 분포:
  echo: 16개
  innoceans: 6개
  tiktok: 4개
  spoon: 1개

🏆 성과 등급 분포:
  A등급: 4개
  B등급: 7개
  C등급: 6개
  D등급: 10개

⏱️ 실행 시간: 7.2초
🎉 Data_dua.csv 자동화 완료!
```

## ⚙️ 명령행 옵션

### 공통 옵션 (두 스크립트 모두 지원)
| 옵션 | 설명 | 예시 |
|------|------|------|
| `--csv` | 처리할 CSV 파일 경로 | `--csv Data_dua.csv` |
| `--backup` | 업데이트 전 현재 데이터 백업 | `--backup` |
| `--export` | 처리된 데이터를 CSV로 내보내기 | `--export` |
| `--verbose` | 상세 로그 출력 | `--verbose` |

### 스크립트별 특징
| 스크립트 | 특징 | 장점 | 단점 |
|----------|------|------|------|
| `appsflyer_automation_real.py` | 모든 시트에 실제 값 입력 | 안정적, 독립적 | 데이터 중복, 수동 업데이트 |
| `appsflyer_automation_formula.py` | 수식 기반 자동 연동 | 실시간 동기화, 효율적 | Google Sheets 의존적 |

## 📈 KPI 계산 방식

### 핵심 지표
- **D1 Retained CAC**: `비용 ÷ D1 유지 유저 수` (주요 성과 지표)
- **CPI**: `비용 ÷ 설치 수`
- **CPC**: `비용 ÷ 클릭 수`
- **CTR**: `(클릭 수 ÷ 노출 수) × 100`

### 성과 등급 기준
- **A등급** (상위 20%): 최우수 성과
- **B등급** (상위 21-50%): 우수 성과
- **C등급** (상위 51-80%): 보통 성과
- **D등급** (하위 20%): 개선 필요

## ⚡ 수식 기반 방식의 장점

### 🔄 실시간 자동 업데이트
- 메인 데이터가 변경되면 **즉시** 모든 시트가 자동 업데이트
- 수동으로 다시 실행할 필요 없음

### 📊 동적 분석
```excel
# 요약 시트 수식 예시
총 콘텐츠 수: =COUNTA(메인데이터!A:A)-1
총 비용: =SUM(메인데이터!B:B)
Echo 매체 수: =COUNTIF(메인데이터!H:H,"echo")

# 상위성과 시트 수식 예시 (자동 정렬)
1위 광고: =INDEX(SORT(메인데이터!A2:Z1000,메인데이터!Y2:Y1000,1),1,1)
1위 CAC: =INDEX(SORT(메인데이터!A2:Z1000,메인데이터!Y2:Y1000,1),1,16)
```

### 🚀 효율성
- **네트워크 트래픽 감소**: 메인 데이터만 전송
- **처리 시간 단축**: 계산 로직이 Google Sheets에서 실행
- **유지보수 용이**: 비즈니스 로직 변경 시 수식만 수정

## 📁 프로젝트 구조

```
CSVSheetsBridge/
├── 📄 appsflyer_automation_real.py        # 표준 방식 실행 스크립트
├── 📄 appsflyer_automation_formula.py     # 수식 기반 실행 스크립트 ⭐
├── 📄 requirements.md                      # 프로젝트 요구사항 명세
├── 📄 PROJECT_SUMMARY.md                  # 프로젝트 완료 보고서
├── 📁 src/
│   ├── 📄 appsflyer_processor_adapted.py      # 데이터 처리기
│   ├── 📄 sheets_updater.py                   # Google Sheets 업데이터
│   ├── 📄 sheets_detector.py                  # 시트 자동 감지
│   └── 📄 sheets_client.py                    # Google Sheets 클라이언트
├── 📁 apps_script/
│   └── 📄 Code.gs                             # Google Apps Script 코드
├── 📁 examples/
│   ├── 📄 basic_usage.py                      # 기본 사용법 예시
│   └── 📄 csv_integration.py                  # CSV 통합 예시
└── 📁 config/
    └── 📄 settings.py                         # 설정 관리
```

## 🔧 문제 해결

### 자주 발생하는 문제

**Q: "환경변수가 설정되지 않았습니다" 오류**
```bash
A: .env 파일이 프로젝트 루트에 있는지 확인하고,
   GOOGLE_SHEETS_WEB_APP_URL과 GOOGLE_SHEETS_SHEET_ID가 올바른지 확인하세요.
```

**Q: "시트를 찾을 수 없습니다" 오류**
```bash
A: Google Sheets에 최소 하나의 시트('시트1' 또는 'Sheet1')가 있는지 확인하세요.
   시스템이 자동으로 기존 시트를 감지해서 활용합니다.
```

**Q: "CSV 파일을 찾을 수 없습니다" 오류**
```bash
A: Data_dua.csv 파일이 프로젝트 디렉토리에 있는지 확인하거나,
   --csv 옵션으로 정확한 파일 경로를 지정하세요.
```

### 로그 확인
- **`automation_results_real.log`**: 실행 결과 요약
- **`appsflyer_automation_real.log`**: 상세 처리 과정

## 🛡️ 보안

- 모든 민감한 정보는 `.env` 파일로 관리
- `.gitignore`를 통해 민감 데이터 보호
- Google Apps Script를 통한 안전한 Sheets 접근

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

- 이슈 리포트: [GitHub Issues](https://github.com/ben-spoonradio/CSVSheetsBridge/issues)
- 기능 요청: [GitHub Discussions](https://github.com/ben-spoonradio/CSVSheetsBridge/discussions)

---

<div align="center">

**🎉 Appsflyer 데이터 분석을 자동화하고 더 나은 성과를 만들어보세요! 🎉**

</div>
