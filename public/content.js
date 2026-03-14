let isEnabled = false;
let sidebarVisible = false;
let sidebar = null;
let mainContainer = null;
let jitsiToggleBtn = null;
let selectedCourse = null;
let selectedCourseName = null;
let selectedTopic = null;
const sidebarId = 'jitsi-ai-sidebar';

let consentPollSent = false;
let pollObserver = null;
let chatObserver = null;
let participantVotes = {};
let lastProcessedPollState = null;

const DatabaseService = {
  _load(callback) {
    chrome.storage.local.get(['fa_session'], (result) => {
      callback(result.fa_session || null);
    });
  },

  _save(session, callback) {
    chrome.storage.local.set({ fa_session: session }, callback);
  },

  /** Initializes a new session with course and topic metadata. */
  startSession(course, courseName, topic, callback) {
    const session = {
      id: 'session-' + Date.now(),
      course,
      courseName,
      topic,
      startedAt: Date.now(),
      consentPollSent: false,
      consentPollId: null,
      consents: {},
      feedbacks: [],
    };
    this._save(session, () => {
      console.log('[FA:DB] Session started:', session.id);
      if (callback) callback(session);
    });
  },

  /** Retrieves the active session data. */
  getSession(callback) {
    this._load(callback);
  },

  /** Clears session data from local storage. */
  clearSession(callback) {
    chrome.storage.local.remove(['fa_session'], () => {
      participantVotes = {};
      lastProcessedPollState = null;
      console.log('[FA:DB] Session cleared');
      if (callback) callback();
    });
  },

  /** Marks the consent poll as dispatched. */
  markConsentPollSent(pollId, callback) {
    this._load((session) => {
      if (!session) return;
      session.consentPollSent = true;
      session.consentPollId = pollId;
      this._save(session, () => {
        console.log('[FA:DB] Consent poll marked as sent:', pollId);
        if (callback) callback(session);
      });
    });
  },

  /** Persists a participant's consent response with validation. */
  saveConsent(participantName, response, callback) {
    this._load((session) => {
      if (!session) return;
      
      const previousVote = participantVotes[participantName];
      
      if (previousVote === response) {
        console.log(`[FA:DB] Participant ${participantName} already voted "${response}", ignoring duplicate`);
        return;
      }
      
      participantVotes[participantName] = response;
      
      if (response === 'yes' && previousVote !== 'yes') {
        session.consents[participantName] = 'yes';
        this._save(session, () => {
          console.log(`[FA:DB] Consent recorded for ${participantName}`);
          if (callback) callback(session);
        });
      } else if (response === 'yes' && previousVote === 'yes') {
        console.log(`[FA:DB] Participant ${participantName} already has consent recorded`);
      } else if (response === 'no' || response === 'multiple') {
        // Always call callback to update UI, regardless of whether consent existed
        if (session.consents[participantName]) {
          delete session.consents[participantName];
          this._save(session, () => {
            console.log(`[FA:DB] Consent removed for ${participantName} (voted "${response}")`);
            if (callback) callback(session);
          });
        } else {
          // Even if no consent existed, call callback to update the counter
          this._save(session, () => {
            console.log(`[FA:DB] Participant ${participantName} voted "${response}", not saved as consent`);
            if (callback) callback(session);
          });
        }
      }
    });
  },

  /** Clears vote tracking state. */
  clearVoteTracking() {
    participantVotes = {};
    lastProcessedPollState = null;
    console.log('[FA:DB] Vote tracking cleared');
  },

  /** Checks if a specific participant has granted consent. */
  hasConsented(participantName, callback) {
    this._load((session) => {
      if (!session) { callback(false); return; }
      callback(session.consents[participantName] === 'yes');
    });
  },

  /** Returns an array of all participants who have consented. */
  getConsentedParticipants(callback) {
    this._load((session) => {
      if (!session) { callback([]); return; }
      const names = Object.entries(session.consents)
        .filter(([, v]) => v === 'yes')
        .map(([k]) => k);
      callback(names);
    });
  },

  /** Saves a chat message as feedback for a consented participant. */
  saveFeedback(sender, text, callback) {
    this._load((session) => {
      if (!session) return;
      const entry = { sender, text, timestamp: Date.now() };
      session.feedbacks.push(entry);
      this._save(session, () => {
        console.log(`[FA:DB] Feedback saved from ${sender}:`, text);
        if (callback) callback(session);
      });
    });
  },

  /** Retrieves all feedback entries for the current session. */
  getFeedbacks(callback) {
    this._load((session) => {
      if (!session) { callback([]); return; }
      callback(session.feedbacks || []);
    });
  },
};

