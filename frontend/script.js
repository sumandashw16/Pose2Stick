const form = document.getElementById("uploadForm");
const downloadVideo = document.getElementById("downloadVideo");
const downloadJSON = document.getElementById("downloadJSON");
const spinner = document.getElementById("spinner");
const statusMessage = document.getElementById("statusMessage"); // message element

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Show spinner and clear previous status
  if (spinner) spinner.style.display = "block";
  if (statusMessage) statusMessage.textContent = "";

  const formData = new FormData();
  formData.append("video", document.getElementById("videoInput").files[0]);
  formData.append("background", document.getElementById("background").value);
  const includeAudio = document.getElementById("includeAudio")?.checked ? "true" : "false";
  formData.append("include_audio", includeAudio);

  try {
    const response = await fetch("https://pose2stick.onrender.com/api/process", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Set download links
    downloadVideo.href = data.video_url;
    downloadJSON.href = data.keypoints_url;

    // Show status message
    if (statusMessage) {
      statusMessage.textContent = "✅ Your video is ready! You can now download it.";
    }

  } catch (err) {
    console.error(err);
    alert("Error processing video: " + err.message);
  } finally {
    if (spinner) spinner.style.display = "none";
  }
});
