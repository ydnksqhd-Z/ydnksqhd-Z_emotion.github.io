from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage

from flask import Flask, request, jsonify
import json

app = Flask(__name__)

#星火认知大模型Spark Max的URL值，其他版本大模型URL值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = '72cf37b5'
SPARKAI_API_SECRET = 'NTI4MmVjMDRlZTk5ZjIxMGUxNjhjYWY0'
SPARKAI_API_KEY = '851fbce2b48a1ccbb09ec76ba2a80258'
#星火认知大模型Spark Max的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'generalv3.5'

spark = ChatSparkLLM(
    spark_api_url=SPARKAI_URL,
    spark_app_id=SPARKAI_APP_ID,
    spark_api_key=SPARKAI_API_KEY,
    spark_api_secret=SPARKAI_API_SECRET,
    spark_llm_domain=SPARKAI_DOMAIN,
    streaming=False,
)

@app.route('/LLM', methods=['POST'])
def communicate():
    data = request.json
    words = data.get('words')
    messages = [ChatMessage(
        role="user",
        content=words
    )]
    handler = ChunkPrintHandler()
    a = spark.generate([messages], callbacks=[handler])
    return jsonify({'context': a.generations[0][0].text}), 200

app.run(port=5003)