// UI Components and Styles
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
    .jai-placeholder { font-size: 13px; color: #9E9E9E; font-style: italic; padding: 8px 0; }
  `;
  document.head.appendChild(style);
}

const icons = {
  people: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
  feedback: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
  warn: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
};

/** Utility to generate a popup list UI from an array. */
function popupList(items) {
  if (!items || items.length === 0) {
    return '<div class="jai-popup"><div class="jai-popup-item jai-placeholder">No data yet</div></div>';
  }
  return `<div class="jai-popup">${items.map(i => `<div class="jai-popup-item">${i}</div>`).join('')}</div>`;
}

/** Classifies theme types for styling. Future integration point for NLP models. */
function getThemeType(label) {
  const positiveKeywords = ['positive', 'good', 'great', 'clear', 'excellent', 'helpful'];
  const negativeKeywords = ['confusion', 'confused', 'difficult', 'hard', 'fast', 'slow', 'needs', 'lack', 'missing', 'unclear', ' kulang', ' hirap', 'di ko'];
  const lowerLabel = label.toLowerCase();
  if (positiveKeywords.some(kw => lowerLabel.includes(kw))) return 'positive';
  if (negativeKeywords.some(kw => lowerLabel.includes(kw))) return 'negative';
  return '';
}

/** Manages mouse events for sidebar popup triggers. */
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

/** Updates the participant count badge and its associated popup list. */
function refreshParticipantsBadge() {
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

/** Updates the feedback count badge and its associated popup list. */
function refreshFeedbacksBadge() {
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

/** Creates and displays the analyzer sidebar in the Jitsi interface. */
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
        ${themesPlaceholder}
      </div>
      <div class="jai-section">
        <div class="jai-section-title">Teaching Strategy Recommendations</div>
        ${recommendationsPlaceholder}
      </div>
    </div>
  `;

  document.body.appendChild(sidebar);
  sidebarVisible = true;
  refreshParticipantsBadge();
  refreshFeedbacksBadge();
  setupPopupHover();

  DatabaseService.getSession((session) => {
    if (session && session.consentPollSent) {
      consentPollSent = true;
      updateConsentButton(true);
    } else {
      updateConsentButton(false);
    }
  });

  document.getElementById('jai-close').addEventListener('click', () => {
    sidebar.style.animation = 'none';
    sidebar.style.transform = 'translateX(100%)';
    sidebar.style.transition = 'transform 0.2s ease';
    setTimeout(() => sidebar.remove(), 200);
    sidebarVisible = false;
    if (mainContainer) mainContainer.style.marginRight = '';
  });

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

/** Automates the creation of a consent poll using Jitsi's UI. */
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
  DatabaseService.markConsentPollSent(pollId, () => {
    updateConsentButton(true);
    startPollObserver();
    startChatObserver();
  });
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

const POLL_SELECTORS = {
  pollContainer: 'div.css-8h8cwl-container',       // Outer poll card (stays in DOM after Skip)
  resultList:    'ul.css-1y07j3x-resultList',       // Results list container
  answerRow:     'ul.css-1y07j3x-resultList > li',  // Each answer result row (plain li)
  answerLabel:   'div.css-sf4n65-answerName',        // Answer text label inside each row
};

function startPollObserver() {
  if (pollObserver) return;
  pollObserver = new MutationObserver(() => _processPollResults());
  pollObserver.observe(document.body, { childList: true, subtree: true });
  console.log('[FA] Poll observer started on document.body');
  _processPollResults();
}

function stopPollObserver() {
  if (pollObserver) { pollObserver.disconnect(); pollObserver = null; }
}

function _processPollResults() {
  const currentPollState = {};
  const pollCard = document.querySelector(POLL_SELECTORS.pollContainer);
  if (pollCard && !pollCard.dataset.detailsClicked) {
    const showDetailsBtn = Array.from(pollCard.querySelectorAll('button')).find(
      btn => btn.textContent.trim().toLowerCase() === 'show details'
    );
    if (showDetailsBtn) {
      console.log('[FA:POLL] Found "Show details" button, clicking to reveal names hidden by Jitsi...');
      pollCard.dataset.detailsClicked = 'true';
      showDetailsBtn.click();
      return;
    }
  }

  const answerRows = document.querySelectorAll(POLL_SELECTORS.answerRow);
  if (answerRows.length === 0) {
    if (pollCard) console.log('[FA:POLL] Poll card visible but no result rows found yet');
    return;
  }

  // Build current poll state from DOM
  answerRows.forEach((row) => {
    const labelEl = row.querySelector(POLL_SELECTORS.answerLabel);
    const labelText = labelEl ? labelEl.textContent.trim().toLowerCase() : '';

    let response = null;
    if (labelText.startsWith('yes')) response = 'yes';
    else if (labelText.startsWith('no')) response = 'no';
    if (!response) return;

    // Collect voter names from any div/span/li children that aren't the answer label or count.
    const candidateVoters = Array.from(row.querySelectorAll('div, span, li'))
      .filter(el => {
        const text = el.textContent.trim();
        return text.length > 0 && text.length < 60
          && !text.toLowerCase().includes('consent')
          && !text.toLowerCase().includes("don't")
          && !text.match(/^\d+\s*\([\d.]+%\)$/);
      });

    if (candidateVoters.length === 0) {
      console.log(`[FA:POLL] "${labelText}" — no voter names yet`);
      return;
    }

    candidateVoters.forEach((voterEl) => {
      const name = voterEl.textContent.trim();
      if (!name) return;
      if (currentPollState[name]) {
        currentPollState[name] = 'multiple';
      } else {
        currentPollState[name] = response;
      }
    });
  });

  // Check if poll state changed since last processing
  const stateChanged = JSON.stringify(currentPollState) !== JSON.stringify(lastProcessedPollState);
  if (!stateChanged && lastProcessedPollState) {
    return;
  }
  lastProcessedPollState = currentPollState;

  // Process each participant's current vote state
  Object.entries(currentPollState).forEach(([name, vote]) => {
    if (vote === 'multiple') {
      console.log(`[FA:POLL] Participant ${name} voted multiple options, NOT counting as consent`);
      DatabaseService.saveConsent(name, 'multiple', () => refreshParticipantsBadge());
    } else if (vote === 'yes') {
      DatabaseService.saveConsent(name, 'yes', () => refreshParticipantsBadge());
    } else if (vote === 'no') {
      DatabaseService.saveConsent(name, 'no', () => refreshParticipantsBadge());
    }
  });
}

const CHAT_SELECTORS = {
  conversationContainer: '#chatconversation',
  messageGroup: '.chat-message-group, .css-ks74nz-messageGroup', // The overall group for consecutive messages
  senderName: '.css-vpkttz-displayName',           // The sender's name (only appears in the first message of a group)
  messageText: '.css-sufr58-userMessage > p',      // Individual message nodes
};

const _processedMessages = new WeakSet();

function startChatObserver() {
  if (chatObserver) return;
  const observeTarget = document.querySelector(CHAT_SELECTORS.conversationContainer) || document.querySelector('#new-toolbox') || document.body;
  chatObserver = new MutationObserver(() => _processChatMessages());
  chatObserver.observe(observeTarget, { childList: true, subtree: true });
  _processChatMessages();
}

function stopChatObserver() {
  if (chatObserver) { chatObserver.disconnect(); chatObserver = null; }
}

function _processChatMessages() {
  document.querySelectorAll(CHAT_SELECTORS.messageText).forEach((pEl) => {
    if (_processedMessages.has(pEl)) return;
    _processedMessages.add(pEl);

    const msgGroup = pEl.closest(CHAT_SELECTORS.messageGroup);
    if (!msgGroup) return;

    const senderEl = msgGroup.querySelector(CHAT_SELECTORS.senderName);
    if (!senderEl) return;

    const senderName = senderEl.textContent.trim();
    
    const bodyClone = pEl.cloneNode(true);
    const srSpan = bodyClone.querySelector('.sr-only');
    if (srSpan) srSpan.remove();
    
    const messageText = bodyClone.textContent.trim();

    if (senderName && messageText) {
      DatabaseService.hasConsented(senderName, (consented) => {
        if (consented) DatabaseService.saveFeedback(senderName, messageText, () => refreshFeedbacksBadge());
      });
    }
  });
}

// Toolbar and Lifecycle
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
}

