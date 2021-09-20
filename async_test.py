from threading import Thread
from threading import current_thread
from asyncio import Future
import asyncio
import time


async def asleep(sleep_for):
   future = Future()
   Thread(target=sync_sleep, args=(sleep_for, future)).start()
   await future


def sync_sleep(sleep_for, future):

   # sleep synchronously
   time.sleep(sleep_for)

   async def sleep_future_resolver():
       future.set_result(None)

   asyncio.run_coroutine_threadsafe(sleep_future_resolver(), loop)


if __name__ == "__main__":
   start = time.time()
   work = list()
   work.append(asleep(1))

   loop = asyncio.get_event_loop()
   loop.run_until_complete(asyncio.wait(work, return_when=asyncio.ALL_COMPLETED))
   print("main program exiting after running for {0}".format(time.time() - start))
