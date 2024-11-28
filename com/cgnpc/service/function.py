from random import randint
from time import sleep

count = 0


def training_fun(filePath=None):
    global count  # 声明使用全局变量
    random_int = randint(5, 15)
    sleep(random_int)
    count += 1
    print(f"索引:{count},文件地址==>{filePath}正在处理算法当中预计处理时间:{random_int}m ...")
    return {"index": count, "processing_time": random_int}