let isEnabled = false;
let sidebarVisible = false;
let sidebar = null;
let mainContainer = null;
let jitsiToggleBtn = null;
let selectedCourse = null;
let selectedCourseName = null;
let selectedTopic = null;
const sidebarId = 'jitsi-ai-sidebar';

// Consent state for data collection
let consentPollSent = false;
const consentState = {
  pollId: null,
  question: 'Do you consent to the collection of your name and chat messages in this meeting for AI-powered feedback analysis during this session?',
  responses: {}, // participantId -> 'yes' | 'no' | null
  timestamp: null
};

// Reset consent state when meeting changes
function resetConsentState() {
  consentPollSent = false;
  consentState.pollId = null;
  consentState.responses = {};
  consentState.timestamp = null;
  chrome.storage.local.remove(['consentState']);
  console.log('[Feedback Analyzer] Consent state reset');
}

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
    { label: 'Recursion clear', feedbacks: [3] },
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
    .jai-source-dot.positive { background: rgba(66,133,244,0.12); border: 1px solid rgba(66,133,244,0.3); }
    .jai-source-dot.positive::after { background: #4285F4; }
    .jai-source-dot.negative { background: rgba(219,68,55,0.12); border: 1px solid rgba(219,68,55,0.3); }
    .jai-source-dot.negative::after { background: #DB4437; }
    .jai-source-dot .jai-popup { top: 50%; transform: translateY(-50%) translateX(4px); right: 100%; margin-right: 8px; max-height: 150px; overflow-y: auto; }
    .jai-issue { display: flex; align-items: flex-start; gap: 8px; padding: 10px 12px; background: #FFF3E0; border: 1px solid #FFE0B2; border-radius: 8px; margin-bottom: 6px; font-size: 13px; color: #E65100; line-height: 1.45; }
    .jai-issue svg { width: 16px; height: 16px; min-width: 16px; color: #E65100; margin-top: 1px; }
    .jai-consent-btn { width: 100%; padding: 12px 16px; background: #2E7D32; color: #FFFFFF; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s ease; margin-bottom: 20px; }
    .jai-consent-btn:hover { background: #388E3C; }
    .jai-consent-btn:disabled { background: #CCCCCC; cursor: not-allowed; }
    .jai-consent-btn.sent { background: #757575; }
  `;
  document.head.appendChild(style);
}

// SVG icons
const icons = {
  people: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
  feedback: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
  warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
};

// Helper function for hover‑popup list
function popupList(items) {
  return `
    <div class="jai-popup">
      ${items.map(i => `<div class="jai-popup-item">${i}</div>`).join('')}
    </div>`;
}

// Helper function for theme type (will use proper NLP classification in the future)
function getThemeType(label) {
  const positiveKeywords = ['positive', 'good', 'great', 'clear', 'excellent', 'helpful'];
  const negativeKeywords = ['confusion', 'confused', 'difficult', 'hard', 'fast', 'slow', 'needs', 'lack', 'missing', 'unclear', ' kulang', ' hirap', 'di ko'];
  
  const lowerLabel = label.toLowerCase();
  
  if (positiveKeywords.some(kw => lowerLabel.includes(kw))) {
    return 'positive';
  }
  if (negativeKeywords.some(kw => lowerLabel.includes(kw))) {
    return 'negative';
  }
  return '';
}

// Helper function for popup hover behavior
function setupPopupHover() {
  document.querySelectorAll('.jai-popup-trigger').forEach(trigger => {
    const popup = trigger.querySelector('.jai-popup');
    if (!popup) return;
    
    let hideTimeout;
    const isSourceDot = trigger.classList.contains('jai-source-dot');
    
    trigger.addEventListener('mouseenter', () => {
      clearTimeout(hideTimeout);
      popup.style.opacity = '1';
      popup.style.pointerEvents = 'auto';
      popup.style.transform = isSourceDot ? 'translateY(-50%) translateX(0)' : 'translateX(0)';
    });
    
    trigger.addEventListener('mouseleave', () => {
      hideTimeout = setTimeout(() => {
        popup.style.opacity = '0';
        popup.style.pointerEvents = 'none';
        popup.style.transform = isSourceDot ? 'translateY(-50%) translateX(4px)' : 'translateX(4px)';
      }, 100);
    });
    
    popup.addEventListener('mouseenter', () => {
      clearTimeout(hideTimeout);
      popup.style.opacity = '1';
      popup.style.pointerEvents = 'auto';
    });
    
    popup.addEventListener('mouseleave', () => {
      hideTimeout = setTimeout(() => {
        popup.style.opacity = '0';
        popup.style.pointerEvents = 'none';
        popup.style.transform = isSourceDot ? 'translateY(-50%) translateX(4px)' : 'translateX(4px)';
      }, 100);
    });
  });
}

// Open sidebar
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
  
  // Build course/topic display string
  const courseTopicDisplay = selectedCourseName && selectedTopic 
    ? `${selectedCourseName} - ${selectedTopic}` 
    : 'Feedback Analyzer';

  // Load consent state from storage and reset for new meeting session
  chrome.storage.local.get(['consentState'], (result) => {
    // Reset consent state for new meeting - this is a fresh session
    resetConsentState();
    
    // Update button to initial state (not sent)
    updateConsentButton(false);
    console.log('[Feedback Analyzer] Consent state reset for new meeting');
  });

  sidebar.innerHTML = `
    <div class="jai-header">
      <span class="jai-header-title">${courseTopicDisplay}</span>
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

      <button id="sendConsentBtn" class="jai-consent-btn ${consentPollSent ? 'sent' : ''}">
        ${consentPollSent ? 'Consent Poll Sent' : 'Send Consent Notice'}
      </button>

      <div class="jai-section">
        <div class="jai-section-title">Feedback Themes</div>
        ${themes.map(t => {
          const themeType = getThemeType(t.label);
          const dotClass = themeType ? `jai-source-dot ${themeType}` : 'jai-source-dot';
          return `
          <div class="jai-item">
            <span class="jai-item-text">${t.label}</span>
            <div class="${dotClass} jai-popup-trigger">
              ${popupList(t.feedbacks.map(i => feedbacks[i]))}
            </div>
          </div>`;
        }).join('')}
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

  // Send Consent Notice button
  const consentBtn = document.getElementById('sendConsentBtn');
  console.log('[Feedback Analyzer] Consent button found:', !!consentBtn, 'consentPollSent:', consentPollSent);
  
  if (consentBtn) {
    consentBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      console.log('[Feedback Analyzer] Button clicked, consentPollSent:', consentPollSent);
      
      if (!consentPollSent) {
        createConsentPoll();
      } else {
        console.log('[Feedback Analyzer] Poll already sent, skipping');
      }
    });
  } else {
    console.log('[Feedback Analyzer] ERROR: Consent button not found in DOM');
  }
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

// Create consent poll in Jitsi using UI interaction
function createConsentPoll() {
  const pollQuestion = 'Do you consent to the collection of your name and chat messages in this meeting for AI-powered feedback analysis during this session?';
  const pollOptions = ['Yes, I consent', "No, I don't consent"];
  
  // Initialize consent state
  consentPollSent = true;
  consentState.pollId = 'consent-' + Date.now();
  consentState.question = pollQuestion;
  consentState.responses = {};
  consentState.timestamp = Date.now();
  
  console.log('[Feedback Analyzer] Creating consent poll via UI:', { pollQuestion, pollOptions });
  
  // Step 1: Click open chat button to reveal chat panel
  const chatButton = document.querySelector('#new-toolbox > div > div > div > div:nth-child(4)');
  
  if (!chatButton) {
    console.log('[Feedback Analyzer] Could not find chat button');
    updateConsentButton();
    chrome.storage.local.set({ consentState: consentState });
    return;
  }
  
  chatButton.click();
  console.log('[Feedback Analyzer] Clicked chat button');
  
  // Step 2: Wait for chat panel and click polls tab
  setTimeout(() => {
    // Try multiple selectors for polls tab
    let pollsTab = document.querySelector('#polls-tab');
    
    if (!pollsTab) {
      // Try the alternative selector
      pollsTab = document.querySelector('#new-toolbox > div > div > div > div:nth-child(4) > div > div > div');
    }
    
    if (!pollsTab) {
      console.log('[Feedback Analyzer] Could not find polls tab');
      updateConsentButton();
      chrome.storage.local.set({ consentState: consentState });
      return;
    }
    
    pollsTab.click();
    console.log('[Feedback Analyzer] Clicked polls tab');
    
    // Step 3: Wait for polls panel and click "Create poll" button
    setTimeout(() => {
      const createPollButton = document.querySelector('button[aria-label="Create a poll"]');
      
      if (!createPollButton) {
        console.log('[Feedback Analyzer] Could not find Create a poll button');
        updateConsentButton();
        chrome.storage.local.set({ consentState: consentState });
        return;
      }
      
      createPollButton.click();
      console.log('[Feedback Analyzer] Clicked Create a poll button');
      
      // Step 4: Wait for poll dialog and fill it
      setTimeout(() => {
        fillPollDialog(pollQuestion, pollOptions);
        
        // Update button state
        updateConsentButton();
        chrome.storage.local.set({ consentState: consentState });
      }, 300); // Wait for dialog
      
    }, 500); // Wait for polls panel
    
  }, 500); // Wait for chat panel
}

// Find the polls button in Jitsi's toolbar
function findPollsButton() {
  // Use the exact selector provided by user
  const button = document.querySelector('button[aria-label="Create a poll"]');
  
  if (button) {
    console.log('[Feedback Analyzer] Found polls button');
    return button;
  }
  
  console.log('[Feedback Analyzer] Could not find polls button');
  return null;
}

// Fill the poll dialog with question and options
function fillPollDialog(question, options) {
  // Use exact selectors provided by user
  const questionInput = document.querySelector('#polls-create-input');
  const option1Input = document.querySelector('#polls-answer-input-0');
  const option2Input = document.querySelector('#polls-answer-input-1');
  const submitButton = document.querySelector('button[aria-label="Save"]');
  
  console.log('[Feedback Analyzer] Dialog elements:', {
    questionInput: !!questionInput,
    option1Input: !!option1Input,
    option2Input: !!option2Input,
    submitButton: !!submitButton
  });
  
  let filled = false;
  
  if (questionInput) {
    // Set the question value
    questionInput.value = question;
    questionInput.dispatchEvent(new Event('input', { bubbles: true }));
    questionInput.dispatchEvent(new Event('change', { bubbles: true }));
    console.log('[Feedback Analyzer] Set poll question');
    filled = true;
  }
  
  if (option1Input) {
    option1Input.value = options[0];
    option1Input.dispatchEvent(new Event('input', { bubbles: true }));
    console.log('[Feedback Analyzer] Set option 1');
    filled = true;
  }
  
  if (option2Input) {
    option2Input.value = options[1];
    option2Input.dispatchEvent(new Event('input', { bubbles: true }));
    console.log('[Feedback Analyzer] Set option 2');
    filled = true;
  }
  
  if (submitButton) {
    submitButton.click();
    console.log('[Feedback Analyzer] Clicked Save button');
  } else {
    console.log('[Feedback Analyzer] Save button not found');
  }
  
  return filled;
}

// Update consent button state
function updateConsentButton(sent = true) {
  const consentBtn = document.getElementById('sendConsentBtn');
  if (consentBtn) {
    if (sent) {
      consentBtn.textContent = 'Consent Poll Sent';
      consentBtn.classList.add('sent');
    } else {
      consentBtn.textContent = 'Send Consent Notice';
      consentBtn.classList.remove('sent');
    }
  }
}

// Get Jitsi conference object
function getJitsiConference() {
  // Jitsi stores the conference in the global APP object
  if (window.APP && window.APP.conference) {
    return window.APP.conference;
  }
  return null;
}

// Check if data collection is allowed for a participant
function canCollectData(participantId) {
  // Only collect data if consent poll was sent and participant consented
  if (!consentPollSent) {
    return false;
  }
  
  const consent = consentState.responses[participantId];
  return consent === 'yes';
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
    
    console.log('[Feedback Analyzer] toggleMaster called:', { meetingActive, isEnabled, course: msg.course, topic: msg.topic });

    if (!meetingActive) {
      sendResponse({ success: false, isEnabled, isMeetingActive: false });
      return true;
    }

    // Store course/topic selections
    selectedCourse = msg.course || null;
    selectedCourseName = msg.courseName || null;
    selectedTopic = msg.topic || null;

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
    
    console.log('[Feedback Analyzer] getState called:', { meetingActive, isEnabled, selectedCourse, selectedTopic });
    
    sendResponse({ 
      isEnabled, 
      isMeetingActive: meetingActive,
      selectedCourse: selectedCourse,
      selectedCourseName: selectedCourseName,
      selectedTopic: selectedTopic
    });
    return true;
  }

  return true;
});
