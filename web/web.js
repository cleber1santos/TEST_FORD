const sendBtn = document.getElementById('sendBtn');
const userQueryInput = document.getElementById('userQuery');
const chatBox = document.getElementById('chatBox');
const fileInput = document.getElementById('fileInput');
const uploadLabel = document.querySelector('.upload-label'); 


sendBtn.addEventListener('click', sendMessage);
userQueryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendMessage();
});


uploadLabel.addEventListener('click', () => fileInput.click());


fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    addMessage(`📎 PDF "${file.name}" enviado.`, 'user');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://127.0.0.1:8000/upload_pdf', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Erro ao enviar PDF');

        const data = await response.json();
        addMessage(`✅ ${data.message}`, 'bot');

    } catch (error) {
        addMessage('❌ Não foi possível enviar o PDF.', 'bot');
        console.error(error);
    } finally {
        fileInput.value = ''; 
    }
});


async function sendMessage() {
    const userQuery = userQueryInput.value.trim();
    if (!userQuery) return;

    addMessage(userQuery, 'user');
    userQueryInput.value = '';

    const botMessage = addMessage('Pensando...', 'bot');

    try {
        const response = await fetch("http://127.0.0.1:8000/pergunta", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ pergunta: userQuery })
        });

        if (!response.ok) throw new Error("Erro ao conectar com API");

        const data = await response.json();
        typeText(botMessage, data.resposta.replace(/\n/g, '<br>'));

    } catch (error) {
        botMessage.innerText = "❌ Desculpe, não consegui obter uma resposta.";
        console.error(error);
    }
}


function addMessage(text, type) {
    const message = document.createElement('div');
    message.classList.add('message', type);
    message.innerHTML = text;
    chatBox.appendChild(message);
    chatBox.scrollTop = chatBox.scrollHeight;
    return message;
}

function typeText(element, text) {
    element.innerHTML = '';
    const codeRegex = /```([\s\S]*?)```/g;
    let lastIndex = 0;
    let match;

    while ((match = codeRegex.exec(text)) !== null) {
        const before = text.slice(lastIndex, match.index).replace(/\n/g, '<br>');
        element.innerHTML += before;

        const codeContent = match[1].trim();
        element.innerHTML += `<pre><code>${escapeHTML(codeContent)}</code></pre>`;

        lastIndex = codeRegex.lastIndex;
    }

    const after = text.slice(lastIndex).replace(/\n/g, '<br>');
    element.innerHTML += after;

    element.scrollIntoView({ behavior: "smooth", block: "end" });
}

function escapeHTML(str) {
    return str.replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;");
}
