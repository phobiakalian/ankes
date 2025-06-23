mqueue = {}

def add_to_mqueue(chat_id: int, title: str, file: str):
    if chat_id not in mqueue:
        mqueue[chat_id] = []
    mqueue[chat_id].append({"title": title, "file": file})

def get_next(chat_id: int):
    if chat_id in mqueue and mqueue[chat_id]:
        return mqueue[chat_id][0]
    return None

def skip_current(chat_id: int):
    if chat_id in mqueue and mqueue[chat_id]:
        mqueue[chat_id].pop(0)

def clear_mqueue(chat_id: int):
    if chat_id in mqueue:
        mqueue[chat_id].clear()

def get_mqueue_list(chat_id: int):
    return mqueue.get(chat_id, [])