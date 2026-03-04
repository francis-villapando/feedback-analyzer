let isEnabled = false;
let sidebarVisible = false;
let sidebar = null;
let mainContainer = null;
let jitsiToggleBtn = null;
const sidebarId = 'jitsi-ai-sidebar';

// Placeholders for development
const sampleData = {
  participants: ['Andrei Artillero', 'Roseanne Borber', 'Francis Villapando', 'Nino Ritualo', 'Lester Gomba'],
  feedbacks: [
    'ambilis ng explanation sa linked list, kahilo po haha',
    'parang kulang sa example yung binary tree traversal',
    'pwede po ba irepeat yung big o notation explanation?',
    'sobrang ganda ng recursive fibonacci example',
    'di ko pa nagegets yung hash table collision resolution',
  ],
  themes: [
    { label: 'Pace too fast', feedbacks: [0, 1, 2, 3, 4] },
    { label: 'Needs traversal examples', feedbacks: [1] },
    { label: 'Needs notation review', feedbacks: [2] },
    { label: 'Positive - recursion clear', feedbacks: [3] },
    { label: 'Hash collision confusion', feedbacks: [4] },
  ],
  recommendations: [
    { label: 'Add 30s pause after linked list insertion visuals', feedbacks: [0] },
    { label: 'Live demo inorder/preorder/postorder traversal side-by-side', feedbacks: [1] },
    { label: 'Show O(n) vs O(log n) graph + real array examples', feedbacks: [2] },
    { label: 'Build recursion visualization with call stack animation', feedbacks: [3] },
    { label: 'Demo chaining vs open addressing collision with live insert', feedbacks: [4] },
  ],
  issues: [
    'Audio quality too low for transcription in the last 2 minutes.'
  ],
};

// Inject CSS styles for sidebar UI
function injectStyles() {
  if (document.getElementById('jitsi-ai-styles')) return;
  const style = document.createElement('style');
  style.id = 'jitsi-ai-styles';
  style.textContent = `
    #${sidebarId} {
      position: fixed;
      top: 0;
      right: 0;
      width: 340px;
      height: 100vh;
      background: #FFFFFF;
      border-left: 1px solid #E0E0E0;
      box-shadow: -2px 0 8px rgba(0,0,0,0.08);
      font-family: Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
      color: #212121;
      z-index: 10000;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      animation: jai-slide-in 0.25s ease-out;
    }
    @keyframes jai-slide-in { from { transform: translateX(100%); } to { transform: translateX(0); } }
    .jai-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #E0E0E0; flex-shrink: 0; }
    .jai-header-title { font-size: 18px; font-weight: 600; color: #2E7D32; }
    .jai-close-btn { width: 28px; height: 28px; border: none; background: #F5F5F5; border-radius: 50%; cursor: pointer; font-size: 16px; color: #757575; display: flex; align-items: center; justify-content: center; transition: background 0.15s; }
    .jai-close-btn:hover { background: #E0E0E0; }
    .jai-content { flex: 1; overflow-y: auto; padding: 20px; }
    .jai-content::-webkit-scrollbar { width: 4px; }
    .jai-content::-webkit-scrollbar-thumb { background: #E0E0E0; border-radius: 2px; }
    .jai-counts { display: flex; gap: 12px; margin-bottom: 20px; }
    .jai-count-badge { display: flex; align-items: center; gap: 6px; padding: 8px 14px; background: #F5F5F5; border: 1px solid #E0E0E0; border-radius: 8px; font-size: 14px; font-weight: 500; color: #212121; cursor: default; flex: 1; justify-content: center; transition: background 0.15s; }
    .jai-count-badge:hover { background: #EEEEEE; }
    .jai-count-num { font-weight: 600; color: #2E7D32; }
    .jai-count-badge svg { width: 18px; height: 18px; color: #2E7D32; }
    .jai-popup { position: absolute; top: -10px; right: 100%; margin-right: 8px; width: 200px; max-height: 200px; background: #FFFFFF; border: 1px solid #E0E0E0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.12); padding: 12px; z-index: 10001; opacity: 0; pointer-events: none; transform: translateX(4px); transition: opacity 0.2s ease, transform 0.2s ease; overflow-y: auto; }
    .jai-popup::-webkit-scrollbar { width: 4px; }
    .jai-popup::-webkit-scrollbar-thumb { background: #E0E0E0; border-radius: 2px; }
    .jai-popup-title { font-size: 12px; font-weight: 600; color: #2E7D32; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
    .jai-popup-item { font-size: 13px; color: #212121; padding: 4px 0; border-bottom: 1px solid #F5F5F5; line-height: 1.4; }
    .jai-popup-item:last-child { border-bottom: none; }
    .jai-section { margin-bottom: 20px; }
    .jai-section-title { font-size: 12px; font-weight: 600; color: #757575; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .jai-item { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; padding: 10px 12px; background: #FFFFFF; border: 1px solid #F5F5F5; border-radius: 8px; margin-bottom: 6px; font-size: 14px; line-height: 1.45; color: #212121; transition: background 0.15s; }
    .jai-item:hover { background: #F5F5F5; }
    .jai-item-text { flex: 1; }
    .jai-source-dot { position: relative; width: 18px; height: 18px; min-width: 18px; border-radius: 50%; background: rgba(46,125,50,0.12); border: 1px solid rgba(46,125,50,0.3); cursor: default; display: flex; align-items: center; justify-content: center; margin-top: 2px; }
    .jai-source-dot::after { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #2E7D32; }
    .jai-source-dot .jai-popup { top: 50%; transform: translateY(-50%) translateX(4px); right: 100%; margin-right: 8px; max-height: 150px; overflow-y: auto; }
    .jai-issue { display: flex; align-items: flex-start; gap: 8px; padding: 10px 12px; background: #FFF3E0; border: 1px solid #FFE0B2; border-radius: 8px; margin-bottom: 6px; font-size: 13px; color: #E65100; line-height: 1.45; }
    .jai-issue svg { width: 16px; height: 16px; min-width: 16px; color: #E65100; margin-top: 1px; }
  `;
  document.head.appendChild(style);
}

