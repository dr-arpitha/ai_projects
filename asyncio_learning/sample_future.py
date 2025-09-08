import asyncio

async def do_something(future, data):
   await asyncio.sleep(1)
   if(data == "success"):
     future.set_result("Operation succeeded")
   else:
     future.set_exception(RuntimeError("Failure"))

# A callback function to be called when the Future is done
def future_callback(future):
   try:
     print(f"Result: {future.result()}")
   except:
     print(f"Exception: {future.exception}")

async def main():
  future = asyncio.Future()
  future.add_done_callback(future_callback) 
  await asyncio.gather(do_something(future, "uccess"))
  if future.done():
    try:
        print(f"main result: {future.result()}")
    except Exception as ex:
        print(f"main Exception: {ex}")
        print("Callback: ",ex)

asyncio.run(main())
