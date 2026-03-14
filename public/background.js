chrome.runtime.onInstalled.addListener(() => {
  console.log('Jitsi AI-powered feedback analyzer installed');
});

// Clear selections when extension is disabled or uninstalled
chrome.management.onDisabled.addListener((info) => {
  if (info.id === chrome.runtime.id) {
    chrome.storage.local.remove(['courseSelection']);
    console.log('Extension disabled - selections cleared');
  }
});

chrome.management.onUninstalled.addListener((info) => {
  if (info.id === chrome.runtime.id) {
    chrome.storage.local.remove(['courseSelection']);
    console.log('Extension uninstalled - selections cleared');
  }
});
