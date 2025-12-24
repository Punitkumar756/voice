let isListening = false;

const voiceBtn = document.getElementById('voiceBtn');
const sendBtn = document.getElementById('sendBtn');
const textInput = document.getElementById('textInput');
const responseBox = document.getElementById('responseBox');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const avatarCircle = document.getElementById('avatarCircle');
const soundWaves = document.getElementById('soundWaves');
const micIcon = document.getElementById('micIcon');

// Voice button click
voiceBtn.addEventListener('click', async () => {
    if (isListening) return;
    
    startListening();
    
    try {
        const response = await fetch('/listen', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        stopListening();
        displayResponse(data);
    } catch (error) {
        stopListening();
        displayError('Error connecting to assistant. Please try again.');
    }
});

// Send button click
sendBtn.addEventListener('click', () => {
    executeCommand(textInput.value);
});

// Enter key press
textInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        executeCommand(textInput.value);
    }
});

// Execute command function
async function executeCommand(command) {
    if (!command.trim()) return;
    
    textInput.value = '';
    showProcessing(command);
    
    try {
        const response = await fetch('/execute', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        });
        
        const data = await response.json();
        displayResponse(data);
    } catch (error) {
        displayError('Error executing command. Please try again.');
    }
}

function startListening() {
    isListening = true;
    voiceBtn.classList.add('listening');
    voiceBtn.querySelector('span').textContent = 'Listening...';
    statusDot.classList.add('listening');
    statusText.textContent = 'Listening';
    avatarCircle.classList.add('active');
    soundWaves.classList.add('active');
    micIcon.className = 'fas fa-circle-notch fa-spin';
    
    responseBox.innerHTML = '<p class="greeting">🎤 Listening to your command...</p>';
}

function stopListening() {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceBtn.querySelector('span').textContent = 'Click to Speak';
    statusDot.classList.remove('listening');
    statusText.textContent = 'Ready';
    avatarCircle.classList.remove('active');
    soundWaves.classList.remove('active');
    micIcon.className = 'fas fa-microphone';
}

function showProcessing(command) {
    responseBox.innerHTML = `
        <p class="command">You: "${command}"</p>
        <p class="response">🤖 Processing...</p>
    `;
}

function displayResponse(data) {
    let icon = '🤖';
    
    if (data.action === 'time') icon = '⏰';
    else if (data.action === 'date') icon = '📅';
    else if (data.action === 'open_app') icon = '📱';
    else if (data.action === 'close_app') icon = '❌';
    else if (data.action === 'volume_up' || data.action === 'volume_down') icon = '🔊';
    else if (data.action === 'screenshot') icon = '📸';
    else if (data.action === 'joke') icon = '😄';
    else if (data.action === 'google_search') icon = '🔍';
    else if (data.action === 'greeting') icon = '👋';
    
    responseBox.innerHTML = `
        <p class="command">You: "${data.command || 'Command'}"</p>
        <p class="response">${icon} ${data.response}</p>
    `;
}

function displayError(message) {
    responseBox.innerHTML = `
        <p class="response">❌ ${message}</p>
    `;
}

// Add some animations on load
window.addEventListener('load', () => {
    setTimeout(() => {
        responseBox.innerHTML = '<p class="greeting">✨ Voice Assistant Ready! Say "Hello" to begin.</p>';
    }, 500);
});

// Add floating animation to avatar
let rotation = 0;
setInterval(() => {
    if (!isListening) {
        rotation += 0.5;
        avatarCircle.style.transform = `rotate(${rotation}deg)`;
    }
}, 50);
