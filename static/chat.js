const chatBox = document.getElementById('chatBox');
const userInput = document.getElementById('userInput');
const fileUpload = document.getElementById('fileUpload');

// История сообщений
let history = [];

// Отправка сообщения
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Добавляем сообщение пользователя в чат
    addMessage(message, 'user');
    userInput.value = '';

    // Показываем индикатор загрузки
    const loadingId = addMessage('Агент думает...', 'bot loading');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, history })
        });

        const data = await response.json();

        // Удаляем индикатор загрузки
        document.getElementById(loadingId)?.remove();

        // Добавляем ответ бота
        addMessage(data.reply, 'bot');
        history = data.history;

        // Обновляем уровень
        updateProfile();

    } catch (error) {
        document.getElementById(loadingId)?.remove();
        addMessage('Ошибка соединения с сервером', 'bot error');
    }
}

// Добавление сообщения в чат
function addMessage(text, className) {
    const id = 'msg-' + Date.now() + Math.random();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'message ' + className;
    div.innerHTML = `<div class="msg-content">${escapeHtml(text)}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

// Экранирование HTML
function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, m => map[m]).replace(/\n/g, '<br>');
}

// Загрузка профиля и уровня
async function updateProfile() {
    try {
        const resp = await fetch('/profile');
        const profile = await resp.json();
        const levelNames = {1:"Новичок",3:"Стажёр",5:"Джун",10:"Мидл",20:"Сеньор",50:"Архитектор"};
        document.getElementById('levelDisplay').textContent = `Уровень: ${levelNames[profile.level] || profile.level}`;
    } catch (e) {}
}

// Обработка файла
fileUpload.addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    addMessage(`Загружаю файл: ${file.name}...`, 'user');

    try {
        const resp = await fetch('/upload', { method: 'POST', body: formData });
        const data = await resp.json();
        if (data.text) {
            addMessage(`Прочитано из файла:\n${data.text}`, 'bot');
            // Можно сразу отправить текст агенту
            history.push({role: 'user', content: data.text});
            userInput.value = data.text;
        } else {
            addMessage('Файл загружен, но текст не распознан.', 'bot');
        }
    } catch (e) {
        addMessage('Ошибка загрузки файла', 'bot error');
    }

    fileUpload.value = ''; // сброс
});

// Отправка по Enter
userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') sendMessage();
});

// Первоначальная загрузка профиля
updateProfile();