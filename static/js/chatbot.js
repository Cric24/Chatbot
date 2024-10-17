// Function to append messages to the chat box
function appendMessage(sender, message, timestamp) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');

    const contentDiv = document.createElement('div');
    contentDiv.classList.add(sender === 'You' ? 'user-message' : 'bot-response');
    contentDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;

    const timeDiv = document.createElement('div');
    timeDiv.classList.add('timestamp');
    timeDiv.textContent = timestamp;

    messageDiv.appendChild(contentDiv);
    messageDiv.appendChild(timeDiv);
    chatBox.appendChild(messageDiv);

    // Auto-scroll to the bottom
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Function to send a message
function sendMessage() {
    const userInput = document.getElementById('user-input');
    const userMessage = userInput.value.trim();
    if (!userMessage) return;  // Prevent sending empty messages

    const currentTime = new Date().toLocaleString();
    appendMessage('You', userMessage, currentTime);
    userInput.value = '';

    // Show typing indicator
    document.getElementById('typing-indicator').style.display = 'block';

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'message=' + encodeURIComponent(userMessage)
    })
    .then(response => response.json())
    .then(data => {
        // Hide typing indicator
        document.getElementById('typing-indicator').style.display = 'none';

        appendMessage('Bot', data.response, data.timestamp);
    })
    .catch(error => {
        document.getElementById('typing-indicator').style.display = 'none';
        appendMessage('Bot', "Sorry, something went wrong. Please try again.", new Date().toLocaleString());
        console.error('Error:', error);
    });
}

// Function to clear the chat
function clearChat() {
    fetch('/clear', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('chat-box').innerHTML = '';
        alert(data.response);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Handle Enter key to send message
document.getElementById('user-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});


// Function to toggle chatbot on mobile
function toggleChat() {
    const chatbotSidebar = document.getElementById('chatbot-sidebar');
    chatbotSidebar.classList.toggle('active');
    console.log('Chatbot toggled:', chatbotSidebar.classList.contains('active'));
}


// Function to toggle dark mode
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const themeToggleButton = document.getElementById('theme-toggle-button');
    if (document.body.classList.contains('dark-mode')) {
        themeToggleButton.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
    } else {
        themeToggleButton.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
    }
}




