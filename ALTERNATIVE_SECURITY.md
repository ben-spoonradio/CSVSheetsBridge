# 대안적 보안 방법

## 🔐 Google Workspace 제약 우회 방법

### 문제: "특정 사용자만" 설정 시 OAuth 필요
Google Workspace 환경에서 "특정 사용자만" 설정하면 익명 HTTP 요청이 차단됩니다.

## 🛠️ 해결 방법 옵션

### Option 1: 개인 Google 계정 사용 (가장 간단)

**장점:**
- 설정이 매우 간단
- OAuth 불필요
- "모든 사용자" 설정도 상대적으로 안전

**단점:**
- 회사 데이터를 개인 계정에서 관리
- 조직 정책 적용 불가

**실행 방법:**
1. 개인 Gmail 계정으로 새 Apps Script 프로젝트 생성
2. 동일한 코드 복사
3. "모든 사용자" 또는 "Google 계정 사용자만" 설정
4. 개인적 사용이므로 보안 위험 최소화

### Option 2: IP 기반 접근 제어

```javascript
// Apps Script에서 IP 제한
function doGet(e) {
  // 허용된 IP 주소 목록 (사무실, 집, 서버 등)
  var allowedIPs = [
    '203.0.113.1',    // 사무실 IP
    '192.168.1.100',  // 집 IP
    '10.0.0.50'       // 서버 IP
  ];

  // 클라이언트 IP 확인 (제한적)
  var clientIP = getClientIP();
  if (allowedIPs.indexOf(clientIP) === -1) {
    return createResponse({error: 'Access denied from this IP'}, 403);
  }

  // 기존 로직...
}
```

### Option 3: 시간 기반 접근 제어

```javascript
function doGet(e) {
  var now = new Date();
  var hour = now.getHours();

  // 업무 시간에만 접근 허용 (9-18시)
  if (hour < 9 || hour > 18) {
    return createResponse({error: 'Access denied outside business hours'}, 403);
  }

  // 주말 제한
  var day = now.getDay();
  if (day === 0 || day === 6) {
    return createResponse({error: 'Access denied on weekends'}, 403);
  }

  // 기존 로직...
}
```

### Option 4: 간단한 토큰 인증

```javascript
function doGet(e) {
  var token = e.parameter.token;
  var validTokens = [
    'your-secret-token-123',
    'another-token-456'
  ];

  if (!token || validTokens.indexOf(token) === -1) {
    return createResponse({error: 'Invalid token'}, 401);
  }

  // 기존 로직...
}
```

**Python에서 사용:**
```python
# .env 파일에 추가
GOOGLE_SHEETS_ACCESS_TOKEN=your-secret-token-123

# 사용법
params = {
    'sheetId': sheet_id,
    'sheetName': sheet_name,
    'token': os.getenv('GOOGLE_SHEETS_ACCESS_TOKEN')
}
response = requests.get(webapp_url, params=params)
```

### Option 5: 조직 내부 제한 + 간단한 인증

**Apps Script 설정:**
```
액세스 권한: "spoonlabs.com 조직 내 사용자만"
추가 인증: 간단한 토큰
```

**장점:**
- Google 로그인 + 추가 토큰으로 이중 보안
- 조직 외부 접근 완전 차단
- 구현 복잡도 낮음

## 💡 권장 방법

### 개발/테스트: Option 1 (개인 계정)
```
위험도: 낮음
복잡도: 매우 낮음
시간: 5분
```

### 소규모 팀: Option 4 (토큰 인증)
```
위험도: 낮음
복잡도: 낮음
시간: 15분
```

### 중간 규모: Option 5 (조직 + 토큰)
```
위험도: 매우 낮음
복잡도: 중간
시간: 30분
```

### 대규모/민감한 데이터: 정식 OAuth
```
위험도: 최소
복잡도: 높음
시간: 2-3시간
```

## 🚀 즉시 적용 가능한 방법

### 1. 토큰 인증 추가 (5분 소요)

**Apps Script 수정:**
```javascript
function doGet(e) {
  // 토큰 확인
  if (e.parameter.token !== 'YOUR_SECRET_TOKEN_HERE') {
    return createResponse({error: 'Unauthorized'}, 401);
  }

  // 기존 코드 그대로...
}
```

**Python 수정:**
```python
# .env에 추가
GOOGLE_SHEETS_ACCESS_TOKEN=YOUR_SECRET_TOKEN_HERE

# 클라이언트 수정
params['token'] = os.getenv('GOOGLE_SHEETS_ACCESS_TOKEN')
```

### 2. 사용량 제한 추가 (10분 소요)

```javascript
function checkRateLimit() {
  var cache = CacheService.getScriptCache();
  var count = parseInt(cache.get('request_count')) || 0;

  if (count > 100) { // 시간당 100회 제한
    return false;
  }

  cache.put('request_count', (count + 1).toString(), 3600);
  return true;
}
```

이 중에서 어떤 방법을 사용하시겠습니까?