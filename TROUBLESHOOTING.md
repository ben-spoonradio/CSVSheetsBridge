# 문제 해결 가이드

## 🚨 일반적인 오류와 해결방법

### 1. 401 Unauthorized 오류

**증상:**
```
오류: Request failed: 401 Client Error: Unauthorized
```

**원인:**
- Apps Script 웹 앱 접근 권한 설정이 올바르지 않음
- Google Workspace 계정에서 추가 권한 설정 필요

**해결방법:**
1. Google Apps Script 편집기에서 **배포 > 배포 관리** 클릭
2. 현재 배포의 **편집** 버튼 클릭
3. **액세스 권한**을 다음 중 하나로 변경:
   - `모든 사용자` (권장)
   - `Google 계정이 있는 모든 사용자`
4. **배포** 버튼 클릭
5. **새로운 웹 앱 URL 복사** (URL이 변경될 수 있음)

### 2. JSON 파싱 오류

**증상:**
```
오류: Request failed: Expecting value: line 1 column 1 (char 0)
```

**원인:**
- 서버에서 JSON 대신 HTML 페이지(로그인 페이지 등)를 반환
- Apps Script 코드에 오류가 있음

**해결방법:**
1. **브라우저에서 직접 테스트:**
   ```
   https://your-web-app-url?sheetId=your-sheet-id
   ```
2. 로그인 페이지가 나타나면 권한 설정 문제
3. 오류 페이지가 나타나면 **Apps Script 로그 확인**

### 3. Google Workspace 계정 문제

**증상:**
- URL이 `/a/macros/domain.com/` 형태
- 401 Unauthorized 오류

**해결방법:**
1. **관리자에게 문의**: Google Workspace 정책으로 Apps Script 실행이 제한될 수 있음
2. **개인 Google 계정 사용**: 조직 계정 대신 개인 Gmail 계정으로 테스트
3. **내부 배포로 변경**: 액세스 권한을 조직 내부로만 제한

## 🧪 디버깅 단계

### 1단계: 브라우저에서 직접 테스트

웹 앱 URL을 브라우저 주소창에 입력:
```
https://script.google.com/a/macros/spoonlabs.com/s/AKfycbzXGzfU1YQ7zQSTlHtALBBPvvc9_09zYOT1CWitnLI1PSihbSiok6O3p7dM1kBti-nfEA/exec?sheetId=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

**기대 결과:**
```json
{
  "statusCode": 200,
  "timestamp": "2024-01-01T12:00:00.000Z",
  "success": true,
  "data": [...],
  "rows": 10,
  "columns": 3
}
```

**실제 결과가 다르면:**
- HTML 로그인 페이지 → 권한 문제
- 오류 메시지 → Apps Script 코드 문제
- 빈 페이지 → URL 문제

### 2단계: Apps Script 로그 확인

1. Apps Script 편집기에서 **실행 > 로그 보기**
2. 최근 실행 로그에서 오류 확인
3. 필요시 코드에 `Logger.log()` 추가

### 3단계: 권한 재설정

1. **배포 삭제 후 재생성:**
   - 배포 > 배포 관리 > 기존 배포 삭제
   - 새 배포 생성 (웹 앱)

2. **권한 재승인:**
   - 함수 선택 후 실행
   - 권한 요청 시 모든 권한 승인

## 🔧 임시 해결방법

### curl로 직접 테스트

```bash
# GET 요청 테스트
curl "https://your-web-app-url?sheetId=your-sheet-id"

# POST 요청 테스트
curl -X POST "https://your-web-app-url" \
  -H "Content-Type: application/json" \
  -d '{"sheetId":"your-sheet-id","action":"append","data":[["테스트","데이터"]]}'
```

### 간단한 테스트 스크립트

```python
import requests

url = "YOUR_WEB_APP_URL"
params = {"sheetId": "YOUR_SHEET_ID"}

response = requests.get(url, params=params)
print(f"상태 코드: {response.status_code}")
print(f"응답 헤더: {response.headers}")
print(f"응답 내용: {response.text[:200]}...")
```

## 📋 체크리스트

문제 해결 전 확인사항:

- [ ] Google Apps Script 코드가 올바르게 복사되었는가?
- [ ] 웹 앱으로 배포가 완료되었는가?
- [ ] 액세스 권한이 "모든 사용자"로 설정되었는가?
- [ ] 웹 앱 URL이 올바른가? (.env 파일 확인)
- [ ] 스프레드시트 ID가 올바른가?
- [ ] 해당 스프레드시트에 접근 권한이 있는가?
- [ ] Google Workspace 정책에 제한이 없는가?

## 🆘 추가 도움

위 방법으로 해결되지 않으면:
1. Apps Script 편집기의 실행 로그 스크린샷
2. 브라우저에서 웹 앱 URL 접근 결과 스크린샷
3. Python에서 발생하는 정확한 오류 메시지

이 정보와 함께 문의해 주세요.