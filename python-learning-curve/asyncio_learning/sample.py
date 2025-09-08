import asyncio

async def say_hello():
  print("Hello")
  await asyncio.sleep(1)
  print("World")

async def say_somethingelse():
  print("Welcome")
  await asyncio.sleep(1)
  print("to asyncio")

async def main():
  print("workings! of asyncio")
  await asyncio.gather(say_hello(),say_somethingelse())
  print("Bubye")

asyncio.run(main())
