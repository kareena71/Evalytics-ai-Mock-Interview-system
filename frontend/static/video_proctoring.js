/* ================= DOM ELEMENTS ================= */

const video = document.getElementById("video");
const statusText = document.getElementById("faceStatus");
const integrityText = document.getElementById("integrityScore");
const violationsText = document.getElementById("violations");

let faceWasVisible = true;

/* ================= START CAMERA ================= */

navigator.mediaDevices.getUserMedia({ video: true })
.then(stream => {
    video.srcObject = stream;
})
.catch(err => {
    console.error("Camera error:", err);
});

/* ================= MEDIAPIPE FACE DETECTOR ================= */

const faceMesh = new FaceMesh({
    locateFile: file =>
        `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
});

faceMesh.setOptions({
    maxNumFaces: 1,
    refineLandmarks: true,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5
});

/* ================= DETECTION RESULT ================= */

faceMesh.onResults(results => {

    // ===== NO FACE DETECTED =====
    if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {

        statusText.innerText = "NO FACE DETECTED";
        statusText.style.color = "#ef4444"; // red

        integrityText.innerText = "●";
        integrityText.style.color = "#ef4444"; // red dot

        // Increase violation only once per disappearance
        if (faceWasVisible) {
            let current = parseInt(violationsText.innerText);
            violationsText.innerText = current + 1;
            faceWasVisible = false;
        }

        return;
    }

    // ===== FACE DETECTED =====
    const face = results.multiFaceLandmarks[0];
    const nose = face[1];

    integrityText.innerText = "●";
    integrityText.style.color = "#22c55e"; // green dot
    faceWasVisible = true;

    // Direction detection
    if (nose.x < 0.35)
        statusText.innerText = "LEFT";
    else if (nose.x > 0.65)
        statusText.innerText = "RIGHT";
    else if (nose.y < 0.35)
        statusText.innerText = "UP";
    else if (nose.y > 0.65)
        statusText.innerText = "DOWN";
    else
        statusText.innerText = "CENTER";

    statusText.style.color = "#f9f9f9"; 
});

/* ================= SEND FRAMES ================= */

const camera = new Camera(video, {
    onFrame: async () => {
        await faceMesh.send({ image: video });
    },
    width: 640,
    height: 480
});

camera.start();

