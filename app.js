const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');

function appendMessage(text, className) {
  const msgDiv = document.createElement('div');
  msgDiv.classList.add('message', className);
  msgDiv.textContent = text;
  chatMessages.appendChild(msgDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatForm.addEventListener('submit', async function(e) {
  e.preventDefault();
  const question = userInput.value.trim();
  if (!question) return;

  appendMessage(question, 'user-message');
  userInput.value = '';

  try {
    const response = await fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: question })
    });
    const data = await response.json();
    appendMessage(data.response || 'Sorry, no response.', 'bot-message');
  } catch (error) {
    appendMessage('Error connecting to server.', 'bot-message');
  }
});
