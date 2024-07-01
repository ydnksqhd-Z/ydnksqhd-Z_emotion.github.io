# -*- coding:utf-8 -*-
#
#
#  语音听写流式 WebAPI 接口调用示例 接口文档（必看）：https://doc.xfyun.cn/rest_api/语音听写（流式版）.html
#  webapi 听写服务参考帖子（必看）：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=38947&extra=
#  语音听写流式WebAPI 服务，热词使用方式：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--个性化热词，
#  设置热词
#  注意：热词只能在识别的时候会增加热词的识别权重，需要注意的是增加相应词条的识别率，但并不是绝对的，具体效果以您测试为准。
#  语音听写流式WebAPI 服务，方言试用方法：登陆开放平台https://www.xfyun.cn/后，找到控制台--我的应用---语音听写（流式）---服务管理--识别语种列表
#  可添加语种或方言，添加后会显示该方言的参数值
#  错误码链接：https://www.xfyun.cn/document/error-code （code返回错误码时必看）
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
from flask import Flask, request, jsonify
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

APP_ID = '72cf37b5'
API_SECRET = 'NTI4MmVjMDRlZTk5ZjIxMGUxNjhjYWY0'
API_KEY = '851fbce2b48a1ccbb09ec76ba2a80258'

app = Flask(__name__)

res = []

class _Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}

        # 业务参数(business)
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1, "vad_eos":10000}

    # 生成url
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'

        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }

        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)

        return url


# 收到websocket消息的处理
def _on_message(ws, message):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            # print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            res.append(errMsg)
        else:
            data = json.loads(message)["data"]["result"]["ws"]
            # print(json.loads(message))
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            # print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
            res.append(result)
    except Exception as e:
        # print("receive msg,but parse exception:", e)
        res.append(e)



# 收到websocket错误的处理
def _on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def _on_close(ws,x,y):
    print("### closed ###")


# 收到websocket连接建立的处理
def _create_on_open(wsParam):
    def _on_open(ws):
        def run(*args):
            frameSize = 8000  # 每一帧的音频大小
            intervel = 0.04  # 发送音频间隔(单位:s)
            status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

            with open(wsParam.AudioFile, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    # 文件结束
                    if not buf:
                        status = STATUS_LAST_FRAME
                    # 第一帧处理
                    # 发送第一帧音频，带business 参数
                    # appid 必须带上，只需第一帧发送
                    if status == STATUS_FIRST_FRAME:
                        d = {"common": wsParam.CommonArgs,
                            "business": wsParam.BusinessArgs,
                            "data": {"status": 0, "format": "audio/L16;rate=16000",
                                    "audio": str(base64.b64encode(buf), 'utf-8'),
                                    "encoding": "raw"}}
                        d = json.dumps(d)
                        ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                    # 中间帧处理
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                    "audio": str(base64.b64encode(buf), 'utf-8'),
                                    "encoding": "raw"}}
                        ws.send(json.dumps(d))
                    # 最后一帧处理
                    elif status == STATUS_LAST_FRAME:
                        d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                    "audio": str(base64.b64encode(buf), 'utf-8'),
                                    "encoding": "raw"}}
                        ws.send(json.dumps(d))
                        time.sleep(1)
                        break
                    # 模拟音频采样间隔
                    time.sleep(intervel)
            ws.close()

        thread.start_new_thread(run, ())
    return _on_open

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    base64_audio = data.get('AudioFile')
    AudioFile = base64.b64decode(base64_audio)

    with open('sound_track/output.pcm', 'wb') as f:
        f.write(AudioFile)
    
    wsParam = _Param(APPID=APP_ID, APISecret=API_SECRET, APIKey=API_KEY, AudioFile='sound_track/output.pcm')

    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=_on_message, on_error=_on_error, on_close=_on_close, on_open=_create_on_open(wsParam))
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    return jsonify({'transcription': res[0]}), 200
    

def unit():
    app.run(port=5001)