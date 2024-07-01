# import LLM
# import VoiceDictation

import json
import base64
import requests

def unit():
    autofile_path = 'sound_track/asr_example_zh.pcm'
    with open(autofile_path, 'rb') as f:
        pcm_data = f.read()
    encoded_pcm_data = base64.b64encode(pcm_data).decode('utf-8')

    json_data = {
        'AudioFile': encoded_pcm_data,
        'format': 'audio/L16;rate=16000',
    }

    json_str = json.dumps(json_data)

    url = 'http://localhost:1300/transcribe'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json_str)
    res = json.loads(response.content)
    print(res['transcription'])

    json_data = {
        'words': res['transcription']
    }
    json_str = json.dumps(json_data)
    url = 'http://localhost:1401/LLM'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json_str)
    res = json.loads(response.content)
    print(res['context'])


unit()