import asyncio
import concurrent.futures
import time

def test(a):
    print("执行一个非常耗时的IO操作")
    time.sleep(2)
    return "暂停了{}秒".format(a)


URLS=[1,2,3,4,5,4,3,2,1]


if __name__ == '__main__':
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(test, url): url for url in URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print(' generated an exception: ' )
            else:
                print('%s' % data)


