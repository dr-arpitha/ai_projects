import time
import asyncio

async def count():
    print("One")
    await asyncio.sleep(1)
    print("Two")
    await asyncio.sleep(1)

async def counter():
    # for _ in range(3):
        await asyncio.gather(count(), count(), count())

if __name__ == "__main__":
    print("Learning asyncio usage")
    start_time = time.perf_counter()
    asyncio.run(counter())
    elapsed_time = time.perf_counter() - start_time
    print(f"{__file__} took {elapsed_time : 0.2f} seconds to complete")

