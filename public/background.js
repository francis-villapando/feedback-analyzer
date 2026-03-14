chrome.runtime.onInstalled.addListener(() => {
  console.log('Jitsi AI-powered feedback analyzer installed');
});

// Clear selections when extension is disabled or uninstalled
chrome.management.onDisabled.addListener((info) => {
  if (info.id === chrome.runtime.id) {
    // Notify active tabs to clean up server data
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      tabs.forEach(tab => {
        if (tab.url && tab.url.includes('meet.jit.si')) {
          chrome.tabs.sendMessage(tab.id, {action: 'extensionDisabled'}, (response) => {
            if (chrome.runtime.lastError) {
              // Tab might not be active or content script not loaded, just clear local storage
              chrome.storage.local.remove(['courseSelection']);
            }
          });
        } else {
          chrome.storage.local.remove(['courseSelection']);
        }
      });
    });
  }
});

chrome.management.onUninstalled.addListener((info) => {
  if (info.id === chrome.runtime.id) {
    // Notify active tabs to clean up server data
    chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
      tabs.forEach(tab => {
        if (tab.url && tab.url.includes('meet.jit.si')) {
          chrome.tabs.sendMessage(tab.id, {action: 'extensionDisabled'}, (response) => {
            if (chrome.runtime.lastError) {
              // Tab might not be active or content script not loaded, just clear local storage
              chrome.storage.local.remove(['courseSelection']);
            }
          });
        } else {
          chrome.storage.local.remove(['courseSelection']);
        }
      });
    });
  }
});
