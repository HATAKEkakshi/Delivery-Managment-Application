import time 
from rich import print
import asyncio
async def endpoint(route:str)->str:
    print(f"Endpoint called {route}")
    await asyncio.sleep(2)
    return f"Response for {route}"
async def server():
    tests=(
        "GET /shipment?id=1",
        "POST /shipment",
        "PUT /shipment?id=1",
        "PATCH /shipment?id=1",
        "DELETE /shipment?id=1"
    )
    start=time.perf_counter()
    async with asyncio.TaskGroup() as task_group:
        tasks=[
            task_group.create_task(endpoint(route))
            for route in tests
            ]
        print(await tasks[0])
    end=time.perf_counter()
    print(f"Total time taken: {end - start:.2f} seconds")
#run the server
asyncio.run(
    server()
)