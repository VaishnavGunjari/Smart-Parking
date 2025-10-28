const videoFeed = document.getElementById("videoFeed");
const startButton = document.getElementById("startButton");
const stopButton = document.getElementById("stopButton");
const statusText = document.getElementById("statusText");

let videoSource = "http://localhost:5000/video_feed"; // Update with your backend video feed URL
let interval;

// Start video feed
startButton.addEventListener("click", () => {
    videoFeed.src = videoSource;
    fetch("http://localhost:5000/start_detection") // Backend endpoint to start detection
        .then(response => response.json())
        .then(data => {
            console.log("Detection started:", data);
            updateStatus();
        })
        .catch(error => console.error("Error starting detection:", error));
});

// Stop video feed
stopButton.addEventListener("click", () => {
    videoFeed.src = "";
    clearInterval(interval);
    fetch("http://localhost:5000/stop_detection") // Backend endpoint to stop detection
        .then(response => response.json())
        .then(data => console.log("Detection stopped:", data))
        .catch(error => console.error("Error stopping detection:", error));
});

// Update parking status
function updateStatus() {
    interval = setInterval(() => {
        fetch("http://localhost:5000/parking_status") // Backend endpoint for parking status
            .then(response => response.json())
            .then(data => {
                const { freeSpaces, totalSpaces } = data;
                statusText.textContent = `Free Spaces: ${freeSpaces} / ${totalSpaces}`;
            })
            .catch(error => console.error("Error updating status:", error));
    }, 1000);
}