function removeJitsiToggleButton() {
  if (jitsiToggleBtn) { jitsiToggleBtn.remove(); jitsiToggleBtn = null; }
  removeSidebar();
}

function toggleSidebar() {
  if (sidebarVisible) removeSidebar();
  else createSidebar();
}

function stopObservers() {
  stopPollObserver();
  stopChatObserver();
}

function isMeetingActive() {
  const hasToolbox = !!document.querySelector('.toolbox-content-items');
  const hasPrejoin = !!document.querySelector('[data-testid="prejoin.joinMeeting"]');
  const hasLogin = !!document.querySelector('[data-testid="lobby.loginButton"]');
  return hasToolbox && !hasPrejoin && !hasLogin;
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'toggleMaster') {
    const meetingActive = isMeetingActive();
    if (!meetingActive) { sendResponse({ success: false, isEnabled, isMeetingActive: false }); return true; }
    selectedCourse = msg.course || null;
    selectedCourseName = msg.courseName || null;
    selectedTopic = msg.topic || null;
    isEnabled = !isEnabled;
    if (isEnabled) DatabaseService.startSession(selectedCourse, selectedCourseName, selectedTopic, () => injectJitsiToggleButton());
    else { stopObservers(); removeJitsiToggleButton(); consentPollSent = false; DatabaseService.clearSession(); }
    sendResponse({ success: true, isEnabled, isMeetingActive: true });
    return true;
  }
  if (msg.action === 'getState') {
    sendResponse({ isEnabled, isMeetingActive: isMeetingActive(), selectedCourse, selectedCourseName, selectedTopic });
    return true;
  }
  if (msg.action === 'meetingEnded') {
    // Clear selections when meeting ends
    chrome.storage.local.remove(['courseSelection']);
    isEnabled = false;
    sendResponse({ success: true });
    return true;
  }
  return true;
});

// Detect meeting end and notify popup to clear selections
let previousMeetingState = isMeetingActive();
setInterval(() => {
  const currentMeetingState = isMeetingActive();
  if (previousMeetingState && !currentMeetingState) {
    // Meeting ended - clear selections
    chrome.storage.local.remove(['courseSelection']);
    console.log('Meeting ended - selections cleared');
  }
  previousMeetingState = currentMeetingState;
}, 1000);
