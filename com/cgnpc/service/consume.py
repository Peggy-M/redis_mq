import redis

from com.cgnpc.service.function import training_fun

# 连接到 Redis 服务
client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
# 消息监听器
pubsub = client.pubsub()

# 订阅 java 发布的通道消息
pubsub.subscribe('topicA')


# 定义消费消息的函数
def consume_message():
    print("通道'topicA'已开启了监听...")
    for message in pubsub.listen():
        # 消息格式是字典，处理消息
        if message['type'] == 'message':
            print(f"通道'topicA'接收到消息:{message['data']}")
            result = training_fun(message['data'])  # 调用算法的处理
            client.publish('topicB', f'模型-{result.get("index")}训练完成,耗时:{result.get("processing_time")}m')

# 开启监听消费
consume_message()
