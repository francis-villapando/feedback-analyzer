(function () {
  window.FA_UI = window.FA_UI || {};

  let sidebarVisible = false;
  let sidebar = null;
  let mainContainer = null;
  let jitsiToggleBtn = null;
  let consentPollSent = false;
  const sidebarId = 'jitsi-ai-sidebar';

  // Add message listener for AI results from content.js
  window.addEventListener('message', function(event) {
    if (event.data.type === 'FA_AI_RESULT') {
      console.log('[FA:UI] Received AI result');
      displayAIResult(event.data.data);
    }
  });

  function displayAIResult(result) {
    console.log('[FA:UI] Displaying in sidebar');
    
    // Update Teaching Strategy Recommendations section - append new strategy (NO PROBLEM, ONLY STRATEGY)
    const strategyContent = document.getElementById('jai-strategies-content');
    if (strategyContent) {
      // Remove placeholder if exists
      if (strategyContent.querySelector('.jai-placeholder')) {
        strategyContent.innerHTML = '';
      }
      
      // Only show strategy for pedagogical messages
      if (result.is_pedagogical && result.strategy) {
        strategyContent.innerHTML += `
          <div class="jai-item">
            <span>${result.strategy}</span>
          </div>
        `;
      }
    }
  }

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
        background: #141515;
        border-left: 1px solid #2A2A2A;
        box-shadow: -2px 0 8px rgba(0,0,0,0.4);
        font-family: Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
        color: #E0E0E0;
        z-index: 10000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        animation: jai-slide-in 0.25s ease-out;
      }
      @keyframes jai-slide-in { from { transform: translateX(100%); } to { transform: translateX(0); } }
      .jai-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 20px; border-bottom: 1px solid #2A2A2A; flex-shrink: 0; }
      .jai-header-title { font-size: 18px; font-weight: 600; color: #4686ec; }
      .jai-close-btn { width: 28px; height: 28px; border: none; background: #1E1E1E; border-radius: 50%; cursor: pointer; font-size: 16px; color: #A0A0A0; display: flex; align-items: center; justify-content: center; transition: background 0.15s; }
      .jai-close-btn:hover { background: #252525; }
      .jai-content { flex: 1; overflow-y: auto; padding: 20px; }
      .jai-content::-webkit-scrollbar { width: 4px; }
      .jai-content::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 2px; }
      .jai-counts { display: flex; gap: 12px; margin-bottom: 20px; }
      .jai-count-badge { display: flex; align-items: center; gap: 6px; padding: 8px 14px; background: #1E1E1E; border: 1px solid #2A2A2A; border-radius: 8px; font-size: 14px; font-weight: 500; color: #E0E0E0; cursor: default; flex: 1; justify-content: center; transition: background 0.15s; }
      .jai-count-badge:hover { background: #252525; }
      .jai-count-num { font-weight: 600; color: #4686ec; }
      .jai-count-badge svg { width: 18px; height: 18px; color: #4686ec; }
      .jai-popup { position: absolute; top: -10px; right: 100%; margin-right: 8px; width: 200px; max-height: 200px; background: #141515; border: 1px solid #2A2A2A; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.4); padding: 12px; z-index: 10001; opacity: 0; pointer-events: none; transform: translateX(4px); transition: opacity 0.2s ease, transform 0.2s ease; overflow-y: auto; }
      .jai-popup::-webkit-scrollbar { width: 4px; }
      .jai-popup::-webkit-scrollbar-thumb { background: #2A2A2A; border-radius: 2px; }
      .jai-popup-title { font-size: 12px; font-weight: 600; color: #4686ec; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.5px; }
      .jai-popup-item { font-size: 13px; color: #E0E0E0; padding: 4px 0; border-bottom: 1px solid #2A2A2A; line-height: 1.4; }
      .jai-popup-item:last-child { border-bottom: none; }
      .jai-section { margin-bottom: 20px; }
      .jai-section-title { font-size: 12px; font-weight: 600; color: #A0A0A0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
      .jai-item { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; padding: 10px 12px; background: #1E1E1E; border: 1px solid #2A2A2A; border-radius: 8px; margin-bottom: 6px; font-size: 14px; line-height: 1.45; color: #E0E0E0; transition: background 0.15s; }
      .jai-item:hover { background: #252525; }
      .jai-item-text { flex: 1; }
      .jai-source-dot { position: relative; width: 18px; height: 18px; min-width: 18px; border-radius: 50%; background: rgba(70,134,236,0.12); border: 1px solid rgba(70,134,236,0.3); cursor: default; display: flex; align-items: center; justify-content: center; margin-top: 2px; }
      .jai-source-dot::after { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #4686ec; }
      .jai-source-dot.positive { background: rgba(70,134,236,0.12); border: 1px solid rgba(70,134,236,0.3); }
      .jai-source-dot.positive::after { background: #4686ec; }
      .jai-source-dot.negative { background: rgba(239,83,80,0.12); border: 1px solid rgba(239,83,80,0.3); }
      .jai-source-dot.negative::after { background: #EF5350; }
      .jai-source-dot .jai-popup { top: 50%; transform: translateY(-50%) translateX(4px); right: 100%; margin-right: 8px; max-height: 150px; overflow-y: auto; }
      .jai-issue { display: flex; align-items: flex-start; gap: 8px; padding: 10px 12px; background: #2A2A2A; border: 1px solid #3A3A3A; border-radius: 8px; margin-bottom: 6px; font-size: 13px; color: #FF8A80; line-height: 1.45; }
      .jai-issue svg { width: 16px; height: 16px; min-width: 16px; color: #FF8A80; margin-top: 1px; }
      .jai-consent-btn { width: 100%; padding: 12px 16px; background: #4686ec; color: #FFFFFF; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s ease; margin-bottom: 20px; }
      .jai-consent-btn:hover { background: #5A9AFF; }
      .jai-consent-btn:disabled { background: #2A2A2A; cursor: not-allowed; }
      .jai-consent-btn.sent { background: #606060; }
      .jai-placeholder { font-size: 13px; color: #606060; font-style: italic; padding: 8px 0; }
    `;
    document.head.appendChild(style);
  }

  const icons = {
    people: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    feedback: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
  };

  function popupList(items) {
    if (!items || items.length === 0) {
      return '<div class="jai-popup"><div class="jai-popup-item jai-placeholder">No data yet</div></div>';
    }
    return `<div class="jai-popup">${items.map(i => `<div class="jai-popup-item">${i}</div>`).join('')}</div>`;
  }

  function getThemeType(label) {
    const positiveKeywords = ['positive', 'good', 'great', 'clear', 'excellent', 'helpful'];
    const negativeKeywords = ['confusion', 'confused', 'difficult', 'hard', 'fast', 'slow', 'needs', 'lack', 'missing', 'unclear', ' kulang', ' hirap', 'di ko'];
    const lowerLabel = (label || '').toLowerCase();
    if (positiveKeywords.some(kw => lowerLabel.includes(kw))) return 'positive';
    if (negativeKeywords.some(kw => lowerLabel.includes(kw))) return 'negative';
    return '';
  }

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

  function refreshParticipantsBadge() {
    if (!window.DatabaseService) {
      console.warn('[FA:UI] DatabaseService not available');
      return;
    }
    DatabaseService.getConsentedParticipants((names) => {
      const badge = document.getElementById('jai-participants-badge');
      if (!badge) return;
      const countEl = badge.querySelector('.jai-count-num');
      const popupEl = badge.querySelector('.jai-popup');
      if (countEl) countEl.textContent = names.length;
      if (popupEl) {
        popupEl.innerHTML = names.length
          ? names.map(n => `<div class="jai-popup-item">${n}</div>`).join('')
          : '<div class="jai-popup-item jai-placeholder">No consented participants yet</div>';
      }
    });
  }

  function refreshFeedbacksBadge() {
    if (!window.DatabaseService) {
      console.warn('[FA:UI] DatabaseService not available');
      return;
    }
    DatabaseService.getFeedbacks((feedbacks) => {
      const badge = document.getElementById('jai-feedbacks-badge');
      if (!badge) return;
      const countEl = badge.querySelector('.jai-count-num');
      const popupEl = badge.querySelector('.jai-popup');
      if (countEl) countEl.textContent = feedbacks.length;
      if (popupEl) {
        popupEl.innerHTML = feedbacks.length
          ? feedbacks.map(f => `<div class="jai-popup-item">${f.text}</div>`).join('')
          : '<div class="jai-popup-item jai-placeholder">No feedbacks collected yet</div>';
      }
    });
  }

  function createSidebar() {
    if (document.getElementById(sidebarId)) return;
    injectStyles();

    mainContainer = document.querySelector('[role="main"]');
    if (mainContainer) mainContainer.style.setProperty('margin-right', '350px', 'important');

    sidebar = document.createElement('div');
    sidebar.id = sidebarId;

    const themesPlaceholder = `<div class="jai-placeholder">Themes will appear here once AI analysis is connected.</div>`;
    const recommendationsPlaceholder = `<div class="jai-placeholder">Recommendations will appear here once AI analysis is connected.</div>`;

    sidebar.innerHTML = `
      <div class="jai-header">
        <span class="jai-header-title">Feedback Analyzer</span>
        <button class="jai-close-btn" id="jai-close" title="Close sidebar">✕</button>
      </div>
      <div class="jai-content">
        <div class="jai-counts">
          <div id="jai-participants-badge" class="jai-count-badge jai-popup-trigger">
            ${icons.people}
            <span class="jai-count-num">0</span> Participants
            <div class="jai-popup"><div class="jai-popup-item jai-placeholder">No consented participants yet</div></div>
          </div>
          <div id="jai-feedbacks-badge" class="jai-count-badge jai-popup-trigger">
            ${icons.feedback}
            <span class="jai-count-num">0</span> Feedbacks
            <div class="jai-popup"><div class="jai-popup-item jai-placeholder">No feedbacks collected yet</div></div>
          </div>
        </div>
        <button id="sendConsentBtn" class="jai-consent-btn ${consentPollSent ? 'sent' : ''}">
          ${consentPollSent ? 'Consent Poll Sent' : 'Send Consent Notice'}
        </button>
        <div class="jai-section">
          <div class="jai-section-title">Feedback Themes</div>
          <div id="jai-themes-content">${themesPlaceholder}</div>
        </div>
        <div class="jai-section">
          <div class="jai-section-title">Teaching Strategy Recommendations</div>
          <div id="jai-strategies-content">${recommendationsPlaceholder}</div>
        </div>
      </div>
    `;

    document.body.appendChild(sidebar);
    sidebarVisible = true;
    refreshParticipantsBadge();
    refreshFeedbacksBadge();
    setupPopupHover();

    if (window.DatabaseService && typeof DatabaseService.getSession === 'function') {
      DatabaseService.getSession((session) => {
        if (session && session.consentPollSent) {
          consentPollSent = true;
          updateConsentButton(true);
        } else {
          updateConsentButton(false);
        }
      });
    }

    const closeBtn = document.getElementById('jai-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        sidebar.style.animation = 'none';
        sidebar.style.transform = 'translateX(100%)';
        sidebar.style.transition = 'transform 0.2s ease';
        setTimeout(() => sidebar.remove(), 200);
        sidebarVisible = false;
        if (mainContainer) mainContainer.style.marginRight = '';
      });
    }

    const consentBtn = document.getElementById('sendConsentBtn');
    if (consentBtn) {
      consentBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!consentPollSent) createConsentPoll();
      });
    }
  }

  function removeSidebar() {
    const el = document.getElementById(sidebarId);
    if (el) { el.remove(); sidebarVisible = false; }
    if (mainContainer) { mainContainer.style.marginRight = ''; mainContainer = null; }
  }

  function createConsentPoll() {
    const pollQuestion = 'Do you consent to the collection of your name and chat messages in this meeting for AI-powered feedback analysis during this session?';
    const pollOptions = ['Yes, I consent', "No, I don't consent"];
    const pollId = 'consent-' + Date.now();

    const chatButton = document.querySelector('#new-toolbox > div > div > div > div:nth-child(4)');
    if (!chatButton) { _finishConsentPollSetup(pollId); return; }
    chatButton.click();

    setTimeout(() => {
      let pollsTab = document.querySelector('#polls-tab') || document.querySelector('#new-toolbox > div > div > div > div:nth-child(4) > div > div > div');
      if (!pollsTab) { _finishConsentPollSetup(pollId); return; }
      pollsTab.click();

      setTimeout(() => {
        const createPollButton = document.querySelector('button[aria-label="Create a poll"]');
        if (!createPollButton) { _finishConsentPollSetup(pollId); return; }
        createPollButton.click();

        setTimeout(() => {
          fillPollDialog(pollQuestion, pollOptions);
          setTimeout(() => {
            const sendButton = document.querySelector('button[aria-label="Send poll"]');
            if (sendButton) {
              sendButton.click();
              console.log('[FA] Consent poll broadcasted');
            }
            setTimeout(() => {
              const skipButton = document.querySelector('button[aria-label="Skip"]') ||
                Array.from(document.querySelectorAll('button')).find(btn => btn.textContent.trim().toLowerCase() === 'skip');
              if (skipButton) skipButton.click();
              _finishConsentPollSetup(pollId);
            }, 1500);
          }, 500);
        }, 300);
      }, 500);
    }, 500);
  }

  function _finishConsentPollSetup(pollId) {
    consentPollSent = true;
    if (window.DatabaseService && typeof DatabaseService.markConsentPollSent === 'function') {
      DatabaseService.markConsentPollSent(pollId, () => {
        updateConsentButton(true);
        if (typeof startPollObserver === 'function') startPollObserver();
        if (typeof startChatObserver === 'function') startChatObserver();
      });
    } else {
      updateConsentButton(true);
      if (typeof startPollObserver === 'function') startPollObserver();
      if (typeof startChatObserver === 'function') startChatObserver();
    }
  }

  function fillPollDialog(question, options) {
    const questionInput = document.querySelector('#polls-create-input');
    const option1Input = document.querySelector('#polls-answer-input-0');
    const option2Input = document.querySelector('#polls-answer-input-1');
    const submitButton = document.querySelector('button[aria-label="Save"]');

    if (questionInput) {
      questionInput.value = question;
      questionInput.dispatchEvent(new Event('input', { bubbles: true }));
      questionInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
    if (option1Input) {
      option1Input.value = options[0];
      option1Input.dispatchEvent(new Event('input', { bubbles: true }));
    }
    if (option2Input) {
      option2Input.value = options[1];
      option2Input.dispatchEvent(new Event('input', { bubbles: true }));
    }
    if (submitButton) submitButton.click();
  }

  function updateConsentButton(sent = true) {
    const consentBtn = document.getElementById('sendConsentBtn');
    if (consentBtn) {
      if (sent) { consentBtn.textContent = 'Consent Poll Sent'; consentBtn.classList.add('sent'); }
      else { consentBtn.textContent = 'Send Consent Notice'; consentBtn.classList.remove('sent'); }
    }
  }

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
      <div style=\"width: 48px; height: 48px; display: flex; align-items: center; justify-content: center; border-radius: inherit; overflow: hidden;\">
        <img src=\"${chrome.runtime.getURL('icon64.png')}\" style=\"width: 100%; height: 100%; object-fit: cover; display: block; border-radius: inherit;\" aria-hidden=\"true\" />
      </div>
    `;
    // use namespace toggleSidebar
    jitsiToggleBtn.addEventListener('click', () => { if (window.FA_UI && window.FA_UI.toggleSidebar) window.FA_UI.toggleSidebar(); });
    jitsiToggleBtn.addEventListener('mouseenter', () => { jitsiToggleBtn.style.background = 'rgba(0,0,0,0.1)'; });
    jitsiToggleBtn.addEventListener('mouseleave', () => { jitsiToggleBtn.style.background = ''; });
    toolbar.appendChild(jitsiToggleBtn);
  }

  function removeJitsiToggleButton() {
    if (jitsiToggleBtn) { jitsiToggleBtn.remove(); jitsiToggleBtn = null; }
    removeSidebar();
  }

  function toggleSidebar() {
    if (sidebarVisible) removeSidebar();
    else createSidebar();
  }

  function setConsentSent(val) {
    consentPollSent = !!val;
  }

  // Expose API
  window.FA_UI.injectStyles = injectStyles;
  window.FA_UI.createSidebar = createSidebar;
  window.FA_UI.removeSidebar = removeSidebar;
  window.FA_UI.createConsentPoll = createConsentPoll;
  window.FA_UI.injectJitsiToggleButton = injectJitsiToggleButton;
  window.FA_UI.removeJitsiToggleButton = removeJitsiToggleButton;
  window.FA_UI.toggleSidebar = toggleSidebar;
  window.FA_UI.refreshParticipantsBadge = refreshParticipantsBadge;
  window.FA_UI.refreshFeedbacksBadge = refreshFeedbacksBadge;
  window.FA_UI.updateConsentButton = updateConsentButton;
  window.FA_UI.popupList = popupList;
  window.FA_UI.getThemeType = getThemeType;
  window.FA_UI.setupPopupHover = setupPopupHover;
  window.FA_UI.setConsentSent = setConsentSent;

})();
