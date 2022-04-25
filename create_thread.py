import json

import requests

async def create_thread(self, name, minutes, message): # https://pastebin.com/kAajBJNN
    token = 'Bot ' + self._state.http.token
    url = f"https://discord.com/api/v9/channels/{self.id}/messages/{message.id}/threads"
    headers = {
        "authorization": token,
        "content-type": "application/json"
    }
    data = {
        "name": name,
        "type": 11,
        "auto_archive_duration": minutes
    }

    return requests.post(url, headers=headers, json=data).json()

async def create_thread_message(token,thread,content, tts=False, embeds=None): # Made from the corpse of helminth
    token = 'Bot ' + token
    channel_id = int(thread["id"])
    print(channel_id)
    headers = {
        "authorization": token,
        "content-type": "application/json"
    }
    request_body = {
        "content": content,
        "tts": tts,
        "embeds": embeds
    }

    return requests.post("https://discordapp.com/api/channels/" + str(channel_id) + "/messages", headers=headers,data=json.dumps(request_body))