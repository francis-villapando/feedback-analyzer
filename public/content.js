let isEnabled = false;
let selectedCourse = null;
let selectedCourseName = null;
let selectedTopic = null;

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
  startSession(meetLink, courseId, topicId, callback) {
    fetch('http://localhost:8000/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        meet_link: meetLink,
        course_id: courseId,
        topic_id: topicId
      })
    })
    .then(res => res.json())
    .then(data => {
      const session = {
        id: data.session_id,
        meetLink: meetLink,
        course: courseId,
        topic: topicId,
        startedAt: Date.now(),
        consentPollSent: false,
        consentPollId: null,
        consents: {},
        feedbacks: [],
      };
      this._save(session, () => {
        console.log('[FA:DB] Session started with server ID:', session.id);
        if (callback) callback(session);
      });
    })
    .catch(err => {
      console.error('[FA:DB] Failed to create session on server:', err);
    });
  },

  /** Ends the current session on the server. */
  endSession(callback) {
    this._load((session) => {
      if (!session || !session.id) {
        console.log('[FA:DB] No active session to end');
        if (callback) callback();
        return;
      }

      // Call server to delete all session data
      fetch(`http://localhost:8000/sessions/${session.id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      })
      .then(res => res.json())
      .then(data => {
        console.log('[FA:DB] Session data deletion result:', data);
        if (callback) callback();
      })
      .catch(err => {
        console.error('[FA:DB] Failed to delete session data:', err);
        if (callback) callback();
      });
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
      if (previousVote === response) return;

      participantVotes[participantName] = response;

      if (response === 'yes') {
        fetch('http://localhost:8000/poll-responses', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: session.id,
            participant_name: participantName,
            poll_question: 'Do you consent to data collection?',
            poll_answer: response
          })
        }).then(res => res.json()).catch(() => {});

        fetch('http://localhost:8000/consents', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: session.id, participant_name: participantName, consent_given: true })
        }).then(res => res.json()).catch(() => {});

        session.consents[participantName] = 'yes';
        this._save(session, () => { if (callback) callback(session); });
      } else if (response === 'no' || response === 'multiple') {
        if (session.consents[participantName]) {
          delete session.consents[participantName];
          this._save(session, () => { if (callback) callback(session); });
        } else {
          if (callback) callback(session);
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
      const names = Object.entries(session.consents).filter(([, v]) => v === 'yes').map(([k]) => k);
      callback(names);
    });
  },

  /** Saves a chat message as feedback for a consented participant. */
  saveFeedback(sender, text, callback) {
    this._load((session) => {
      if (!session) return;
      if (!session.consents || session.consents[sender] !== 'yes') { if (callback) callback(session); return; }
      const entry = { sender, text, timestamp: Date.now() };
      session.feedbacks.push(entry);
      fetch('http://localhost:8000/feedback', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: session.id, participant_id: sender, message: text }) })
        .then(res => res.json()).catch(() => {});
      this._save(session, () => { if (callback) callback(session); });
    });
  },

  /** Retrieves all feedback entries for the current session. */
  getFeedbacks(callback) {
    this._load((session) => { if (!session) { callback([]); return; } callback(session.feedbacks || []); });
  },
};

// Poll processing selectors and logic
const POLL_SELECTORS = {
  pollContainer: 'div.css-8h8cwl-container',
  resultList:    'ul.css-1y07j3x-resultList',
  answerRow:     'ul.css-1y07j3x-resultList > li',
  answerLabel:   'div.css-sf4n65-answerName',
};

function startPollObserver() {
  if (pollObserver) return;
  pollObserver = new MutationObserver(() => _processPollResults());
  pollObserver.observe(document.body, { childList: true, subtree: true });
  _processPollResults();
}

function stopPollObserver() { if (pollObserver) { pollObserver.disconnect(); pollObserver = null; } }

function _processPollResults() {
  const currentPollState = {};
  const pollCard = document.querySelector(POLL_SELECTORS.pollContainer);
  if (pollCard && !pollCard.dataset.detailsClicked) {
    const showDetailsBtn = Array.from(pollCard.querySelectorAll('button')).find(btn => btn.textContent.trim().toLowerCase() === 'show details');
    if (showDetailsBtn) { pollCard.dataset.detailsClicked = 'true'; showDetailsBtn.click(); return; }
  }

  const answerRows = document.querySelectorAll(POLL_SELECTORS.answerRow);
  if (answerRows.length === 0) return;

  answerRows.forEach((row) => {
    const labelEl = row.querySelector(POLL_SELECTORS.answerLabel);
    const labelText = labelEl ? labelEl.textContent.trim().toLowerCase() : '';
    let response = null;
    if (labelText.startsWith('yes')) response = 'yes'; else if (labelText.startsWith('no')) response = 'no';
    if (!response) return;

    const candidateVoters = Array.from(row.querySelectorAll('div, span, li')).filter(el => {
      const text = el.textContent.trim();
      return text.length > 0 && text.length < 60 && !text.toLowerCase().includes('consent') && !text.toLowerCase().includes("don't") && !text.match(/^\d+\s*\([\d.]+%\)$/);
    });

    if (candidateVoters.length === 0) return;
    candidateVoters.forEach((voterEl) => {
      const name = voterEl.textContent.trim();
      if (!name) return;
      if (currentPollState[name]) currentPollState[name] = 'multiple'; else currentPollState[name] = response;
    });
  });

  const stateChanged = JSON.stringify(currentPollState) !== JSON.stringify(lastProcessedPollState);
  if (!stateChanged && lastProcessedPollState) return;
  lastProcessedPollState = currentPollState;

  Object.entries(currentPollState).forEach(([name, vote]) => {
    if (vote === 'multiple') DatabaseService.saveConsent(name, 'multiple', () => { if (window.FA_UI && window.FA_UI.refreshParticipantsBadge) window.FA_UI.refreshParticipantsBadge(); });
    else if (vote === 'yes') DatabaseService.saveConsent(name, 'yes', () => { if (window.FA_UI && window.FA_UI.refreshParticipantsBadge) window.FA_UI.refreshParticipantsBadge(); });
    else if (vote === 'no') DatabaseService.saveConsent(name, 'no', () => { if (window.FA_UI && window.FA_UI.refreshParticipantsBadge) window.FA_UI.refreshParticipantsBadge(); });
  });
}

// Chat processing selectors and logic
const CHAT_SELECTORS = {
  conversationContainer: '#chatconversation',
  messageGroup: '.chat-message-group, .css-ks74nz-messageGroup',
  senderName: '.css-vpkttz-displayName',
  messageText: '.css-sufr58-userMessage > p',
};

const _processedMessages = new WeakSet();

function startChatObserver() {
  if (chatObserver) return;
  const observeTarget = document.querySelector(CHAT_SELECTORS.conversationContainer) || document.querySelector('#new-toolbox') || document.body;
  chatObserver = new MutationObserver(() => _processChatMessages());
  chatObserver.observe(observeTarget, { childList: true, subtree: true });
  _processChatMessages();
}

function stopChatObserver() { if (chatObserver) { chatObserver.disconnect(); chatObserver = null; } }

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
    const srSpan = bodyClone.querySelector('.sr-only'); if (srSpan) srSpan.remove();
    const messageText = bodyClone.textContent.trim();

    if (senderName && messageText) {
      DatabaseService.hasConsented(senderName, (consented) => {
        if (consented) DatabaseService.saveFeedback(senderName, messageText, () => { if (window.FA_UI && window.FA_UI.refreshFeedbacksBadge) window.FA_UI.refreshFeedbacksBadge(); });
      });
    }
  });
}

// Helpers
function stopObservers() { stopPollObserver(); stopChatObserver(); }

function isMeetingActive() {
  const hasToolbox = !!document.querySelector('.toolbox-content-items');
  const hasPrejoin = !!document.querySelector('[data-testid="prejoin.joinMeeting"]');
  const hasLogin = !!document.querySelector('[data-testid="lobby.loginButton"]');
  return hasToolbox && !hasPrejoin && !hasLogin;
}

// Message interface with popup
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'toggleMaster') {
    const meetingActive = isMeetingActive();
    if (!meetingActive) { sendResponse({ success: false, isEnabled, isMeetingActive: false }); return true; }
    selectedCourse = msg.course || null;
    selectedCourseName = msg.courseName || null;
    selectedTopic = msg.topic || null;
    isEnabled = !isEnabled;
    if (isEnabled) {
      const meetLink = window.location.href;
      DatabaseService.startSession(meetLink, selectedCourse, selectedTopic, () => { if (window.FA_UI && window.FA_UI.injectJitsiToggleButton) window.FA_UI.injectJitsiToggleButton(); });
    } else {
      DatabaseService.endSession(() => {
        stopObservers();
        if (window.FA_UI && window.FA_UI.removeJitsiToggleButton) window.FA_UI.removeJitsiToggleButton();
        if (window.FA_UI && window.FA_UI.setConsentSent) window.FA_UI.setConsentSent(false);
        DatabaseService.clearSession();
      });
    }
    sendResponse({ success: true, isEnabled, isMeetingActive: true });
    return true;
  }
  if (msg.action === 'getState') {
    sendResponse({ isEnabled, isMeetingActive: isMeetingActive(), selectedCourse, selectedCourseName, selectedTopic });
    return true;
  }
  if (msg.action === 'meetingEnded') {
    chrome.storage.local.remove(['courseSelection']);
    isEnabled = false;
    sendResponse({ success: true });
    return true;
  }
  if (msg.action === 'extensionDisabled') {
    DatabaseService.endSession(() => {
      chrome.storage.local.remove(['courseSelection']);
      isEnabled = false;
      console.log('Extension disabled - server data deleted and selections cleared');
    });
    sendResponse({ success: true });
    return true;
  }
  return true;
});

// Detect meeting end and notify popup to clear selections
let previousMeetingState = isMeetingActive();
let previousUrl = window.location.href;
setInterval(() => {
  const currentMeetingState = isMeetingActive();
  const currentUrl = window.location.href;
  if ((previousMeetingState && !currentMeetingState) || (previousUrl !== currentUrl && !currentUrl.includes('meet.jit.si'))) {
    chrome.storage.local.remove(['courseSelection']);
    DatabaseService.endSession(() => { console.log('Meeting ended - selections cleared and server data deleted'); });
  }
  previousMeetingState = currentMeetingState; previousUrl = currentUrl;
}, 1000);

// Monitor for DOM removal indicating meeting left
const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    if (mutation.type === 'childList') {
      const meetingElements = document.querySelectorAll('.filmstrip, .toolbox-content-items, #largeVideoContainer');
      if (meetingElements.length === 0) {
        chrome.storage.local.remove(['courseSelection']);
        DatabaseService.endSession(() => { console.log('Meeting elements removed - server data deleted'); });
        break;
      }
    }
  }
});

observer.observe(document.body, { childList: true, subtree: true });

window.DatabaseService = DatabaseService;
