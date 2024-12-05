// Function to generate a random password
function generateRandomPassword(length = 12, includeNumbers = true, includeSpecialChars = true) {
    const letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    const specialChars = '!@#$%^&*()_-+=<>?/,.';
    
    let characterSet = letters; // Default character set (only letters)
    
    if (includeNumbers) {
      characterSet += numbers;
    }
    
    if (includeSpecialChars) {
      characterSet += specialChars;
    }
    
    let password = '';
    
    for (let i = 0; i < length; i++) {
      password += characterSet.charAt(Math.floor(Math.random() * characterSet.length));
    }
    
    return password;
  }
  
  // Function to load the stored password from chrome.storage
  function loadPassword() {
    chrome.storage.local.get('generatedPassword', function(result) {
      if (result.generatedPassword) {
        document.getElementById("password").value = result.generatedPassword;
      }
    });
  }
  
  // Load the password when the popup is opened (or when the extension is reopened)
  loadPassword();
  
  // Listen for click on the "Generate Password" button
  document.getElementById("generate-btn").addEventListener("click", function() {
    const password = generateRandomPassword(); // Generate a random password
    document.getElementById("password").value = password; // Set it in the password field (making it visible)
  
    // Save the generated password to chrome.storage
    chrome.storage.local.set({ 'generatedPassword': password }, function() {
      console.log('Password generated and saved!');
    });
  });
  
  // Listen for click on the "Save" button
  document.getElementById("save-btn").addEventListener("click", function() {
    // Get the values from the input fields
    const webUrl = document.getElementById("web-url").value;
    const password = document.getElementById("password").value;
  
    // Check if both fields have values
    if (webUrl && password) {
      // Send the URL and password to the Flask backend
      fetch('http://localhost:5000/save_password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ web_url: webUrl, password: password })
      })
      .then(response => response.json())
      .then(data => {
        if (data.message === 'Password saved successfully!') {
          alert('Password saved successfully!');
          document.getElementById("web-url").value = '';
          document.getElementById("password").value = '';
        } else {
          alert('Failed to save password: ' + data.message);
        }
      })
      .catch(error => {
        console.error('Error saving password:', error);
        alert('Error saving password!');
      });
    } else {
      alert('Please fill in both fields!');
    }
  });
  