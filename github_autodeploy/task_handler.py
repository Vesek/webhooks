from pydantic import FilePath, DirectoryPath
import asyncio
import subprocess
from models import Task

class TaskHandler:
    def __init__(self, max_queue_length=0):
        self.queue: asyncio.Queue[Task] = asyncio.Queue(max_queue_length) # Create a Queue of type 'Task' with max_queue_length
        asyncio.create_task(self.consumer())

    async def consumer(self):
        while True:
            task = await self.queue.get() # Wait for task
            subprocess.run([task.run], cwd=task.work_dir, shell=True) # Run the task and wait for it to complete
            self.queue.task_done() # Mark task as done
