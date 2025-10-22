let videoCount = 0;

export function addVideo() {
    videoCount++;
    const videoDiv = document.createElement("div");
    videoDiv.classList.add("video");

    videoDiv.innerHTML = `
        <label>Виберіть відео ${videoCount}</label>
        <input type="file" name="videos_file" accept="video/*" required>

        <label>Опис відео ${videoCount}</label>
        <textarea name="videos_description" placeholder="Опишіть відео..." rows="3" required></textarea>

        <button type="button" class="remove-video-btn">🗑 Видалити</button>
        <hr>
    `;

    videoDiv.querySelector(".remove-video-btn").addEventListener("click", () => videoDiv.remove());

    document.getElementById("video_download").appendChild(videoDiv);
    videoDiv.scrollIntoView({ behavior: "smooth" });
}
