"""Utilities for multithreaded parallel execution of tasks."""

import threading
import multiprocessing
import multiprocessing.pool
from contextlib import contextmanager
from Queue import Queue

from .log import log_to_client

class TaskQueue(Queue, object):
    """Executable task queue used for multithreaded execution of multiple
    function calls. Concurrency is limited by `pool_size`."""
    def __init__(self, pool_size):
        super(TaskQueue, self).__init__()
        self.pool_size = pool_size
        self.errors = []

    def enqueue_task(self, fn, *args, **kwargs):
        self.put((fn, args, kwargs))

    def _task_executor(self, fn, args, kwargs):
        try:
            fn(*args, **kwargs)
        except Exception as e:
            self.errors.append(e.message)

    def execute(self):
        self.pool = multiprocessing.pool.ThreadPool(self.pool_size)
        while not self.empty():
            fn, args, kwargs = self.get()
            self.pool.apply_async(self._task_executor, args=(fn, args, kwargs))
        self.pool.close()
        self.pool.join()

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
