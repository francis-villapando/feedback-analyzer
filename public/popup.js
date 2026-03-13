// Course and topic data structure
const courseTopics = {
  dsa: {
    name: "Data Structures & Algorithms",
    topics: [
      "Arrays", "Linked Lists", "Stacks", "Queues", "Trees",
      "Binary Trees", "Binary Search Trees", "Heaps", "Hash Tables",
      "Graphs", "Sorting Algorithms", "Searching Algorithms",
      "Dynamic Programming", "Recursion", "Big O Notation"
    ]
  },
  gameProgramming: {
    name: "Game Programming",
    topics: [
      "Game Loops", "Physics Engine", "Collision Detection",
      "Sprite Animation", "AI Behavior", "Level Design",
      "Input Handling", "Audio Systems", "Graphics Rendering"
    ]
  },
  networking: {
    name: "Computer Networking",
    topics: [
      "OSI Model", "TCP/IP", "HTTP/HTTPS", "DNS", "Routing",
      "Subnetting", "Firewalls", "VPN", "Wireless Networks",
      "Network Security", "Socket Programming"
    ]
  },
  webDevelopment: {
    name: "Web Development",
    topics: [
      "HTML/CSS", "JavaScript", "DOM Manipulation", "React/Vue/Angular",
      "REST APIs", "Node.js", "Database Integration", "Authentication",
      "Responsive Design", "Web Performance", "SEO"
    ]
  },
  database: {
    name: "Database Systems",
    topics: [
      "SQL Queries", "Database Design", "Normalization", "Indexing",
      "Transactions", "ACID Properties", "NoSQL", "MongoDB",
      "Data Warehousing", "ER Diagrams"
    ]
  },
  operatingSystems: {
    name: "Operating Systems",
    topics: [
      "Process Management", "Memory Management", "CPU Scheduling",
      "File Systems", "Deadlocks", "Synchronization",
      "Virtual Memory", "Paging", "Threading", "I/O Management"
    ]
  }
};

// State variables
let isEnabled = false;
let isMeetingActive = false;
let selectedCourse = null;
let selectedCourseName = null;
let selectedTopic = null;

// DOM Elements
const courseSelect = document.getElementById('courseSelect');
const topicSelect = document.getElementById('topicSelect');
const masterToggle = document.getElementById('masterToggle');
const status = document.getElementById('status');

// UI helpers

function setDisabledUI(message) {
  masterToggle.disabled = true;
  masterToggle.classList.remove('active');
  status.textContent = message;
  status.classList.add('warning');
  status.classList.remove('active');
  
  // Disable dropdowns
  courseSelect.disabled = true;
  topicSelect.disabled = true;
  courseSelect.classList.remove('enabled');
  topicSelect.classList.remove('enabled');
}

function setMeetingInactiveUI() {
  masterToggle.disabled = true;
  masterToggle.classList.remove('active');
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
    status.textContent = 'Analyzer is active';
    status.classList.add('active');
  } else {
    masterToggle.classList.remove('active');
    if (selectedCourse && selectedTopic) {
      status.textContent = 'Analyzer is disabled';
      status.classList.remove('active');
    } else if (selectedCourse) {
      status.textContent = 'Please select a topic';
      status.classList.remove('active');
    } else {
      status.textContent = 'Please select course & topic first';
      status.classList.remove('active');
    }
  }
}

function updateToggleState() {
  // Toggle is enabled only when both course and topic are selected
  if (selectedCourse && selectedTopic) {
    masterToggle.disabled = false;
  } else {
    masterToggle.disabled = true;
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

function populateCourses() {
  // Clear existing options except first
  courseSelect.innerHTML = '<option value="">Select a course...</option>';
  
  for (const [key, value] of Object.entries(courseTopics)) {
    const option = document.createElement('option');
    option.value = key;
    option.textContent = value.name;
    courseSelect.appendChild(option);
  }
}

function populateTopics(courseKey) {
  // Clear existing options except first
  topicSelect.innerHTML = '<option value="">Select a topic...</option>';
  
  if (!courseKey || !courseTopics[courseKey]) {
    return;
  }
  
  const topics = courseTopics[courseKey].topics;
  for (const topic of topics) {
    const option = document.createElement('option');
    option.value = topic;
    option.textContent = topic;
    topicSelect.appendChild(option);
  }
}

// Storage functions

function saveSelections() {
  const selection = {
    course: selectedCourse,
    courseName: selectedCourse ? courseTopics[selectedCourse]?.name || selectedCourseName : null,
    topic: selectedTopic,
    timestamp: Date.now()
  };
  
  chrome.storage.local.set({ courseSelection: selection });
}

function loadSelections(callback) {
  chrome.storage.local.get(['courseSelection'], (result) => {
    if (result.courseSelection) {
      selectedCourse = result.courseSelection.course;
      selectedCourseName = result.courseSelection.courseName;
      selectedTopic = result.courseSelection.topic;
      
      // Restore dropdown values
      if (selectedCourse) {
        courseSelect.value = selectedCourse;
        populateTopics(selectedCourse);
        
        if (selectedTopic) {
          topicSelect.value = selectedTopic;
        }
      }
      
      updateTopicDropdownState();
    }
    callback();
  });
}

// Event handlers

function handleCourseChange() {
  selectedCourse = courseSelect.value;
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
  saveSelections();
}

function handleTopicChange() {
  selectedTopic = topicSelect.value;
  
  // Update toggle state
  updateToggleState();
  
  // Update status message
  if (selectedTopic) {
    if (isEnabled) {
      status.textContent = 'Analyzer is active';
      status.classList.add('active');
    } else {
      status.textContent = 'Analyzer is disabled';
      status.classList.remove('active');
    }
  } else {
    status.textContent = 'Please select a topic';
  }
  
  // Save selections
  saveSelections();
}

// Initialize

function init() {
  // Populate courses dropdown
  populateCourses();
  
  // Reset to default placeholder values - do not restore saved selections
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
    
    // Get state from content script without loading saved selections
    chrome.tabs.sendMessage(tabs[0].id, { action: "getState" }, (response) => {
        if (chrome.runtime.lastError) {
          console.log('Content script not found or error:', chrome.runtime.lastError);
          setMeetingInactiveUI();
          return;
        }
        
        if (response !== undefined) {
          isEnabled = response.isEnabled;
          isMeetingActive = response.isMeetingActive;
          
          // Note: We don't restore course/topic selections from content script
          // The popup always starts with placeholder values
          
          if (isMeetingActive) {
            setMeetingActiveUI();
          } else {
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
