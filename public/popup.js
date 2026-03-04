let isEnabled = false;

// UI helpers

function setDisabledUI(message) {
  const btn = document.getElementById('masterToggle');
  const status = document.getElementById('status');
  btn.disabled = true;
  btn.classList.remove('active');
  status.textContent = message;
  status.classList.add('warning');
  status.classList.remove('active');
}

function updateUI(isMeetingActive = true) {
  const btn = document.getElementById('masterToggle');
  const status = document.getElementById('status');

  if (!isMeetingActive) {
    setDisabledUI('Please join a meeting first');
    return;
  }

  btn.disabled = false;

  // Clear warning style for normal statuses
  status.classList.remove('warning');

  if (isEnabled) {
    btn.classList.add('active');
    status.textContent = 'Analyzer is active';
    status.classList.add('active');
  } else {
    btn.classList.remove('active');
    status.textContent = 'Analyzer is disabled';
    status.classList.remove('active');
  }
}

// On popup open: check tab and get current state

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
      updateUI(response.isMeetingActive);
    }
  });
});

// Toggle button click

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
        updateUI(response.isMeetingActive);
      }
    });
  });
});

// Privacy panel toggle

document.getElementById('privacyToggle').addEventListener('click', () => {
  const panel = document.getElementById('privacyPanel');
  const button = document.getElementById('privacyToggle');
  const isOpen = panel.classList.toggle('open');
  button.setAttribute('aria-expanded', isOpen);
});
