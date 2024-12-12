import redis
import json
from com.cgnpc.steady.S1BuildModel import build_model

# 连接到 Redis 服务
client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
# 消息监听器
pubsub = client.pubsub()

# 订阅 Java 发布的通道消息
pubsub.subscribe('topicA')


# 定义消费消息的函数
def consume_message():
    print("通道 'topicA' 已开启监听...")
    for message in pubsub.listen():
        try:
            # 消息格式是字典，处理消息
            if message['type'] == 'message':
                print(f"通道 'topicA' 接收到消息: {message['data']}")

                message_dict = json.loads(message['data'])

                # 获取 modelingRequestDTO 数据
                if "modelingRequestDTO" in message_dict:
                    modeling_request_dto = message_dict["modelingRequestDTO"]
                    # 调用算法的处理
                    # result = build_model(modeling_request_dto)
                    result = "ok"
                    # 将结果发布到另一个通道
                    client.publish('topicB', f"{result}")

        except Exception as e:
            # 捕获并记录异常，同时保持服务运行
            print(f"处理消息时发生异常: {e}")
            # 可选：将异常记录到日志文件或监控系统


# 开启监听消费
try:
    consume_message()
except KeyboardInterrupt:
    # 处理手动停止监听的情况
    print("监听已停止。")
except Exception as e:
    print(f"监听服务意外终止: {e}")
