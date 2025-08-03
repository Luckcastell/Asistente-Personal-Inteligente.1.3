async function uploadPDF() {
  const fileInput = document.getElementById("pdf-file");
  if (!fileInput.files.length) return alert("Selecciona un archivo PDF");

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const res = await fetch("http://127.0.0.1:8000/upload", { method: "POST", body: formData });
  const data = await res.json();
  document.getElementById("upload-status").innerText = data.message || data.error;
}

async function sendMessage() {
  const input = document.getElementById("user-input");
  const chatBox = document.getElementById("chat-box");
  const msg = input.value.trim();
  if (!msg) return;

  chatBox.innerHTML += `<div class="message user"><strong>Tú:</strong> ${msg}</div>`;
  input.value = "";

  const res = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg })
  });
  const data = await res.json();

  chatBox.innerHTML += `<div class="message bot"><strong>Suriel:</strong> ${data.reply}</div>`;
  chatBox.scrollTop = chatBox.scrollHeight;
}
