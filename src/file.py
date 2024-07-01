import LLM
import VoiceDictation

import json
import base64
import requests
import threading

class MyCounter(threading.Thread):
    def __init__(self, functional):
        threading.Thread.__init__(self)
        self.functional = functional

    def run(self):
        self.functional()

class MainCounter(threading.Thread):
    def run(self):
        words = VoiceDictaton('sound_track/asr_example_zh.pcm')
        res = callLLM(words)
        print(res)


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

    return res['transcription']

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
    VoiceDictationThread = MyCounter(VoiceDictation.unit)
    LLMThread = MyCounter(LLM.unit)
    main_thread = MainCounter()
    # VoiceDictation.unit()
    # LLM.unit()
    VoiceDictationThread.start()
    LLMThread.start()
    main_thread.start()
