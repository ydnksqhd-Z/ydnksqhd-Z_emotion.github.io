import LLM
import VoiceDictation

import json

def unit():
    autofile_path = '/workspaces/ydnksqhd-Z_emotion.github.io/sound_track/asr_example_zh.pcm'
    words = VoiceDictation.transcribe(autofile_path)
    print(len(words))
    for mes in words :
        res = json.loads(mes)
        if res['status'] == 0 :
            print(res['data'])
        else :
            print("error")


unit()