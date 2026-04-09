// State variables
let isEnabled = false;
let isMeetingActive = false;
let selectedCourse = null;
let selectedCourseName = null;
let selectedTopic = null;
let courseTopics = {};
let currentMeetingUrl = null;

// DOM Elements
const courseSelect = document.getElementById('courseSelect');
const topicSelect = document.getElementById('topicSelect');
const masterToggle = document.getElementById('masterToggle');
const status = document.getElementById('status');

// UI helpers

function setDisabledUI(message) {
  masterToggle.disabled = true;
  masterToggle.classList.remove('active');
  masterToggle.textContent = 'Enable Analyzer';
  status.textContent = message;
  status.classList.add('warning');
  status.classList.remove('active');
  
  // Disable dropdowns
  courseSelect.disabled = true;
  topicSelect.disabled = true;
  courseSelect.classList.remove('enabled');
  topicSelect.classList.remove('enabled');
}

function lockDropdowns() {
  courseSelect.disabled = true;
  topicSelect.disabled = true;
  courseSelect.classList.remove('enabled');
  topicSelect.classList.remove('enabled');
}

function unlockDropdowns() {
  courseSelect.disabled = false;
  courseSelect.classList.add('enabled');
  if (selectedCourse) {
    topicSelect.disabled = false;
    topicSelect.classList.add('enabled');
  }
}

function setMeetingInactiveUI() {
  masterToggle.disabled = true;
  masterToggle.classList.remove('active');
  masterToggle.textContent = 'Enable Analyzer';
  status.textContent = 'Please join a meeting first';
  status.classList.add('warning');
  status.classList.remove('active');
  
  // Disable dropdowns when not in meeting
  courseSelect.disabled = true;
  topicSelect.disabled = true;
  courseSelect.classList.remove('enabled');
  topicSelect.classList.remove('enabled');
}

function setMeetingActiveUI() {
  status.classList.remove('warning');
  
  // Enable course dropdown when in meeting
  courseSelect.disabled = false;
  courseSelect.classList.add('enabled');
  
  // Update toggle state based on selections
  updateToggleState();
  
  if (isEnabled) {
    masterToggle.classList.add('active');
    masterToggle.classList.remove('enabled');
    masterToggle.textContent = 'Disable Analyzer';
    // Lock dropdowns when analyzer is enabled
    lockDropdowns();
    status.textContent = 'Analyzer is active';
    status.classList.add('active');
  } else {
    masterToggle.classList.remove('active');
    if (selectedCourse && selectedTopic) {
      masterToggle.classList.add('enabled');
      masterToggle.textContent = 'Enable Analyzer';
      // Unlock dropdowns when analyzer is disabled
      unlockDropdowns();
      status.textContent = 'Analyzer is disabled';
      status.classList.remove('active');
    } else if (selectedCourse) {
      masterToggle.classList.remove('enabled');
      masterToggle.textContent = 'Enable Analyzer';
      unlockDropdowns();
      status.textContent = 'Please select a topic';
      status.classList.remove('active');
    } else {
      masterToggle.classList.remove('enabled');
      masterToggle.textContent = 'Enable Analyzer';
      unlockDropdowns();
      status.textContent = 'Please select course & topic first';
      status.classList.remove('active');
    }
  }
}

function updateToggleState() {
  // Toggle is enabled only when both course and topic are selected
  if (selectedCourse && selectedTopic) {
    masterToggle.disabled = false;
    if (isEnabled) {
      masterToggle.classList.add('active');
      masterToggle.classList.remove('enabled');
      masterToggle.textContent = 'Disable Analyzer';
    } else {
      masterToggle.classList.remove('active');
      masterToggle.classList.add('enabled');
      masterToggle.textContent = 'Enable Analyzer';
    }
  } else {
    masterToggle.disabled = true;
    masterToggle.classList.remove('active', 'enabled');
    masterToggle.textContent = 'Enable Analyzer';
  }
}

function updateTopicDropdownState() {
  // Topic dropdown is enabled only when a course is selected
  if (selectedCourse) {
    topicSelect.disabled = false;
    topicSelect.classList.add('enabled');
  } else {
    topicSelect.disabled = true;
    topicSelect.classList.remove('enabled');
    // Reset topic when course changes
    topicSelect.value = '';
    selectedTopic = null;
  }
}

// Populate dropdowns

async function populateCourses() {
  console.log('populateCourses called');
  try {
    const response = await fetch('http://localhost:8000/courses');
    console.log('Response status:', response.status);
    const courses = await response.json();
    console.log('Courses data:', courses);
    
    courseSelect.innerHTML = '<option value="">Select a course...</option>';
    
    for (const course of courses) {
      // Store in courseTopics map for lookup by ID
      courseTopics[course.id] = course;
      
      const option = document.createElement('option');
      option.value = course.id;
      option.textContent = course.name;
      courseSelect.appendChild(option);
    }
    console.log('Dropdown populated with', courses.length, 'courses');
    return courses;
  } catch (error) {
    console.error('Error loading courses:', error);
    return [];
  }
}

async function populateTopics(courseId) {
  try {
    const response = await fetch(`http://localhost:8000/courses/${courseId}/topics`);
    const topics = await response.json();
    
    topicSelect.innerHTML = '<option value="">Select a topic...</option>';
    
    for (const topic of topics) {
      const option = document.createElement('option');
      option.value = topic.id;
      option.textContent = topic.name;
      topicSelect.appendChild(option);
    }
    return topics;
  } catch (error) {
    console.error('Error loading topics:', error);
    return [];
  }
}

// Storage functions

