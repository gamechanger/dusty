"""Utilities for multithreaded parallel execution of tasks."""

import threading
import multiprocessing
from contextlib import contextmanager
from Queue import Queue

from .log import log_to_client

class TaskQueue(Queue, object):
    """Executable task queue used for multithreaded execution of multiple
    function calls. Concurrency is limited by `pool_size`."""
    def __init__(self, pool_size):
        super(TaskQueue, self).__init__()
        self.threads = []
        self.errors = []
        self.pool_semaphore = threading.Semaphore(pool_size)

    def enqueue_task(self, fn, *args, **kwargs):
        self.put((fn, args, kwargs))

    def _task_executor(self, fn, args, kwargs):
        try:
            fn(*args, **kwargs)
        except Exception as e:
            self.errors.append(e.message)
        finally:
            self.pool_semaphore.release()

    def execute(self):
        while not self.empty():
            self.pool_semaphore.acquire()
            fn, args, kwargs = self.get()
            thread = threading.Thread(target=self._task_executor,
                                            args=(fn, args, kwargs))
            self.threads.append(thread)
            thread.daemon = True
            thread.start()

        for thread in self.threads:
            thread.join()

        if self.errors:
            for error in self.errors:
                log_to_client(error)
            raise RuntimeError("Exceptions encountered during parallel task execution")

@contextmanager
def parallel_task_queue(pool_size=multiprocessing.cpu_count()*2):
    """Context manager for setting up a TaskQueue. Upon leaving the
    context manager, all tasks that were enqueued will be executed
    in parallel subject to `pool_size` concurrency constraints."""
    task_queue = TaskQueue(pool_size)
    yield task_queue
    task_queue.execute()
