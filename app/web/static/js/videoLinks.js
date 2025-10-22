let video_url_Count = 0;

export function addVideo_url() {
  video_url_Count++;
  const video_url_Div = document.createElement("div");
  video_url_Div.classList.add("video_url");

  video_url_Div.innerHTML = `
    <label>Назва відео ${video_url_Count}</label>
    <input type="text" name="videos_url[${video_url_Count}][title]" placeholder="Назва відео" required>

    <label>Посилання на відео ${video_url_Count}</label>
    <input type="text" name="videos_url[${video_url_Count}][url]" placeholder="https://..." required>

    <button type="button" class="remove-video-btn">🗑 Видалити</button>
  `;

  video_url_Div.querySelector(".remove-video-btn").addEventListener("click", () => {
    video_url_Div.remove();
  });

  document.getElementById("video_url").appendChild(video_url_Div);
  video_url_Div.scrollIntoView({ behavior: "smooth" });
}
