import asyncio
import time

async def test(a):
    print("执行一个非常耗时的IO操作")
    time.sleep(2)
    return "暂停了{}秒".format(a)


def callback(future):
    print("正在执行回调函数，获取返回的结果是：", future.result())


if __name__ == '__main__':
    coroutine = test("2") # 生成一个协程对象
    coroutine2 = test("1") # 生成一个协程对象
    loop = asyncio.get_event_loop() # 定义事件循环对象
    task = loop.create_task(coroutine) # 将协程转换为task任务
    task2 = loop.create_task(coroutine2) # 将协程转换为task任务
    task.add_done_callback(callback)
    task2.add_done_callback(callback)
    tasks = [];
    tasks.append(task);
    tasks.append(task2);
    ga = asyncio.gather(
        *tasks
    )

    loop.run_until_complete(ga) # 将task任务扔进事件循环对象中触发


