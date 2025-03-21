async function convert() {
    const urlInput = document.getElementById("url");
    const mediaTypeSelect = document.getElementById("media_type");
    const qualitySelect = document.getElementById("quality");
    const messageDiv = document.getElementById("message");
    
    const youtubeUrl = urlInput.value.trim();
    const media_type = mediaTypeSelect.value;
    const quality = qualitySelect.value;

    if (!youtubeUrl) {
        messageDiv.innerText = "Please enter a valid YouTube URL.";
        return;
    }

    messageDiv.innerText = "Converting, please wait...";

    try {
        const response = await fetch("/convert", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url: youtubeUrl, media_type: media_type, quality: quality })
        });

        if (!response.ok) {
            const errorData = await response.json();
            messageDiv.innerText = "Error: " + errorData.error;
            return;
        }

        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        // Set file name based on media type
        a.download = media_type === "audio" ? "audio.wav" : "video.mp4";
        document.body.appendChild(a);
        a.click();
        a.remove();
        messageDiv.innerText = "Conversion complete! Download should start shortly.";
    } catch (error) {
        messageDiv.innerText = "Error: " + error.message;
    }
}
