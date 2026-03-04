let sidebarVisible = false;
let sidebar = null;
let mainContainer = null;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "toggleSidebar") {
    toggleSidebar();
    sendResponse({ success: true });
  }
});

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
  console.log('White sidebar injected');
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

// Auto-cleanup
window.addEventListener('unload', hideSidebar);
