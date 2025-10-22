from app.database.crud.web.corses.handle_courses import create_video_url, create_task_for_module, generate_answer


def parse_video_data(form):
    videos_data = {}

    for key, value in form.items():
        if key.startswith("videos_url["):
            # приклад: videos_url[${video_url_Count}]
            parts = key.replace("videos_url[", "").replace("]", "").split("[")
            video_id = int(parts[0])
            field_name = parts[1] if len(parts) > 1 else None

            if video_id not in videos_data:
                videos_data[video_id] = {"title": None, "url": None}

            if field_name in ("title", "url"):
                videos_data[video_id][field_name] = value

    return videos_data


async def save_videos(videos_data, module_id):
    if videos_data:
        for video in videos_data.values():
            title = video.get("title")
            link = video.get("url")
            if title and link:
                await create_video_url(title, module_id, link)


def parse_tasks_data(form):
    tasks = {}

    for key, value in form.items():
        if key.startswith("tasks["):
            # приклад: tasks[1][answers][2][text]
            parts = key.replace("tasks[", "").replace("]", "").split("[")
            task_index = int(parts[0])
            field = parts[1]

            if task_index not in tasks:
                tasks[task_index] = {"question": None, "answers": []}

            if field == "question":
                tasks[task_index]["question"] = value
            elif field == "answers":
                ans_index = int(parts[2])
                ans_field = parts[3]
                while len(tasks[task_index]["answers"]) <= ans_index:
                    tasks[task_index]["answers"].append({})
                tasks[task_index]["answers"][ans_index][ans_field] = value
    return tasks


async def save_tasks(tasks_data, module_id):
    for task in tasks_data.values():
        task_id = await create_task_for_module(task["question"], None, module_id)
        for answer in task["answers"]:
            text = answer.get("text")
            is_correct = str(answer.get("is_correct")).lower() == "true"
            await generate_answer(text, is_correct, task_id)


