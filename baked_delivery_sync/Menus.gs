function createMenus() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Baked Tools')
      .addItem('Sync for Delivery', 'makeHTTPRequest')
      .addItem('Send Test', 'sendTestEmailer')
      .addItem('Send to Client', 'sendEmailsEmailer')
      .addSeparator()
      .addItem('Sync for Tracking [CLT]', 'handleSyncMenuItem')
      .addToUi();
}

function sendTestEmailer() {
  sendTest("Emailer");
}

function sendEmailsEmailer() {
  sendEmails("Emailer");
}

function onInstall(e) {
  createMenus();
}

function onOpen() {
  createMenus();
}
