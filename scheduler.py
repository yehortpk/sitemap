import asyncio
import queue
import time
from urllib.parse import urlparse

from config import ScrapperConfig
from executor import TaskExecutor


class Scheduler:
    def __init__(self):
        self._queue = queue.Queue()
        self._host_last_request: dict[str, float] = {}
        self._visited = set()
        self._executor = TaskExecutor()
        self._tasks = []

    def enqueue(self, url: str):
        if url not in self._visited:
            self._queue.put(url)
            self._visited.add(url)

    def add_links_to_queue(self, task: asyncio.Task[dict[str, set[str]]]) -> None:
        """
        Done callback for _executor.handle_request(url). Adds parsed links
        from the `url` page
        :param task: executed task
        :return:
        """
        result = task.result()
        for domain in result:
            for link in result[domain]:
                self.enqueue(link)

    async def run(self):
        while self._queue:
            url = self._queue.get()

            scrapper_config = ScrapperConfig(url)
            hostname = urlparse(url).hostname

            now = time.monotonic()
            last_request = self._host_last_request.get(hostname, now)
            next_allowed_time = last_request + scrapper_config.interval_ms/1000

            # Sleep if necessary to respect the interval
            if now < next_allowed_time:
                await asyncio.sleep(next_allowed_time - now)

            # Schedule the task
            task = asyncio.create_task(self._executor.fetch_links(url))
            self._tasks.append(task)
            task.add_done_callback(self.add_links_to_queue)

            # Update last request time for the host
            self._host_last_request[hostname] = time.monotonic()

            await asyncio.gather(*self._tasks)