function saveSelections(meetingUrl) {
  const selection = {
    course: selectedCourse,
    courseName: selectedCourse ? courseTopics[selectedCourse]?.name || selectedCourseName : null,
    topic: selectedTopic,
    meetingUrl: meetingUrl,
    timestamp: Date.now()
  };
  
  chrome.storage.local.set({ courseSelection: selection });
}

function clearSelections() {
  chrome.storage.local.remove(['courseSelection']);
  selectedCourse = null;
  selectedCourseName = null;
  selectedTopic = null;
}

function loadSelections(meetingUrl, callback) {
  chrome.storage.local.get(['courseSelection'], (result) => {
    if (result.courseSelection) {
      // Verify this is the same meeting URL
      if (result.courseSelection.meetingUrl === meetingUrl) {
        selectedCourse = result.courseSelection.course;
        selectedCourseName = result.courseSelection.courseName;
        selectedTopic = result.courseSelection.topic;
        
        // Restore dropdown values
        if (selectedCourse) {
          courseSelect.value = selectedCourse;
          // Populate topics and then set the selected topic
          populateTopics(selectedCourse).then(() => {
            if (selectedTopic) {
              topicSelect.value = selectedTopic;
            }
            updateTopicDropdownState();
            callback();
          });
          return; // Return early to avoid callback being called twice
        }
        
        updateTopicDropdownState();
      } else {
        // Different meeting URL - clear selections
        clearSelections();
      }
    }
    callback();
  });
}

// Event handlers

function handleCourseChange() {
  selectedCourse = courseSelect.value;
  selectedCourseName = courseTopics[selectedCourse]?.name;
  selectedTopic = null;
  
  // Populate topics based on selected course
  populateTopics(selectedCourse);
  
  // Update topic dropdown state
  updateTopicDropdownState();
  
  // Update toggle state
  updateToggleState();
  
  // Update status message
  if (selectedCourse) {
    status.textContent = 'Please select a topic';
  } else {
    status.textContent = 'Please select course & topic first';
  }
  
  // Save selections
  saveSelections(currentMeetingUrl);
}

function handleTopicChange() {
  selectedTopic = topicSelect.value;
  
  // Update toggle state
  updateToggleState();
  
  // Update status message
  if (selectedTopic) {
    if (isEnabled) {
      masterToggle.classList.add('active');
      masterToggle.classList.remove('enabled');
      masterToggle.textContent = 'Disable Analyzer';
      status.textContent = 'Analyzer is active';
      status.classList.add('active');
    } else {
      masterToggle.classList.remove('active');
      masterToggle.classList.add('enabled');
      masterToggle.textContent = 'Enable Analyzer';
      status.textContent = 'Analyzer is disabled';
      status.classList.remove('active');
    }
  } else {
    status.textContent = 'Please select a topic';
  }
  
  // Save selections
  saveSelections(currentMeetingUrl);
}

// Initialize

async function init() {
  // Populate courses dropdown
  await populateCourses();
  
  // Reset to default placeholder values - will load from storage after verifying meeting
  selectedCourse = null;
  selectedCourseName = null;
  selectedTopic = null;
  courseSelect.value = '';
  topicSelect.value = '';
  updateTopicDropdownState();
  
  // Check current tab and get state
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0] || !tabs[0].url || !tabs[0].url.includes('meet.jit.si')) {
      setDisabledUI('Please open Jitsi Meet first');
      return;
    }
    
    // Store the current meeting URL
    currentMeetingUrl = tabs[0].url;
    
    // Get state from content script
    chrome.tabs.sendMessage(tabs[0].id, { action: "getState" }, (response) => {
        if (chrome.runtime.lastError) {
          console.log('Content script not found or error:', chrome.runtime.lastError);
          setMeetingInactiveUI();
          return;
        }
        
        if (response !== undefined) {
          isEnabled = response.isEnabled;
          isMeetingActive = response.isMeetingActive;
          
          if (isMeetingActive) {
            // Load saved selections for this meeting
            loadSelections(currentMeetingUrl, () => {
              setMeetingActiveUI();
            });
          } else {
            // Clear selections when not in a meeting
            clearSelections();
            setMeetingInactiveUI();
          }
        } else {
          setMeetingInactiveUI();
        }
      });
    });
}

// Event listeners

courseSelect.addEventListener('change', handleCourseChange);
topicSelect.addEventListener('change', handleTopicChange);

// Toggle button click

masterToggle.addEventListener('click', () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (!tabs[0] || !tabs[0].url || !tabs[0].url.includes('meet.jit.si')) {
      setDisabledUI('Please open Jitsi Meet first');
      return;
    }
    
    chrome.tabs.sendMessage(
      tabs[0].id,
      {
        action: "toggleMaster",
        course: selectedCourse,
        courseName: courseTopics[selectedCourse]?.name,
        topic: selectedTopic
      },
      (response) => {
        if (chrome.runtime.lastError) {
          console.log('Error:', chrome.runtime.lastError);
          return;
        }
        if (response) {
          isEnabled = response.isEnabled;
          isMeetingActive = response.isMeetingActive;
          
          // Clear selections if analyzer was disabled (turned off)
          if (!isEnabled) {
            clearSelections();
            courseSelect.value = '';
            topicSelect.value = '';
            updateTopicDropdownState();
          }
          
          setMeetingActiveUI();
        }
      }
    );
  });
});

// Privacy panel toggle

document.getElementById('privacyToggle').addEventListener('click', () => {
  const panel = document.getElementById('privacyPanel');
  const button = document.getElementById('privacyToggle');
  const isOpen = panel.classList.toggle('open');
  button.setAttribute('aria-expanded', isOpen);
});

// Initialize on popup open
init();
