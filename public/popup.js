let isEnabled = false;

function setDisabledUI(message) {
  const btn = document.getElementById('masterToggle');
  const status = document.getElementById('status');
  btn.disabled = true;
  btn.style.background = '#ccc';
  btn.style.cursor = 'not-allowed';
  btn.textContent = 'Enable Analyzer';
  status.textContent = message;
}

function updateUI(isPrejoin = false) {
  const btn = document.getElementById('masterToggle');
  const status = document.getElementById('status');

  if (isPrejoin) {
    setDisabledUI('Please join a meeting first');
    return;
  }

  btn.disabled = false;
  btn.style.cursor = 'pointer';

  if (isEnabled) {
    btn.textContent = 'Disable Analyzer';
    btn.style.background = '#34a853';
    status.textContent = 'Enabled';
  } else {
    btn.textContent = 'Enable Analyzer';
    btn.style.background = '#4285f4';
    status.textContent = 'Disabled';
  }
}

// Fetch initial state when popup opens
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (!tabs[0] || !tabs[0].url || !tabs[0].url.includes('meet.jit.si')) {
    setDisabledUI('Please open Jitsi Meet first');
    return;
  }

  chrome.tabs.sendMessage(tabs[0].id, { action: "getState" }, (response) => {
    if (chrome.runtime.lastError) {
      console.log('Content script not found or error:', chrome.runtime.lastError);
      return;
    }
    if (response !== undefined) {
      isEnabled = response.isEnabled;
      updateUI(response.isPrejoin);
    }
  });
});

document.getElementById('masterToggle').addEventListener('click', () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0] || !tabs[0].url || !tabs[0].url.includes('meet.jit.si')) {
      setDisabledUI('Please open Jitsi Meet first');
      return;
    }

    chrome.tabs.sendMessage(tabs[0].id, { action: "toggleMaster" }, (response) => {
      if (chrome.runtime.lastError) {
        console.log('Error:', chrome.runtime.lastError);
        return;
      }
      if (response) {
        isEnabled = response.isEnabled;
        updateUI(response.isPrejoin);
      }
    });
  });
});
