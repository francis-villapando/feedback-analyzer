let sidebarVisible = false;
let sidebar = null;
let mainContainer = null;
let jitsiToggleBtn = null;
let masterEnabled = false;

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "toggleMaster") {
    masterEnabled = !masterEnabled;
    if (masterEnabled) {
      injectJitsiToggleButton();
    } else {
      removeJitsiToggleButton();
    }
    sendResponse({ success: true, isEnabled: masterEnabled });
  } else if (request.action === "getState") {
    sendResponse({ isEnabled: masterEnabled });
  }
  return true; // Indicates we will send a response synchronously or asynchronously
});

function injectJitsiToggleButton() {
  const toolbar = document.querySelector('.toolbox-content-items');
  if (!toolbar || jitsiToggleBtn) return;

  // Clone Jitsi's exact button structure
  jitsiToggleBtn = document.createElement('div');
  jitsiToggleBtn.className = 'toolbox-button';
  jitsiToggleBtn.setAttribute('role', 'button');
  jitsiToggleBtn.setAttribute('tabindex', '0');
  jitsiToggleBtn.setAttribute('aria-disabled', 'false');
  jitsiToggleBtn.style.cursor = 'pointer';

  // Inner structure matching Jitsi exactly
  jitsiToggleBtn.innerHTML = `
    <div style="width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: inherit; overflow: hidden;">
      <img src="${chrome.runtime.getURL('icon32.png')}" 
           style="width: 100%; height: 100%; object-fit: cover; display: block; border-radius: inherit;" 
           aria-hidden="true">
    </div>
  `;

  // Add click handler to the outer div (matches Jitsi's pattern)
  jitsiToggleBtn.addEventListener('click', toggleSidebar);

  // Jitsi hover effects
  jitsiToggleBtn.addEventListener('mouseenter', () => {
    jitsiToggleBtn.style.background = 'rgba(0,0,0,0.1)';
  });
  jitsiToggleBtn.addEventListener('mouseleave', () => {
    jitsiToggleBtn.style.background = '';
  });

  toolbar.appendChild(jitsiToggleBtn);
  console.log('Feedback analyzer button injected');
}

function removeJitsiToggleButton() {
  if (jitsiToggleBtn) {
    jitsiToggleBtn.remove();
    jitsiToggleBtn = null;
  }
  hideSidebar(); // Also hide sidebar when disabling
}

// Rest of your existing showSidebar/hideSidebar functions stay THE SAME
function toggleSidebar() {
  if (sidebarVisible) {
    hideSidebar();
  } else {
    showSidebar();
  }
}

function showSidebar() {
  mainContainer = document.querySelector('[role="main"]');
  if (!mainContainer) return;

  mainContainer.style.setProperty('margin-right', '350px', 'important');

  sidebar = document.createElement('div');
  sidebar.id = 'ai-sidebar';
  sidebar.innerHTML = '<h3 style="margin:0;padding:10px;background:#f0f0f0;border-bottom:1px solid #ddd">AI Sidebar</h3><div style="padding:20px;height:calc(100vh - 60px);overflow:auto">Messages will appear here</div>';

  sidebar.style.cssText = `
    position: fixed !important;
    right: 0 !important;
    top: 0 !important;
    width: 340px !important;
    height: 100vh !important;
    background: white !important;
    border-left: 1px solid #ccc !important;
    box-shadow: -4px 0 20px rgba(0,0,0,0.2) !important;
    z-index: 2147483647 !important;
    overflow: hidden !important;
  `;

  document.body.appendChild(sidebar);
  sidebarVisible = true;
}

function hideSidebar() {
  if (sidebar) {
    sidebar.remove();
  }
  if (mainContainer) {
    mainContainer.style.marginRight = '';
  }
  sidebarVisible = false;
}
