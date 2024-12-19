from pydantic import FilePath, DirectoryPath
from models import Script
import asyncio
import logging

class Task:
    def __init__(self, script: Script, uuid: str):
        self.script = script
        self.uuid = uuid

class TaskHandler:
    def __init__(self, logger: logging.Logger, max_queue_length=0):
        self.queue: asyncio.Queue[Task] = asyncio.Queue(max_queue_length) # Create a Queue of type 'Task' with max_queue_length
        self.logger = logger
        asyncio.create_task(self.consumer())

    async def consumer(self):
        while True:
            task = await self.queue.get() # Wait for task
            self.logger.info(f"Task {task.uuid} - started processing")
            process = await asyncio.create_subprocess_shell(str(task.script.run), cwd=task.script.work_dir, stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE) # Run the task and wait for it to complete, then get the returned process
            _, stderr = await process.communicate()
            if process.returncode == 0:
                self.logger.info(f"Task {task.uuid} - successfuly completed")
            else:
                self.logger.error(f"Task {task.uuid} - ended with an error!")
                if stderr is not None:
                    self.logger.error(f"Task {task.uuid} - START OF ERROR:")
                    for line in stderr.decode('utf-8').strip().split("\n"):
                        self.logger.error(f"Task {task.uuid} - {line}")
                    self.logger.error(f"Task {task.uuid} - END OF ERROR")
            self.queue.task_done() # Mark task as done
