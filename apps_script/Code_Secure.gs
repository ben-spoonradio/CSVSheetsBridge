// 보안이 강화된 Google Apps Script 코드

function doGet(e) {
  // API 키 검증
  if (!validateApiKey(e.parameter.apiKey)) {
    return createResponse({error: 'Unauthorized access'}, 401);
  }

  // 사용량 제한 체크
  if (!checkRateLimit(e.parameter.clientId)) {
    return createResponse({error: 'Rate limit exceeded'}, 429);
  }

  try {
    var sheetId = e.parameter.sheetId;
    var sheetName = e.parameter.sheetName || 'Sheet1';

    if (!sheetId) {
      return createResponse({error: 'sheetId parameter required'}, 400);
    }

    var sheet = SpreadsheetApp.openById(sheetId);
    var worksheet = sheet.getSheetByName(sheetName);

    if (!worksheet) {
      return createResponse({error: 'Worksheet not found'}, 404);
    }

    var data = worksheet.getDataRange().getValues();

    // 접근 로그 기록
    logAccess('READ', e.parameter.clientId, sheetId, sheetName);

    return createResponse({
      success: true,
      data: data,
      rows: data.length,
      columns: data[0] ? data[0].length : 0
    });

  } catch (error) {
    logError('GET_ERROR', error.toString(), e.parameter.clientId);
    return createResponse({error: 'Internal server error'}, 500);
  }
}

function doPost(e) {
  try {
    var requestData = JSON.parse(e.postData.contents);

    // API 키 검증
    if (!validateApiKey(requestData.apiKey)) {
      return createResponse({error: 'Unauthorized access'}, 401);
    }

    // 사용량 제한 체크
    if (!checkRateLimit(requestData.clientId)) {
      return createResponse({error: 'Rate limit exceeded'}, 429);
    }

    var sheetId = requestData.sheetId;
    var sheetName = requestData.sheetName || 'Sheet1';
    var action = requestData.action;
    var data = requestData.data;
    var range = requestData.range;

    if (!sheetId) {
      return createResponse({error: 'sheetId required'}, 400);
    }

    var sheet = SpreadsheetApp.openById(sheetId);
    var worksheet = sheet.getSheetByName(sheetName);

    if (!worksheet) {
      return createResponse({error: 'Worksheet not found'}, 404);
    }

    var result = {};

    switch (action) {
      case 'append':
        if (data && Array.isArray(data)) {
          data.forEach(function(row) {
            worksheet.appendRow(row);
          });
          result = {success: true, action: 'appended', rows: data.length};
        } else {
          return createResponse({error: 'data array required for append'}, 400);
        }
        break;

      case 'update':
        if (range && data) {
          worksheet.getRange(range).setValues(data);
          result = {success: true, action: 'updated', range: range};
        } else {
          return createResponse({error: 'range and data required for update'}, 400);
        }
        break;

      case 'overwrite':
        worksheet.clear();
        if (data && data.length > 0) {
          worksheet.getRange(1, 1, data.length, data[0].length).setValues(data);
          result = {success: true, action: 'overwritten', rows: data.length};
        }
        break;

      default:
        return createResponse({error: 'Invalid action'}, 400);
    }

    // 접근 로그 기록
    logAccess(action.toUpperCase(), requestData.clientId, sheetId, sheetName);

    return createResponse(result);

  } catch (error) {
    logError('POST_ERROR', error.toString());
    return createResponse({error: 'Internal server error'}, 500);
  }
}

function validateApiKey(providedKey) {
  if (!providedKey) {
    return false;
  }

  // Script Properties에서 유효한 API 키 가져오기
  var validKey = PropertiesService.getScriptProperties().getProperty('API_KEY');
  return providedKey === validKey;
}

function checkRateLimit(clientId) {
  if (!clientId) {
    clientId = 'anonymous';
  }

  var cache = CacheService.getScriptCache();
  var rateLimitKey = 'rate_limit_' + clientId;
  var hourlyLimit = 100; // 시간당 100회 제한

  var requestCount = parseInt(cache.get(rateLimitKey)) || 0;

  if (requestCount >= hourlyLimit) {
    return false;
  }

  // 카운터 증가 (1시간 TTL)
  cache.put(rateLimitKey, (requestCount + 1).toString(), 3600);
  return true;
}

function logAccess(action, clientId, sheetId, sheetName) {
  var logSheet = getLogSheet();
  if (logSheet) {
    logSheet.appendRow([
      new Date(),
      action,
      clientId || 'unknown',
      sheetId,
      sheetName || 'unknown',
      Session.getActiveUser().getEmail()
    ]);
  }
}

function logError(type, message, clientId) {
  var logSheet = getLogSheet();
  if (logSheet) {
    logSheet.appendRow([
      new Date(),
      'ERROR_' + type,
      clientId || 'unknown',
      '',
      message.substring(0, 200), // 오류 메시지 200자 제한
      Session.getActiveUser().getEmail()
    ]);
  }
}

function getLogSheet() {
  try {
    var logSheetId = PropertiesService.getScriptProperties().getProperty('LOG_SHEET_ID');
    if (logSheetId) {
      var logSpreadsheet = SpreadsheetApp.openById(logSheetId);
      return logSpreadsheet.getSheetByName('AccessLog') || logSpreadsheet.getActiveSheet();
    }
  } catch (error) {
    // 로그 시트 접근 실패 시 무시 (메인 기능에 영향 없음)
  }
  return null;
}

function createResponse(data, statusCode) {
  statusCode = statusCode || 200;

  return ContentService
    .createTextOutput(JSON.stringify({
      statusCode: statusCode,
      timestamp: new Date().toISOString(),
      ...data
    }))
    .setMimeType(ContentService.MimeType.JSON);
}

function setupSecurity() {
  // 초기 보안 설정 함수 (한 번만 실행)
  var properties = PropertiesService.getScriptProperties();

  // API 키 생성 (32자리 랜덤 문자열)
  var apiKey = generateRandomKey(32);
  properties.setProperty('API_KEY', apiKey);

  Logger.log('Generated API Key: ' + apiKey);
  Logger.log('Please save this key securely and use it in your Python application.');
}

function generateRandomKey(length) {
  var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  var result = '';
  for (var i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}