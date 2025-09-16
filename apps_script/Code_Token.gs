// 토큰 인증이 추가된 Apps Script 코드
// 기존 코드에 토큰 검증만 추가

function doGet(e) {
  // 토큰 검증
  if (!validateToken(e.parameter.token)) {
    return createResponse({error: 'Unauthorized access - invalid token'}, 401);
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

    return createResponse({
      success: true,
      data: data,
      rows: data.length,
      columns: data[0] ? data[0].length : 0
    });

  } catch (error) {
    return createResponse({error: error.toString()}, 500);
  }
}

function doPost(e) {
  try {
    var requestData = JSON.parse(e.postData.contents);

    // 토큰 검증
    if (!validateToken(requestData.token)) {
      return createResponse({error: 'Unauthorized access - invalid token'}, 401);
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
      case 'update':
        if (range && data) {
          worksheet.getRange(range).setValues(data);
          result = {success: true, action: 'updated', range: range};
        } else {
          return createResponse({error: 'range and data required for update'}, 400);
        }
        break;

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

      case 'clear':
        if (range) {
          worksheet.getRange(range).clear();
          result = {success: true, action: 'cleared', range: range};
        } else {
          worksheet.clear();
          result = {success: true, action: 'cleared', range: 'all'};
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
        return createResponse({error: 'Invalid action. Use: update, append, clear, overwrite'}, 400);
    }

    return createResponse(result);

  } catch (error) {
    return createResponse({error: error.toString()}, 500);
  }
}

function validateToken(providedToken) {
  // 유효한 토큰 목록 (여러 개 설정 가능)
  var validTokens = [
    'SecureToken123ABC',           // 메인 토큰
    'BackupToken456DEF',           // 백업 토큰
    'DevToken789GHI'               // 개발용 토큰
  ];

  return providedToken && validTokens.indexOf(providedToken) !== -1;
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

function testFunction() {
  var testSheetId = 'YOUR_SHEET_ID_HERE';
  var sheet = SpreadsheetApp.openById(testSheetId);
  var worksheet = sheet.getActiveSheet();

  worksheet.appendRow(['테스트', '데이터', new Date()]);

  Logger.log('테스트 완료');
}