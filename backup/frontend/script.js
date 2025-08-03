async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const message = input.value.trim();
  if (!message) return;

  chatBox.innerHTML += `<div class="message user"><strong>Tú:</strong> ${message}</div>`;
  input.value = "";

  const response = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  });

  const data = await response.json();
  chatBox.innerHTML += `<div class="message bot"><strong>Suriel:</strong> ${data.reply}</div>`;
  chatBox.scrollTop = chatBox.scrollHeight;
}
