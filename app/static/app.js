let token = localStorage.getItem("stayhappy_token") || null;
let moodChart = null;

// Show the app if we already have a token saved from before
if (token) {
  document.getElementById("auth-section").style.display = "none";
  document.getElementById("app-section").style.display = "block";
  loadJournal();
  loadMoodTrend();
  loadChatHistory();
}

async function register() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const res = await fetch("/api/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (res.ok) {
    handleAuthSuccess(data);
  } else {
    document.getElementById("auth-message").textContent = data.error || "Registration failed";
  }
}

async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  if (res.ok) {
    handleAuthSuccess(data);
  } else {
    document.getElementById("auth-message").textContent = data.error || "Login failed";
  }
}

function handleAuthSuccess(data) {
  token = data.access_token;
  localStorage.setItem("stayhappy_token", token);
  document.getElementById("auth-section").style.display = "none";
  document.getElementById("app-section").style.display = "block";
  loadJournal();
  loadMoodTrend();
  loadChatHistory();
}

function authHeaders() {
  return { "Content-Type": "application/json", "Authorization": "Bearer " + token };
}

async function submitJournal() {
  const content = document.getElementById("journal-text").value.trim();
  if (!content) return;
  const res = await fetch("/api/journal", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ content }),
  });
  const data = await res.json();
  if (res.ok) {
    document.getElementById("journal-text").value = "";
    if (data.crisis_flag) {
      document.getElementById("journal-message").textContent = data.support_message;
    } else {
      document.getElementById("journal-message").textContent = "Saved. Risk level: " + data.entry.risk_label;
    }
    loadJournal();
  }
}

async function loadJournal() {
  const res = await fetch("/api/journal", { headers: authHeaders() });
  const entries = await res.json();
  const list = document.getElementById("journal-list");
  list.innerHTML = "";
  entries.forEach((e) => {
    const div = document.createElement("div");
    div.className = "journal-entry" + (e.risk_label === "high" ? " crisis" : "");
    div.textContent = `[${e.risk_label || "..."}] ${e.content}`;
    list.appendChild(div);
  });
}

async function logMood() {
  const score = parseInt(document.getElementById("mood-score").value);
  if (!score || score < 1 || score > 10) return;
  await fetch("/api/mood", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ score, tags: [] }),
  });
  document.getElementById("mood-score").value = "";
  loadMoodTrend();
}

async function loadMoodTrend() {
  const res = await fetch("/api/mood/trend", { headers: authHeaders() });
  const data = await res.json();

  if (moodChart) moodChart.destroy();
  const ctx = document.getElementById("moodChart").getContext("2d");
  moodChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [{
        label: "Mood score",
        data: data.scores,
        borderColor: "#4a6c5b",
        backgroundColor: "rgba(74,108,91,0.15)",
        tension: 0.3,
        fill: true,
      }],
    },
    options: {
      scales: { y: { min: 1, max: 10 } },
    },
  });
}

async function sendChat() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;
  appendChatMessage("user", message);
  input.value = "";

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ message }),
  });
  const data = await res.json();
  appendChatMessage("assistant", data.reply);
}

async function loadChatHistory() {
  const res = await fetch("/api/chat/history", { headers: authHeaders() });
  const messages = await res.json();
  const win = document.getElementById("chat-window");
  win.innerHTML = "";
  messages.forEach((m) => appendChatMessage(m.role, m.content));
}

function appendChatMessage(role, content) {
  const win = document.getElementById("chat-window");
  const div = document.createElement("div");
  div.className = "chat-msg " + role;
  div.textContent = content;
  win.appendChild(div);
  win.scrollTop = win.scrollHeight;
}