function doGet(e) {
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
    var sheetId = requestData.sheetId;
    var sheetName = requestData.sheetName || 'Sheet1';
    var action = requestData.action;
    var data = requestData.data;
    var range = requestData.range;

    if (!sheetId) {
      return createResponse({error: 'sheetId required'}, 400);
    }

    var sheet = SpreadsheetApp.openById(sheetId);
    var worksheet = null;

    // 시트 생성 및 시트 목록 조회의 경우 worksheet가 null이어도 됨
    if (action !== 'create_sheet' && action !== 'get_sheet_names') {
      worksheet = sheet.getSheetByName(sheetName);
      if (!worksheet) {
        return createResponse({error: 'Worksheet not found'}, 404);
      }
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

      case 'create_sheet':
        if (!sheetName || sheetName === 'Sheet1') {
          return createResponse({error: 'Valid sheetName required for creating new sheet'}, 400);
        }

        // 시트가 이미 존재하는지 확인
        var existingSheet = sheet.getSheetByName(sheetName);
        if (existingSheet) {
          result = {success: true, action: 'create_sheet', message: 'Sheet already exists', sheetName: sheetName};
        } else {
          // 새 시트 생성
          var newSheet = sheet.insertSheet(sheetName);
          result = {success: true, action: 'create_sheet', sheetName: sheetName, sheetId: newSheet.getSheetId()};
        }
        break;

      case 'get_sheet_names':
        var sheets = sheet.getSheets();
        var sheetNames = sheets.map(function(s) { return s.getName(); });
        result = {success: true, action: 'get_sheet_names', sheet_names: sheetNames, count: sheetNames.length};
        break;

      default:
        return createResponse({error: 'Invalid action. Use: update, append, clear, overwrite, create_sheet, get_sheet_names'}, 400);
    }

    return createResponse(result);

  } catch (error) {
    return createResponse({error: error.toString()}, 500);
  }
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