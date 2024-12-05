// background.js

// A simple event listener that listens for a message from the content script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("Message received from content script:", message);
  
    if (message.action === 'get_data') {
      // Respond with some data (could be fetched from storage, etc.)
      sendResponse({ data: "Here's some data from background.js" });
    }
  
    return true;  // To indicate async response
  });
  
  // Handle browser action click event
  chrome.browserAction.onClicked.addListener((tab) => {
    // Send a message to the content script or perform other actions
    chrome.tabs.sendMessage(tab.id, { action: 'toggle_feature' }, (response) => {
      console.log('Response from content script:', response);
    });
  });
  
  // A simple example of using storage to persist data in the background
  chrome.runtime.onInstalled.addListener(() => {
    console.log("Extension installed!");
  
    // Initialize some settings in local storage
    chrome.storage.local.set({ featureEnabled: true }, () => {
      console.log("Feature enabled status initialized.");
    });
  });
  
  // An example of interacting with browser storage when some event happens
  chrome.storage.local.get('featureEnabled', (result) => {
    if (result.featureEnabled) {
      console.log("Feature is enabled.");
    } else {
      console.log("Feature is disabled.");
    }
  });
  