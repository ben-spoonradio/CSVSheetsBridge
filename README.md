# CSV Sheets Bridge

Google Apps Script를 사용하여 Python과 Google Sheets를 연동하는 라이브러리입니다. 복잡한 OAuth 인증이나 Google Cloud Console 설정 없이 간단하게 Google Sheets를 조작할 수 있습니다.

## ✨ 특징

- **간단한 설정**: OAuth나 서비스 계정 없이 Google Apps Script만으로 설정
- **안정적인 연결**: Google 인프라에서 실행되는 웹 앱을 통한 안정적인 API 호출
- **재시도 기능**: 네트워크 오류 시 자동 재시도 지원
- **CSV 연동**: CSV 파일과 Google Sheets 간의 양방향 동기화
- **무료**: Google Apps Script는 무료 서비스

## 🚀 빠른 시작

### 1. Google Apps Script 설정

#### 1-1. Google Apps Script 프로젝트 생성
1. [Google Apps Script](https://script.google.com) 접속
2. Google 계정으로 로그인
3. "새 프로젝트" 클릭
4. 프로젝트 이름 변경 (예: "SheetsAPI")

#### 1-2. Apps Script 코드 복사
`apps_script/Code.gs` 파일의 내용을 Google Apps Script 편집기에 복사합니다.

#### 1-3. 웹 앱으로 배포
1. Apps Script 편집기에서 "배포" > "새 배포" 클릭
2. 유형 선택: "웹 앱"
3. 설정:
   - 설명: "Sheets API Web App"
   - 실행 계정: "나"
   - 액세스 권한: "모든 사용자" (또는 "Google 계정이 있는 모든 사용자")
4. "배포" 클릭
5. 웹 앱 URL 복사 (예: `https://script.google.com/macros/s/SCRIPT_ID/exec`)

### 2. Python 환경 설정

#### 2-1. 패키지 설치
```bash
pip install -r requirements.txt
```

#### 2-2. 환경변수 설정
```bash
# .env 파일 생성
cp .env.template .env
```

`.env` 파일에 실제 값을 입력:
```env
GOOGLE_SHEETS_WEB_APP_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec
GOOGLE_SHEETS_SHEET_ID=YOUR_SHEET_ID
```

## 📖 사용법

### 기본 사용

```python
from src.sheets_client import GoogleSheetsClient

# 클라이언트 생성
client = GoogleSheetsClient('https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec')

# 데이터 읽기
result = client.read_sheet('YOUR_SHEET_ID')
print(result['data'])

# 행 추가
new_data = [
    ['이름', '나이', '도시'],
    ['김철수', 25, '서울']
]
client.append_rows('YOUR_SHEET_ID', new_data)

# 특정 범위 업데이트
update_data = [['새로운 값', '업데이트됨']]
client.update_range('YOUR_SHEET_ID', 'A1:B1', update_data)

# 시트 전체 덮어쓰기
overwrite_data = [
    ['제품명', '가격'],
    ['노트북', 1000000],
    ['마우스', 30000]
]
client.overwrite_sheet('YOUR_SHEET_ID', overwrite_data)
```

### 재시도 기능이 포함된 안정적인 클라이언트

```python
from src.sheets_client import RobustGoogleSheetsClient

# 재시도 기능이 포함된 클라이언트
robust_client = RobustGoogleSheetsClient('YOUR_WEB_APP_URL')

# 네트워크 오류 시 자동으로 3번까지 재시도
result = robust_client.read_sheet('YOUR_SHEET_ID')
```

### CSV 파일과 연동

```python
from examples.csv_integration import csv_to_sheets, sheets_to_csv

# CSV 파일을 Google Sheets로 업로드
csv_to_sheets('data.csv', 'YOUR_WEB_APP_URL', 'YOUR_SHEET_ID')

# Google Sheets를 CSV 파일로 다운로드
sheets_to_csv('YOUR_WEB_APP_URL', 'YOUR_SHEET_ID', 'output.csv')
```

## 📁 프로젝트 구조

```
CSVSheetsBridge/
├── apps_script/
│   └── Code.gs                 # Google Apps Script 코드
├── src/
│   └── sheets_client.py        # Python 클라이언트 라이브러리
├── examples/
│   ├── basic_usage.py         # 기본 사용 예제
│   └── csv_integration.py     # CSV 연동 예제
├── config/
│   └── settings.py            # 설정 관리
├── .env.template              # 환경변수 템플릿
├── requirements.txt           # Python 의존성
├── setup.py                   # 패키지 설정
└── README.md                  # 이 파일
```

## 🔧 API 참조

### GoogleSheetsClient

#### `read_sheet(sheet_id, sheet_name='Sheet1')`
스프레드시트 데이터를 읽습니다.

**매개변수:**
- `sheet_id` (str): 스프레드시트 ID
- `sheet_name` (str): 시트 이름 (기본값: 'Sheet1')

**반환값:**
```python
{
    'success': True,
    'data': [...],  # 2차원 리스트
    'rows': 10,
    'columns': 3
}
```

#### `append_rows(sheet_id, data, sheet_name='Sheet1')`
시트에 새 행을 추가합니다.

#### `update_range(sheet_id, range_str, data, sheet_name='Sheet1')`
특정 범위의 데이터를 업데이트합니다.

#### `overwrite_sheet(sheet_id, data, sheet_name='Sheet1')`
시트 전체 내용을 새 데이터로 덮어씁니다.

#### `clear_sheet(sheet_id, range_str=None, sheet_name='Sheet1')`
시트의 내용을 지웁니다.

### 유틸리티 함수

#### `extract_sheet_id_from_url(url)`
Google Sheets URL에서 스프레드시트 ID를 추출합니다.

```python
url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit"
sheet_id = extract_sheet_id_from_url(url)
# 결과: "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
```

## 🔍 예제 실행

### 기본 사용 예제
```bash
python examples/basic_usage.py
```

### CSV 연동 예제
```bash
python examples/csv_integration.py
```

## ❗ 주의사항

### 장점
- **인증 불필요**: OAuth나 서비스 계정 설정 없음
- **간단한 설정**: Google Apps Script만 작성하면 됨
- **안정적**: Google 인프라에서 실행
- **무료**: Google Apps Script는 무료 서비스

### 한계
- **실행 시간 제한**: Apps Script는 6분 실행 제한
- **API 호출 제한**: 일일 호출 횟수 제한 있음
- **네트워크 지연**: HTTP 요청을 통한 간접 접근

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 있습니다. 자세한 내용은 LICENSE 파일을 참조하세요.

## 🆘 문제 해결

### 일반적인 오류

#### "sheetId parameter required"
- 스프레드시트 ID가 올바르게 설정되었는지 확인
- URL에서 ID를 정확히 추출했는지 확인

#### "Worksheet not found"
- 시트 이름이 정확한지 확인 (대소문자 구분)
- 해당 시트가 스프레드시트에 존재하는지 확인

#### "Request failed"
- 웹 앱 URL이 올바른지 확인
- Apps Script 배포 설정에서 액세스 권한 확인
- 네트워크 연결 상태 확인

### 디버깅

Apps Script에서 로그 확인:
1. Google Apps Script 편집기에서 "실행" > "로그 보기"
2. `Logger.log()` 함수를 사용하여 디버그 정보 출력

## 📞 지원

문제가 있거나 질문이 있으시면 GitHub Issues를 통해 문의해 주세요.