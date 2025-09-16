# 보안 가이드

## 🔒 보안 수준별 설정

### Level 1: 기본 보안 (현재 상태)
**위험도: 높음** 🔴

**현재 설정:**
```
액세스 권한: 모든 사용자
데이터: 공개
인증: 없음
```

**위험사항:**
- 누구나 웹 앱 URL로 접근 가능
- 스프레드시트 데이터 유출 위험
- 무제한 API 호출로 인한 할당량 소진
- 데이터 변조/삭제 가능

### Level 2: 조직 제한
**위험도: 중간** 🟡

**설정 방법:**
1. Google Apps Script → 배포 → 배포 관리
2. 액세스 권한: `Google 계정이 있는 사용자만`
3. 또는 `조직 내 사용자만` (Google Workspace)

**장점:**
- Google 로그인 필수
- 익명 접근 차단
- 사용자 추적 가능

**단점:**
- 여전히 많은 사용자 접근 가능

### Level 3: 특정 사용자만
**위험도: 낮음** 🟢

**설정 방법:**
1. 액세스 권한: `특정 사용자만`
2. 승인된 사용자 이메일 추가
3. 주기적 접근 권한 검토

**장점:**
- 최소 권한 원칙
- 명확한 접근 제어
- 감사 추적 가능

## 🔐 고급 보안 방법

### 1. API 키 인증 추가

**Apps Script 코드 수정:**
```javascript
function doGet(e) {
  // API 키 검증
  var apiKey = e.parameter.apiKey;
  var validApiKey = PropertiesService.getScriptProperties().getProperty('API_KEY');

  if (!apiKey || apiKey !== validApiKey) {
    return createResponse({error: 'Invalid API key'}, 401);
  }

  // 기존 로직 계속...
}
```

**Python에서 사용:**
```python
client.read_sheet(sheet_id, sheet_name, api_key='your-secret-key')
```

### 2. IP 주소 제한

```javascript
function doGet(e) {
  // 허용된 IP 주소 목록
  var allowedIPs = ['192.168.1.100', '203.0.113.1'];
  var clientIP = getClientIP();

  if (allowedIPs.indexOf(clientIP) === -1) {
    return createResponse({error: 'Access denied from this IP'}, 403);
  }

  // 기존 로직...
}

function getClientIP() {
  // Google Apps Script에서 클라이언트 IP 가져오기는 제한적
  // 대안: 헤더에 IP 정보 포함하도록 요청
  return null;
}
```

### 3. 사용량 제한 (Rate Limiting)

```javascript
function doGet(e) {
  var cache = CacheService.getScriptCache();
  var clientId = e.parameter.clientId || 'anonymous';
  var rateLimitKey = 'rate_limit_' + clientId;

  var requestCount = cache.get(rateLimitKey) || 0;
  if (requestCount > 100) { // 시간당 100회 제한
    return createResponse({error: 'Rate limit exceeded'}, 429);
  }

  cache.put(rateLimitKey, parseInt(requestCount) + 1, 3600); // 1시간

  // 기존 로직...
}
```

### 4. 데이터 암호화

```python
import os
from cryptography.fernet import Fernet

class SecureGoogleSheetsClient(GoogleSheetsClient):
    def __init__(self, web_app_url, encryption_key=None):
        super().__init__(web_app_url)
        self.fernet = Fernet(encryption_key or self._generate_key())

    def _generate_key(self):
        return Fernet.generate_key()

    def _encrypt_data(self, data):
        return self.fernet.encrypt(str(data).encode()).decode()

    def _decrypt_data(self, encrypted_data):
        return self.fernet.decrypt(encrypted_data.encode()).decode()
```

## 📊 권장 보안 설정

### 개발/테스트 환경
```
액세스 권한: Google 계정이 있는 사용자만
API 키: 선택사항
IP 제한: 없음
사용량 제한: 낮음 (시간당 1000회)
```

### 프로덕션 환경
```
액세스 권한: 특정 사용자만
API 키: 필수
IP 제한: 사무실/서버 IP만
사용량 제한: 엄격 (시간당 100회)
데이터 암호화: 권장
로깅: 모든 접근 기록
```

### 민감한 데이터 환경
```
액세스 권한: 특정 사용자 1-2명
API 키: 복잡한 키 + 정기 교체
IP 제한: 특정 서버만
사용량 제한: 매우 엄격 (시간당 50회)
데이터 암호화: 필수
감사 로그: 모든 작업 기록
정기 보안 검토: 월 1회
```

## 🚨 긴급 보안 조치

### 의심스러운 접근 발견 시
1. **즉시 배포 중지**: 배포 관리 → 배포 삭제
2. **새 스크립트 ID**: 새 배포로 URL 변경
3. **로그 확인**: Apps Script 실행 로그 검토
4. **데이터 검증**: 스프레드시트 내용 확인

### 정기 보안 점검
- [ ] 접근 로그 검토 (월 1회)
- [ ] API 키 교체 (분기 1회)
- [ ] 권한 설정 검토 (월 1회)
- [ ] 의존성 업데이트 (월 1회)

## 💡 보안 모범 사례

### 1. 환경변수 보안
```bash
# .env 파일을 절대 Git에 커밋하지 마세요
echo ".env" >> .gitignore

# 복잡한 값 사용
GOOGLE_SHEETS_WEB_APP_URL=https://...매우긴스크립트ID.../exec
GOOGLE_SHEETS_API_KEY=매우복잡한랜덤문자열
```

### 2. 코드 보안
```python
# 하드코딩 금지
❌ sheet_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

# 환경변수 사용
✅ sheet_id = os.getenv('GOOGLE_SHEETS_SHEET_ID')
```

### 3. 네트워크 보안
```python
# HTTPS 강제
if not web_app_url.startswith('https://'):
    raise ValueError("HTTPS required for security")

# SSL 검증
response = requests.get(url, verify=True)
```

### 4. 오류 처리
```python
# 민감한 정보 노출 방지
try:
    result = client.read_sheet(sheet_id)
except Exception as e:
    # 사용자에게는 일반적 메시지
    print("데이터 접근 중 오류가 발생했습니다.")
    # 로그에는 상세 정보
    logger.error(f"Sheet access failed: {str(e)}")
```

## 📞 보안 문의

보안 관련 질문이나 의심스러운 활동 발견 시:
1. 즉시 배포 중지
2. 로그 수집
3. 보안팀 또는 개발팀에 보고