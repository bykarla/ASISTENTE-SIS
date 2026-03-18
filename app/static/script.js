const chatBox = document.getElementById('chat-box');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');
const chatToggle = document.getElementById('chat-toggle');
const chatWindow = document.getElementById('chat-window');
const minimizeBtn = document.getElementById('minimize-btn');
const closeBtn = document.getElementById('close-btn');
const optBtns = document.querySelectorAll('.opt-btn');
const escalateBtn = document.getElementById('escalate-btn');

let mediaRecorder;
let audioChunks = [];
let isRecording = false;
let sesionId = localStorage.getItem('contexto_conversacion_id') || null;

// --- Controles de Ventana ---
chatToggle.addEventListener('click', () => {
    chatWindow.classList.toggle('hidden');
    chatToggle.classList.add('hidden');
});

minimizeBtn.addEventListener('click', () => {
    chatWindow.classList.add('hidden');
    chatToggle.classList.remove('hidden');
});

closeBtn.addEventListener('click', () => {
    chatWindow.classList.add('hidden');
    chatToggle.classList.remove('hidden');
});

// --- Opciones Rápidas ---
optBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        sendMessage(query);
    });
});

escalateBtn.addEventListener('click', () => {
    sendMessage("Quiero hablar con un agente humano");
});

// --- Chat Core ---
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

sendBtn.addEventListener('click', () => sendMessage());

async function sendMessage(textOverride = null) {
    const text = textOverride || userInput.value.trim();
    if (!text) return;

    appendMessage('user', text);
    if (!textOverride) userInput.value = '';

    try {
        const formData = new FormData();
        formData.append('mensaje', text);
        formData.append('tipo_entrada', 'texto');
        if (sesionId) formData.append('contexto_conversacion_id', sesionId);

        const response = await fetch('/api/v1/asistente-virtual/query', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            appendMessage('bot', `Error del servidor (${response.status}).`);
            return;
        }

        const data = await response.json();
        handleResponse(data);
    } catch (error) {
        appendMessage('bot', 'No se pudo conectar con el servidor.');
    }
}

function handleResponse(data) {
    appendMessage('bot', data.respuesta, data);
}

function appendMessage(sender, text, metadata = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    if (sender === 'bot') {
        msgDiv.innerHTML = `
            <div class="bot-avatar"><i data-lucide="bot"></i></div>
            <div class="message-content">
                <p>${text}</p>
                <span class="message-time">${time}</span>
            </div>
        `;
    } else {
        msgDiv.innerHTML = `
            <div class="message-content">
                <p>${text}</p>
                <span class="message-time">${time}</span>
            </div>
        `;
    }

    if (metadata && metadata.capa_utilizada) {
        const info = document.createElement('div');
        info.style.fontSize = '0.6rem';
        info.style.opacity = '0.5';
        info.style.marginTop = '4px';
        info.textContent = `Capa ${metadata.capa_utilizada} | Confianza: ${metadata.confianza.toFixed(2)}`;
        msgDiv.querySelector('.message-content').appendChild(info);
    }

    chatBox.appendChild(msgDiv);
    lucide.createIcons();
    chatBox.scrollTop = chatBox.scrollHeight;
}

// --- Voz ---
micBtn.addEventListener('click', async () => {
    if (!isRecording) startRecording();
    else stopRecording();
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            sendAudio(audioBlob);
        };
        mediaRecorder.start();
        isRecording = true;
        micBtn.classList.add('recording');
        micBtn.innerHTML = '<i data-lucide="square"></i>';
        lucide.createIcons();
    } catch (err) {
        alert('Micrófono desactivado.');
    }
}

function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.innerHTML = '<i data-lucide="mic"></i>';
    lucide.createIcons();
}

async function sendAudio(blob) {
    appendMessage('user', '[Audio enviado...]');
    try {
        const formData = new FormData();
        formData.append('audio', blob, 'query.wav');
        formData.append('tipo_entrada', 'voz');
        if (sesionId) formData.append('contexto_conversacion_id', sesionId);

        const response = await fetch('/api/v1/asistente-virtual/query', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        handleResponse(data);
    } catch (error) {
        appendMessage('bot', 'Error al procesar audio.');
    }
}
