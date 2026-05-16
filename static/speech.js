// Speech to Text
let recognition;

if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.lang = "en-US";

    recognition.onresult = function (event) {
        let transcript = event.results[event.results.length - 1][0].transcript;
        document.getElementById("answer").value += transcript + " ";
    };
}

function startRecording() {
    if (recognition) {
        recognition.start();
    } else {
        alert("Speech Recognition not supported");
    }
}

// Text to Speech
function speakQuestion() {
    let question = document.getElementById("question").innerText;
    let msg = new SpeechSynthesisUtterance(question);
    speechSynthesis.speak(msg);
}
let violations = 0;
let lastFaceTime = Date.now();

setInterval(() => {
  const now = Date.now();
  if (now - lastFaceTime > 3000) {
    violations++;
    document.getElementById("violations").innerText = violations;
  }
}, 3000);
