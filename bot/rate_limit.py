import time

user_requests = {}

def check_limit(user_id):
    now = time.time()

    if user_id not in user_requests:
        user_requests[user_id] = []

    # Oxirgi 5 soniyadagi so'rovlarni saqlash
    user_requests[user_id] = [
        t for t in user_requests[user_id] if now - t < 5
    ]

    if len(user_requests[user_id]) > 3:
        return False

    user_requests[user_id].append(now)
    return True