// SVG icons
const icons = {
  people: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
  feedback: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
  warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
};

// Helper function to build hover‑popup list
function popupList(items) {
  return `
    <div class="jai-popup">
      ${items.map(i => `<div class="jai-popup-item">${i}</div>`).join('')}
    </div>`;
}

// Setup popup hover behavior after sidebar is created
function setupPopupHover() {
  // Handle .jai-popup-trigger elements
  document.querySelectorAll('.jai-popup-trigger').forEach(trigger => {
    const popup = trigger.querySelector('.jai-popup');
    if (!popup) return;
    
    let hideTimeout;
    const isSourceDot = trigger.classList.contains('jai-source-dot');
    
    // Show popup on mouseenter
    trigger.addEventListener('mouseenter', () => {
      clearTimeout(hideTimeout);
      popup.style.opacity = '1';
      popup.style.pointerEvents = 'auto';
      popup.style.transform = isSourceDot ? 'translateY(-50%) translateX(0)' : 'translateX(0)';
    });
    
    // Hide popup on mouseleave with delay
    trigger.addEventListener('mouseleave', () => {
      hideTimeout = setTimeout(() => {
        popup.style.opacity = '0';
        popup.style.pointerEvents = 'none';
        popup.style.transform = isSourceDot ? 'translateY(-50%) translateX(4px)' : 'translateX(4px)';
      }, 100);
    });
    
    // Keep popup visible when hovering the popup itself
    popup.addEventListener('mouseenter', () => {
      clearTimeout(hideTimeout);
      popup.style.opacity = '1';
      popup.style.pointerEvents = 'auto';
    });
    
    // Hide popup when leaving the popup
    popup.addEventListener('mouseleave', () => {
      hideTimeout = setTimeout(() => {
        popup.style.opacity = '0';
        popup.style.pointerEvents = 'none';
        popup.style.transform = isSourceDot ? 'translateY(-50%) translateX(4px)' : 'translateX(4px)';
      }, 100);
    });
  });
}

// Sidebar UI
function createSidebar() {
  if (document.getElementById(sidebarId)) return;
  injectStyles();

  mainContainer = document.querySelector('[role="main"]');
  if (mainContainer) {
    mainContainer.style.setProperty('margin-right', '350px', 'important');
  }

  sidebar = document.createElement('div');
  sidebar.id = sidebarId;

  const { participants, feedbacks, themes, recommendations, issues } = sampleData;

  sidebar.innerHTML = `
    <div class="jai-header">
      <span class="jai-header-title">Feedback Analyzer</span>
      <button class="jai-close-btn" id="jai-close" title="Close sidebar">✕</button>
    </div>
    <div class="jai-content">
      <div class="jai-counts">
        <div class="jai-count-badge jai-popup-trigger">
          ${icons.people}
          <span class="jai-count-num">${participants.length}</span> Participants
          ${popupList(participants)}
        </div>
        <div class="jai-count-badge jai-popup-trigger">
          ${icons.feedback}
          <span class="jai-count-num">${feedbacks.length}</span> Feedbacks
          ${popupList(feedbacks)}
        </div>
      </div>

      <div class="jai-section">
        <div class="jai-section-title">Feedback Themes</div>
        ${themes.map(t => `
          <div class="jai-item">
            <span class="jai-item-text">${t.label}</span>
            <div class="jai-source-dot jai-popup-trigger">
              ${popupList(t.feedbacks.map(i => feedbacks[i]))}
            </div>
          </div>
        `).join('')}
      </div>

      <div class="jai-section">
        <div class="jai-section-title">Teaching Strategy Recommendations</div>
        ${recommendations.map(r => `
          <div class="jai-item">
            <span class="jai-item-text">${r.label}</span>
            <div class="jai-source-dot jai-popup-trigger">
              ${popupList(r.feedbacks.map(i => feedbacks[i]))}
            </div>
          </div>
        `).join('')}
      </div>

      ${issues.length ? `
        <div class="jai-section">
          <div class="jai-section-title">Issues</div>
          ${issues.map(msg => `
            <div class="jai-issue">
              ${icons.warn}
              <span>${msg}</span>
            </div>
          `).join('')}
        </div>
      ` : ''}
    </div>
  `;

  document.body.appendChild(sidebar);
  sidebarVisible = true;
  
  // Setup popup hover behavior
  setupPopupHover();

  // Close sidebar
  document.getElementById('jai-close').addEventListener('click', () => {
    sidebar.style.animation = 'none';
    sidebar.style.transform = 'translateX(100%)';
    sidebar.style.transition = 'transform 0.2s ease';
    setTimeout(() => sidebar.remove(), 200);
    sidebarVisible = false;
    if (mainContainer) {
      mainContainer.style.marginRight = '';
    }
  });
}

