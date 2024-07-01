# import LLM
# import VoiceDictation

import json
import base64
import requests

def VoiceDictaton(autofile):
    with open(autofile, 'rb') as f:
        pcm_data = f.read()
    encoded_pcm_data = base64.b64encode(pcm_data).decode('utf-8')
    json_data = {
        'AudioFile': encoded_pcm_data,
        'format': 'audio/L16;rate=16000',
    }
    json_str = json.dumps(json_data)

    url = 'http://localhost:5001/transcribe'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json_str)
    res = json.loads(response.content)

    return res

def callLLM(words):
    json_data = {
        'words': words
    }
    json_str = json.dumps(json_data)

    url = 'http://localhost:5003/LLM'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json_str)
    res = json.loads(response.content)

    return res['context']

if __name__ == '__main__':
    words = VoiceDictaton('sound_track/asr_example_zh.pcm')
    callLLM(words)