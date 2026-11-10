const $ = (id) => document.getElementById(id);
let recognition = null;
let listening = false;
let latestAnalysis = null;
let conversation = [];

function addBubble(role, text) {
  const node = document.createElement("div");
  node.className = "bubble " + role;
  const label = document.createElement("small");
  label.textContent = role === "seller" ? "YOU" : "VIRTUAL KAM";
  const body = document.createElement("span");
  body.textContent = text;
  node.append(label, body);
  $("transcript").appendChild(node);
  $("transcript").scrollTop = $("transcript").scrollHeight;
}

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 1;
  utterance.lang = "en-IN";
  const voices = window.speechSynthesis.getVoices();
  const voice = voices.find(v => /en-IN/i.test(v.lang)) || voices.find(v => /en/i.test(v.lang));
  if (voice) utterance.voice = voice;
  window.speechSynthesis.speak(utterance);
}

function renderAnalysis(data) {
  latestAnalysis = data;
  const m = data.metrics;
  const cards = [
    ["ORDERS", m.orders.current.toLocaleString("en-IN"), m.orders.change_pct],
    ["VISITS", m.visits.current.toLocaleString("en-IN"), m.visits.change_pct],
    ["CONVERSION", m.conversion_rate.current + "%", m.conversion_rate.change_pct],
    ["REVENUE", "₹" + Math.round(m.revenue_inr.current / 1000) + "k", m.revenue_inr.change_pct]
  ];
  $("metrics").innerHTML = cards.map(([name, value, change]) => {
    const good = Number(change) >= 0;
    return '<div class="metric"><label>' + name + '</label><strong>' + value + '</strong><small class="' + (good ? 'good' : '') + '">' + (change > 0 ? "+" : "") + change + '% vs previous</small></div>';
  }).join("");
  $("signals").innerHTML = data.signals.map(s =>
    '<div class="signal ' + s.severity + '"><span class="dot"></span><div><strong>' +
    escapeHtml(s.title) + '</strong><p>' + escapeHtml(s.evidence) + '</p></div></div>'
  ).join("");
  $("actions").innerHTML = data.actions.map(a =>
    '<div class="action"><div class="priority ' + a.priority.toLowerCase() + '">' + a.priority + '</div><div><strong>' +
    escapeHtml(a.title) + '</strong><p>' + escapeHtml(a.steps) + '</p><small>' + escapeHtml(a.timeframe) + ' · ' + escapeHtml(a.success_metric) + '</small></div></div>'
  ).join("");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
}

async function sendMessage(message) {
  const clean = message.trim();
  if (!clean) return;
  addBubble("seller", clean);
  conversation.push({role:"seller",text:clean});
  $("messageInput").value = "";
  $("callStatus").textContent = "Reviewing your business signals…";
  try {
    const response = await fetch("/api/analyze", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({message:clean})
    });
    if (!response.ok) throw new Error("The analysis service returned an error.");
    const result = await response.json();
    renderAnalysis(result.analysis);
    addBubble("assistant", result.reply);
    conversation.push({role:"assistant",text:result.reply});
    speak(result.reply);
    $("callStatus").textContent = "Your recovery plan is ready";
    $("callSummary").innerHTML = '<div class="eyebrow">CALL SUMMARY</div><p>' +
      escapeHtml(result.analysis.summary) + '</p><p><strong>Next priority:</strong> ' +
      escapeHtml(result.analysis.actions[0]?.title || "Review the latest seller signals") + '</p><p><strong>AI response mode:</strong> ' +
      escapeHtml(result.provider === "gemini" ? "Gemini + verified diagnostics" : "Deterministic fallback + verified diagnostics") + '</p>';
  } catch (error) {
    addBubble("assistant", "I could not reach the analysis service. Please check that the local app is running and try again.");
    $("callStatus").textContent = "Connection issue";
  }
}

function startRecognition() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    $("micHint").textContent = "Speech input unavailable here. Use the text box below.";
    return;
  }
  recognition = new SpeechRecognition();
  recognition.lang = "en-IN";
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    sendMessage(transcript);
  };
  recognition.onerror = (event) => {
    $("micHint").textContent = "Microphone issue: " + event.error + ". You can type below.";
    stopListeningUI();
  };
  recognition.onend = () => stopListeningUI();
  try {
    recognition.start();
    listening = true;
    $("micButton").style.background = "#188568";
    $("micTitle").textContent = "Listening…";
    $("micHint").textContent = "Speak clearly, then pause";
    $("callStatus").textContent = "Listening to seller";
    $("wave").classList.add("active");
    $("stopButton").disabled = false;
  } catch {
    $("micHint").textContent = "Could not start speech recognition. Use the text box.";
  }
}

function stopListeningUI() {
  listening = false;
  $("micButton").style.background = "";
  $("micTitle").textContent = "Start voice call";
  $("micHint").textContent = "Allow microphone access when prompted";
  $("wave").classList.remove("active");
}

$("micButton").addEventListener("click", () => {
  if (listening) {
    recognition?.stop();
    stopListeningUI();
  } else startRecognition();
});
$("stopButton").addEventListener("click", () => {
  recognition?.stop();
  window.speechSynthesis?.cancel();
  stopListeningUI();
  $("callStatus").textContent = "Call ended";
  $("stopButton").disabled = true;
});
$("sendButton").addEventListener("click", () => sendMessage($("messageInput").value));
$("messageInput").addEventListener("keydown", event => {
  if (event.key === "Enter") sendMessage($("messageInput").value);
});
$("commitButton").addEventListener("click", async () => {
  const commitment = $("commitmentInput").value.trim();
  if (commitment.length < 3) {
    $("commitStatus").textContent = "Please enter the action you can commit to.";
    return;
  }
  const response = await fetch("/api/commitment", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body:JSON.stringify({commitment})
  });
  const result = await response.json();
  $("commitStatus").textContent = result.message + " — " + result.commitment;
  addBubble("assistant", "Great. I have captured your commitment for this demo: " + commitment + ". We will review the agreed metric in the stated time window.");
  speak("Great. I have captured your commitment. We will review the agreed metric in the stated time window.");
});

async function init() {
  try {
    const [seller, analysis] = await Promise.all([
      fetch("/api/seller").then(r => r.json()),
      fetch("/api/analysis").then(r => r.json())
    ]);
    $("sellerName").textContent = seller.seller.seller_name;
    $("sellerMeta").textContent = seller.seller.category + " · Demo seller";
    renderAnalysis(analysis);
    window.speechSynthesis?.getVoices();
  } catch (error) {
    $("callStatus").textContent = "Could not load seller demo data";
  }
}
init();