function removeSidebar() {
  const el = document.getElementById(sidebarId);
  if (el) {
    el.remove();
    sidebarVisible = false;
  }
  if (mainContainer) {
    mainContainer.style.marginRight = '';
    mainContainer = null;
  }
}

// Jitsi toolbar button injection
function injectJitsiToggleButton() {
  const toolbar = document.querySelector('.toolbox-content-items');
  if (!toolbar || jitsiToggleBtn) return;

  jitsiToggleBtn = document.createElement('div');
  jitsiToggleBtn.className = 'toolbox-button';
  jitsiToggleBtn.setAttribute('role', 'button');
  jitsiToggleBtn.setAttribute('tabindex', '0');
  jitsiToggleBtn.setAttribute('aria-disabled', 'false');
  jitsiToggleBtn.style.cursor = 'pointer';

  jitsiToggleBtn.innerHTML = `
    <div style="width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: inherit; overflow: hidden;">
      <img src="${chrome.runtime.getURL('icon32.png')}" style="width: 100%; height: 100%; object-fit: cover; display: block; border-radius: inherit;" aria-hidden="true" />
    </div>
  `;

  jitsiToggleBtn.addEventListener('click', toggleSidebar);

  jitsiToggleBtn.addEventListener('mouseenter', () => { jitsiToggleBtn.style.background = 'rgba(0,0,0,0.1)'; });
  jitsiToggleBtn.addEventListener('mouseleave', () => { jitsiToggleBtn.style.background = ''; });

  toolbar.appendChild(jitsiToggleBtn);
  console.log('Feedback Analyzer button injected');
}

function removeJitsiToggleButton() {
  if (jitsiToggleBtn) {
    jitsiToggleBtn.remove();
    jitsiToggleBtn = null;
  }
  removeSidebar();
}

function toggleSidebar() {
  if (sidebarVisible) {
    removeSidebar();
  } else {
    createSidebar();
  }
}

// Helper function to check if in Jitsi meet
function isMeetingActive() {
  const hasToolbox = !!document.querySelector('.toolbox-content-items');
  const hasPrejoin = !!document.querySelector('[data-testid="prejoin.joinMeeting"]');
  const hasLogin = !!document.querySelector('[data-testid="lobby.loginButton"]');
  return hasToolbox && !hasPrejoin && !hasLogin;
}

// Message handler from popup.js
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'toggleMaster') {
    const meetingActive = isMeetingActive();
    
    console.log('[Feedback Analyzer] toggleMaster called:', { meetingActive, isEnabled });

    if (!meetingActive) {
      sendResponse({ success: false, isEnabled, isMeetingActive: false });
      return true;
    }

    isEnabled = !isEnabled;
    if (isEnabled) {
      injectJitsiToggleButton();
    } else {
      removeJitsiToggleButton();
    }
    sendResponse({ success: true, isEnabled, isMeetingActive: true });
    return true;
  }

  // Popup UI asks for current state
  if (msg.action === 'getState') {
    const meetingActive = isMeetingActive();
    
    console.log('[Feedback Analyzer] getState called:', { meetingActive, isEnabled });
    
    sendResponse({ isEnabled, isMeetingActive: meetingActive });
    return true;
  }

  // Sidebar toggle request from popup
  if (msg.type === 'toggleSidebar') {
    msg.enabled ? createSidebar() : removeSidebar();
    return true;
  }

  return true;
});
