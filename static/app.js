const dropZone   = document.getElementById("drop-zone");
const fileInput  = document.getElementById("file-input");
const btnUpload  = document.getElementById("btn-upload");
const btnSend    = document.getElementById("btn-send");
const btnClear   = document.getElementById("btn-clear");
const msgInput   = document.getElementById("msg-input");
const fileList   = document.getElementById("file-list");
const chatMsgs   = document.getElementById("chat-messages");
const toast      = document.getElementById("toast");
const welcomeMsg = document.getElementById("welcome-msg");

let archivos = [];
let docsReady = false;

function showToast(msg, type) {
  toast.textContent = msg;
  toast.className   = "show " + type;
  setTimeout(function() { toast.className = ""; }, 3000);
}

fileInput.addEventListener("change", function() {
  if (fileInput.files.length > 0) btnUpload.disabled = false;
});

dropZone.addEventListener("dragover", function(e) {
  e.preventDefault();
  dropZone.classList.add("drag-over");
});

dropZone.addEventListener("dragleave", function() {
  dropZone.classList.remove("drag-over");
});

dropZone.addEventListener("drop", function(e) {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  fileInput.files = e.dataTransfer.files;
  if (fileInput.files.length > 0) btnUpload.disabled = false;
});

btnUpload.addEventListener("click", async function() {
  if (!fileInput.files[0]) return;
  var form = new FormData();
  form.append("archivo", fileInput.files[0]);

  btnUpload.disabled  = true;
  btnUpload.textContent = "Procesando...";

  try {
    var res  = await fetch("/subir", { method: "POST", body: form });
    var data = await res.json();

    if (!res.ok || data.error) {
      showToast("Error: " + (data.error || "Error al subir"), "error");
    } else {
      archivos.push(data);
      renderFileList();
      docsReady = true;
      btnSend.disabled = false;
      if (welcomeMsg) welcomeMsg.remove();
      showToast(data.nombre + " cargado (" + data.paginas + " pagina/s)", "success");
      addBotMsg(data.nombre + " cargado correctamente.\n" + data.paginas + " pagina(s) indexadas en ChromaDB.\n\nYa puedes hacer preguntas sobre este documento.");
    }
  } catch (err) {
    showToast("Error de conexion", "error");
  }

  btnUpload.textContent = "Subir documento";
  fileInput.value = "";
  btnUpload.disabled = true;
});

function renderFileList() {
  if (archivos.length === 0) {
    fileList.innerHTML = '<div class="empty-state">Aun no hay documentos</div>';
    return;
  }
  fileList.innerHTML = archivos.map(function(a) {
    return '<div class="file-item">' +
      '<span class="file-badge">' + a.tipo + '</span>' +
      '<span class="file-name" title="' + a.nombre + '">' + a.nombre + '</span>' +
      '<span class="file-pages">' + a.paginas + 'p</span>' +
    '</div>';
  }).join("");
}

btnClear.addEventListener("click", async function() {
  await fetch("/limpiar", { method: "POST" });
  archivos  = [];
  docsReady = false;
  btnSend.disabled = true;
  renderFileList();
  chatMsgs.innerHTML =
    '<div class="welcome" id="welcome-msg">' +
      '<div class="welcome-icon">🔍</div>' +
      '<h2>Asistente RAG</h2>' +
      '<p>Sube un documento PDF o TXT en el panel izquierdo y luego escribe tu pregunta aqui.</p>' +
    '</div>';
  showToast("Sesion limpiada", "success");
});

function escHtml(t) {
  return t.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\n/g,"<br>");
}

function scrollBottom() {
  chatMsgs.scrollTop = chatMsgs.scrollHeight;
}

function addUserMsg(text) {
  var d = document.createElement("div");
  d.className = "msg user";
  d.innerHTML =
    '<div class="msg-bubble">' + escHtml(text) + '</div>' +
    '<div class="msg-meta">Tu - ahora</div>';
  chatMsgs.appendChild(d);
  scrollBottom();
}

function addBotMsg(text, fuentes) {
  fuentes = fuentes || [];
  var d = document.createElement("div");
  d.className = "msg bot";
  var chips = "";
  if (fuentes.length > 0) {
    var seen = {};
    var unicos = fuentes.filter(function(f) {
      var key = f.fuente + (f.pagina || "");
      if (seen[key]) return false;
      seen[key] = true;
      return true;
    });
    chips = '<div class="sources">' +
      '<div class="sources-title">Fuentes encontradas</div>' +
      unicos.map(function(f) {
        return '<div class="source-chip" title="' + escHtml(f.contenido) + '">' +
          '<div class="source-chip-dot"></div>' +
          escHtml(f.fuente) + (f.pagina ? " - p." + f.pagina : "") +
        '</div>';
      }).join("") +
    '</div>';
  }
  d.innerHTML =
    '<div class="msg-bubble">' + escHtml(text) + '</div>' +
    chips +
    '<div class="msg-meta">RAG - ChromaDB</div>';
  chatMsgs.appendChild(d);
  scrollBottom();
}

function addTyping() {
  var d = document.createElement("div");
  d.className = "msg bot";
  d.id = "typing-indicator";
  d.innerHTML = '<div class="msg-bubble typing"><span></span><span></span><span></span></div>';
  chatMsgs.appendChild(d);
  scrollBottom();
  return d;
}

async function enviarPregunta() {
  var texto = msgInput.value.trim();
  if (!texto || !docsReady) return;

  addUserMsg(texto);
  msgInput.value = "";
  msgInput.style.height = "46px";
  btnSend.disabled = true;

  var typing = addTyping();

  try {
    var res = await fetch("/preguntar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pregunta: texto })
    });
    var data = await res.json();
    typing.remove();

    if (!res.ok || data.error) {
      addBotMsg("Error: " + (data.error || "Error al procesar la pregunta"));
    } else {
      addBotMsg(data.respuesta, data.fragmentos || []);
    }
  } catch (err) {
    typing.remove();
    addBotMsg("Error de conexion con el servidor.");
  }

  btnSend.disabled = !docsReady;
}

btnSend.addEventListener("click", enviarPregunta);

msgInput.addEventListener("keydown", function(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    enviarPregunta();
  }
});

msgInput.addEventListener("input", function() {
  msgInput.style.height = "46px";
  msgInput.style.height = Math.min(msgInput.scrollHeight, 120) + "px";
});
