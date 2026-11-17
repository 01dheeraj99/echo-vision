// EchoVision - Accessible Interactive Engine
document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const browseBtn = document.getElementById("browse-btn");
  const contrastToggle = document.getElementById("contrast-toggle");
  const fontIncreaseBtn = document.getElementById("font-increase");
  const fontResetBtn = document.getElementById("font-reset");
  const srAnnouncer = document.getElementById("sr-announcements");

  const cameraToggleBtn = document.getElementById("camera-toggle-btn");
  const cameraContainer = document.getElementById("camera-container");
  const webcamVideo = document.getElementById("webcam-video");
  const webcamCanvas = document.getElementById("webcam-canvas");
  const captureBtn = document.getElementById("capture-btn");
  const closeCameraBtn = document.getElementById("close-camera-btn");

  const loadingIndicator = document.getElementById("loading-indicator");
  const resultsSection = document.getElementById("results-section");

  const audioPlayer = document.getElementById("audio-player");
  const narrationTranscript = document.getElementById("narration-transcript");
  const replayBtn = document.getElementById("replay-btn");
  const browserSpeechBtn = document.getElementById("browser-speech-btn");
  const downloadAudioLink = document.getElementById("download-audio-link");
  const speedButtons = document.querySelectorAll(".speed-btn");

  const resultImage = document.getElementById("result-image");
  const annotatedImage = document.getElementById("annotated-image");
  const imageToggleContainer = document.getElementById("image-toggle-container");
  const showOriginalBtn = document.getElementById("show-original-btn");
  const showAnnotatedBtn = document.getElementById("show-annotated-btn");

  const captionOutput = document.getElementById("caption-output");
  const objectsSummaryOutput = document.getElementById("objects-summary-output");
  const objectsTagList = document.getElementById("objects-tag-list");
  const ocrOutput = document.getElementById("ocr-output");
  const execTimeBadge = document.getElementById("exec-time");
  const newAnalysisBtn = document.getElementById("new-analysis-btn");
  const sampleButtons = document.querySelectorAll(".sample-btn");

  let webcamStream = null;
  let currentNarrationText = "";

  // Helper: Announce messages to screen readers
  function announce(message) {
    if (srAnnouncer) {
      srAnnouncer.textContent = "";
      setTimeout(() => {
        srAnnouncer.textContent = message;
      }, 50);
    }
  }

  // High Contrast Mode
  const savedContrast = localStorage.getItem("echovision_contrast");
  if (savedContrast === "true") {
    document.body.classList.add("high-contrast");
  }

  contrastToggle.addEventListener("click", () => {
    document.body.classList.toggle("high-contrast");
    const isHigh = document.body.classList.contains("high-contrast");
    localStorage.setItem("echovision_contrast", isHigh ? "true" : "false");
    announce(isHigh ? "High contrast mode enabled." : "High contrast mode disabled.");
  });

  // Font Size Adjustments
  let baseFontSize = 16;
  fontIncreaseBtn.addEventListener("click", () => {
    if (baseFontSize < 24) {
      baseFontSize += 2;
      document.documentElement.style.fontSize = `${baseFontSize}px`;
      announce(`Text size increased to ${baseFontSize} pixels.`);
    }
  });

  fontResetBtn.addEventListener("click", () => {
    baseFontSize = 16;
    document.documentElement.style.fontSize = `16px`;
    announce("Text size reset to default.");
  });

  // Dropzone Events
  browseBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  dropzone.addEventListener("click", () => fileInput.click());

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("drag-over");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("drag-over");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files && fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  // Webcam Controls
  cameraToggleBtn.addEventListener("click", async () => {
    try {
      webcamStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      webcamVideo.srcObject = webcamStream;
      cameraContainer.classList.remove("hidden");
      cameraContainer.setAttribute("aria-hidden", "false");
      cameraContainer.scrollIntoView({ behavior: "smooth" });
      announce("Camera activated. Align your visual subject and click Capture.");
    } catch (err) {
      alert("Could not access camera: " + err.message);
      announce("Error accessing camera.");
    }
  });

  closeCameraBtn.addEventListener("click", stopCamera);

  function stopCamera() {
    if (webcamStream) {
      webcamStream.getTracks().forEach((track) => track.stop());
      webcamStream = null;
    }
    cameraContainer.classList.add("hidden");
    cameraContainer.setAttribute("aria-hidden", "true");
    announce("Camera closed.");
  }

  captureBtn.addEventListener("click", () => {
    if (!webcamStream) return;
    const width = webcamVideo.videoWidth || 640;
    const height = webcamVideo.videoHeight || 480;

    webcamCanvas.width = width;
    webcamCanvas.height = height;
    const ctx = webcamCanvas.getContext("2d");
    ctx.drawImage(webcamVideo, 0, 0, width, height);

    const base64Data = webcamCanvas.toDataURL("image/jpeg", 0.9);
    stopCamera();
    analyzeBase64(base64Data);
  });

  // Sample Buttons
  sampleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const sampleName = btn.getAttribute("data-sample");
      if (sampleName) {
        analyzeSample(sampleName);
      }
    });
  });

  // Main Analysis Request Functions
  function handleFileSelected(file) {
    if (!file.type.startsWith("image/")) {
      alert("Please select a valid image file.");
      return;
    }
    const formData = new FormData();
    formData.append("image", file);
    sendAnalysisRequest(formData, false);
  }

  function analyzeBase64(base64Data) {
    sendAnalysisRequest(JSON.stringify({ image_base64: base64Data }), true);
  }

  function analyzeSample(sampleName) {
    sendAnalysisRequest(JSON.stringify({ sample_name: sampleName }), true);
  }

  async function sendAnalysisRequest(bodyData, isJson) {
    showLoading(true);
    announce("Analyzing image. Please wait while models generate caption, detect objects, and produce speech.");

    try {
      const headers = {};
      if (isJson) {
        headers["Content-Type"] = "application/json";
      }

      const response = await fetch("/analyze", {
        method: "POST",
        headers: headers,
        body: bodyData,
      });

      const data = await response.json();
      showLoading(false);

      if (!response.ok || !data.success) {
        throw new Error(data.error || "Image analysis failed.");
      }

      displayResults(data);
    } catch (err) {
      showLoading(false);
      alert("Error processing image: " + err.message);
      announce("Analysis failed: " + err.message);
    }
  }

  function showLoading(isLoading) {
    if (isLoading) {
      loadingIndicator.classList.remove("hidden");
      resultsSection.classList.add("hidden");
      loadingIndicator.scrollIntoView({ behavior: "smooth" });
    } else {
      loadingIndicator.classList.add("hidden");
    }
  }

  // Display Output
  function displayResults(data) {
    currentNarrationText = data.narration || "";
    narrationTranscript.textContent = currentNarrationText;
    execTimeBadge.textContent = `Processed in ${data.execution_time_seconds}s`;

    // Audio Playback
    if (data.audio_url) {
      audioPlayer.src = data.audio_url;
      downloadAudioLink.href = data.audio_url;
      downloadAudioLink.classList.remove("hidden");
      audioPlayer.play().catch(() => {
        // Autoplay may be blocked by browser policy without user gesture
        console.log("Autoplay was prevented by browser.");
      });
    } else {
      downloadAudioLink.classList.add("hidden");
    }

    // Visual Views
    resultImage.src = data.image_url;
    if (data.annotated_image_url) {
      annotatedImage.src = data.annotated_image_url;
      imageToggleContainer.classList.remove("hidden");
    } else {
      imageToggleContainer.classList.add("hidden");
    }
    showOriginalImage();

    // Text & Object Breakdown
    captionOutput.textContent = data.caption || "(No caption generated)";
    objectsSummaryOutput.textContent = data.objects_summary || "No objects identified.";

    // Render Object Badges
    objectsTagList.innerHTML = "";
    if (data.objects && data.objects.length > 0) {
      data.objects.forEach((obj) => {
        const tag = document.createElement("span");
        tag.className = "tag";
        tag.textContent = `${obj.label} (${Math.round(obj.confidence * 100)}%)`;
        objectsTagList.appendChild(tag);
      });
    }

    ocrOutput.textContent = data.ocr_text ? data.ocr_text : "(No embedded text detected in image)";

    resultsSection.classList.remove("hidden");
    resultsSection.scrollIntoView({ behavior: "smooth" });

    announce(`Analysis complete. Narration: ${currentNarrationText}`);
  }

  // Audio Controls
  replayBtn.addEventListener("click", () => {
    if (audioPlayer.src) {
      audioPlayer.currentTime = 0;
      audioPlayer.play();
      announce("Replaying narration.");
    }
  });

  browserSpeechBtn.addEventListener("click", () => {
    if (!currentNarrationText) return;
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(currentNarrationText);
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
      announce("Reading aloud with browser voice.");
    } else {
      alert("Browser speech synthesis is not supported on this browser.");
    }
  });

  speedButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      speedButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const speed = parseFloat(btn.getAttribute("data-speed"));
      audioPlayer.playbackRate = speed;
      announce(`Audio playback speed set to ${speed}x.`);
    });
  });

  // Image Toggle Buttons
  showOriginalBtn.addEventListener("click", showOriginalImage);
  showAnnotatedBtn.addEventListener("click", showAnnotatedImage);

  function showOriginalImage() {
    resultImage.classList.remove("hidden");
    annotatedImage.classList.add("hidden");
    showOriginalBtn.classList.add("active");
    showAnnotatedBtn.classList.remove("active");
  }

  function showAnnotatedImage() {
    resultImage.classList.add("hidden");
    annotatedImage.classList.remove("hidden");
    showOriginalBtn.classList.remove("active");
    showAnnotatedBtn.classList.add("active");
  }

  newAnalysisBtn.addEventListener("click", () => {
    resultsSection.classList.add("hidden");
    dropzone.scrollIntoView({ behavior: "smooth" });
    fileInput.value = "";
    if (audioPlayer) audioPlayer.pause();
    announce("Ready for new image analysis.");
  });

  // Global Keyboard Shortcuts
  document.addEventListener("keydown", (e) => {
    // Avoid triggering shortcuts while typing inside inputs
    if (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA") return;

    // 'U' -> Upload
    if (e.key === "u" || e.key === "U") {
      fileInput.click();
    }
    // 'C' -> Camera Toggle
    else if (e.key === "c" || e.key === "C") {
      cameraToggleBtn.click();
    }
    // 'Space' -> Toggle Audio Play/Pause
    else if (e.code === "Space") {
      if (!audioPlayer.paused) {
        e.preventDefault();
        audioPlayer.pause();
        announce("Audio paused.");
      } else if (audioPlayer.src) {
        e.preventDefault();
        audioPlayer.play();
        announce("Audio playing.");
      }
    }
    // 'S' -> Sample Image Test
    else if (e.key === "s" || e.key === "S") {
      if (sampleButtons.length > 0) {
        sampleButtons[0].click();
      }
    }
  });
});

