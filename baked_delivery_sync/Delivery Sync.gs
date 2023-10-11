function makeHTTPRequest() {
  // Open a dialog box for user input
  var ui = SpreadsheetApp.getUi();
  var response = ui.prompt('Sync for Delivery', 'Add Submission Details/Notes:', ui.ButtonSet.OK_CANCEL);
  
  // Check if OK button was clicked
  if (response.getSelectedButton() == ui.Button.OK) {
    // Get the input value
    var inputValue = response.getResponseText();
    
    // Get the active sheet
    var sheet = SpreadsheetApp.getActiveSheet();
    
    // Set the value in cell A1
    sheet.getRange('Emailer!G2').setValue(inputValue);
  } else {
    // If Cancel button was clicked, do nothing
    Logger.log('User clicked cancel.');
  }

  var fileId = SpreadsheetApp.getActiveSpreadsheet().getId();
  var file = DriveApp.getFileById(fileId);
  
  // Set sharing settings to "Anyone with the link can edit"
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.EDIT);
  
  // Add service account as an editor
  file.addEditor('baked-sheet-sync@appspot.gserviceaccount.com');

  // Get sheet name etc and make service request
  var sheetName = SpreadsheetApp.getActiveSpreadsheet().getName();
  var projectName = sheetName.substring(0, 3);
  
  var dateStringMatch = sheetName.match(/\d{6}/);
  var deliveryIteration = "";
  
  if (dateStringMatch) {
    var dateIndex = dateStringMatch.index;
    if (sheetName.charAt(dateIndex + 6) === "_") {
      deliveryIteration = sheetName.substring(dateIndex + 7, dateIndex + 9);
    }
  }

  var params = {
    "project_name": projectName,
    "delivery_iteration": deliveryIteration
  };

  var queryString = Object.keys(params).map(key => key + '=' + params[key]).join('&');
  
  Logger.log("Query string: " + queryString);
  Logger.log("Project Name: " + projectName);
  Logger.log("Delivery Iteration: " + deliveryIteration);

  var response = UrlFetchApp.fetch("https://us-central1-send-to-client-app.cloudfunctions.net/delivery-sync?" + queryString, {"muteHttpExceptions": true});
  
  // Check HTTP response
  var statusCode = response.getResponseCode();
  var content = response.getContentText();
  
  if (statusCode !== 200) {
    // Only show UI alert for errors
    Logger.log("Error (status " + statusCode + "): " + content);
    SpreadsheetApp.getUi().alert('An error occurred: ' + content);
  } else {
    // Log success for debugging but no UI alert
    Logger.log("Success: " + content);
  }
}

