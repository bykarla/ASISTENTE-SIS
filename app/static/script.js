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
    escalateRequest();
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
        const response = await fetch('/api/v1/consultar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mensaje: text,
                contexto_conversacion_id: sesionId
            })
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
    // Guardar el ID de conversación para mantener el contexto
    if (data.conversation_id) {
        sesionId = data.conversation_id;
        localStorage.setItem('contexto_conversacion_id', sesionId);
    }
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
    alert('La función de voz no está disponible en este momento.');
    /* 
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        ...
    } catch (err) {
        alert('Micrófono desactivado.');
    }
    */
}

function stopRecording() {
    mediaRecorder.stop();
    isRecording = false;
    micBtn.classList.remove('recording');
    micBtn.innerHTML = '<i data-lucide="mic"></i>';
    lucide.createIcons();
}

async function sendAudio(blob) {
    // Función deshabilitada temporalmente
    appendMessage('bot', 'El procesamiento de voz no está configurado en el servidor principal.');
}

async function escalateRequest() {
    if (!sesionId) {
        appendMessage('bot', 'Por favor, inicia una consulta antes de solicitar un agente.');
        return;
    }

    appendMessage('user', '[Solicitando hablar con un humano...]');

    try {
        const response = await fetch('/api/v1/escalar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_id: sesionId,
                motivo_escalado: "SOLICITUD_USUARIO",
                resumen_conversacion: "El usuario solicitó atención humana desde la interfaz.",
                user_message: "Solicitud manual de escalado",
                departamento_destino: "SECRETARIA"
            })
        });

        const data = await response.json();
        if (response.ok) {
            appendMessage('bot', data.mensaje);
            // Mostrar info del ticket si existe
            if (data.ticket_id) {
                const info = document.createElement('div');
                info.style.fontSize = '0.7rem';
                info.style.opacity = '0.7';
                info.style.marginTop = '4px';
                info.style.color = 'var(--sis-blue)';
                info.textContent = `Ticket generado: #${data.ticket_id.substring(0,8)}`;
                chatBox.lastElementChild.querySelector('.message-content').appendChild(info);
            }
        } else {
            appendMessage('bot', 'No se pudo procesar el escalado en este momento.');
        }
    } catch (error) {
        appendMessage('bot', 'Error de conexión con el servicio de soporte.');
    }
}

