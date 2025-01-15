import os, time

fifo_path = "/tmp/digest_fifo"

def reader(func):
    if not os.path.exists(fifo_path):
        os.mkfifo(fifo_path)
    with open(fifo_path, "r") as f:
        while True:
            msg = f.readline().strip()
            if msg:
                #print("Other program got:", msg)
                func(msg)

def writer(digest_msg):
    if not os.path.exists(fifo_path):
        os.mkfifo(fifo_path)
    with open(fifo_path, "w") as f:
        f.write(digest_msg + "\n")

if __name__ == "__main__":
    # 示例：启动reader或writer
    # reader()
    # time.sleep(5)
    # writer("digest received")
    pass