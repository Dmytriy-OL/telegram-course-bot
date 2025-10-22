let taskCount = 0;

export function addTask() {
  taskCount++;
  const taskDiv = document.createElement("div");
  taskDiv.classList.add("task");

  taskDiv.innerHTML = `
    <label>Питання ${taskCount}</label>
    <textarea name="tasks[${taskCount}][question]" rows="2" required></textarea>

    <div class="answers">
      <label>✅ Правильна відповідь</label>
      <input type="text" name="tasks[${taskCount}][answers][0][text]" required>
      <input type="hidden" name="tasks[${taskCount}][answers][0][is_correct]" value="true">

      <label>❌ Неправильна відповідь 1</label>
      <input type="text" name="tasks[${taskCount}][answers][1][text]" required>
      <input type="hidden" name="tasks[${taskCount}][answers][1][is_correct]" value="false">

      <label>❌ Неправильна відповідь 2</label>
      <input type="text" name="tasks[${taskCount}][answers][2][text]" required>
      <input type="hidden" name="tasks[${taskCount}][answers][2][is_correct]" value="false">

      <label>❌ Неправильна відповідь 3</label>
      <input type="text" name="tasks[${taskCount}][answers][3][text]" required>
      <input type="hidden" name="tasks[${taskCount}][answers][3][is_correct]" value="false">
    </div>

    <button type="button" class="remove-task-btn">🗑 Видалити</button>
  `;

  taskDiv.querySelector(".remove-task-btn").addEventListener("click", () => taskDiv.remove());

  document.getElementById("tasks").appendChild(taskDiv);
  taskDiv.scrollIntoView({ behavior: "smooth" });
}
