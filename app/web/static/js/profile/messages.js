const listItems = document.querySelectorAll(".list-item");
const empty = document.getElementById("empty");
const chat = document.getElementById("chat");

listItems.forEach(item => {
    item.addEventListener("click", () => {
        empty.style.display = "none";
        chat.style.display = "flex";

        listItems.forEach(i => i.classList.remove("active"));
        item.classList.add("active");
        item.classList.remove("unread");
    });
});
