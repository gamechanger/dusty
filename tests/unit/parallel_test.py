from mock import Mock, call

from ..testcases import DustyTestCase
from dusty.parallel import TaskQueue, parallel_task_queue

global_mock = Mock()

def _fake_task(*args, **kwargs):
    global_mock(*args, **kwargs)

def _fake_exception(*args, **kwargs):
    raise ValueError()

class TestParallel(DustyTestCase):
    def setUp(self):
        super(TestParallel, self).setUp()
        self.queue = TaskQueue(2)
        global_mock.reset_mock()

    def test_enqueue_task(self):
        self.queue.enqueue_task(_fake_task, 1, 2, a=3, b=4)
        fn, args, kwargs = self.queue.get()
        self.assertEqual(fn, _fake_task)
        self.assertEqual(args, (1, 2))
        self.assertItemsEqual(kwargs, {'a': 3, 'b': 4})

    def test_task_executor(self):
        self.queue._task_executor(_fake_task, (1,), {'a': 2})
        global_mock.assert_called_with(1, a=2)

    def test_task_executor_exception(self):
        self.queue._task_executor(_fake_exception, tuple(), {})
        self.assertEqual(len(self.queue.errors), 1)

    def test_execute_single(self):
        self.queue.enqueue_task(_fake_task, 1, a=2)
        self.queue.execute()
        global_mock.assert_called_with(1, a=2)

    def test_execute_multiple(self):
        self.queue.enqueue_task(_fake_task, 1, a=2)
        self.queue.enqueue_task(_fake_task, 3, b=4)
        self.queue.execute()
        global_mock.assert_has_calls([call(1, a=2),
                                      call(3, b=4)], any_order=True)

    def test_execute_with_exceptions(self):
        self.queue.enqueue_task(_fake_task, 1, a=2)
        self.queue.enqueue_task(_fake_exception)
        with self.assertRaises(RuntimeError):
            self.queue.execute()

    def test_context_manager(self):
        with parallel_task_queue() as queue:
            queue.enqueue_task(_fake_task, 1, a=2)
            queue.enqueue_task(_fake_task, 3, b=4)
        global_mock.assert_has_calls([call(1, a=2),
                                      call(3, b=4)], any_order=True)

    def test_context_manager_exception(self):
        with self.assertRaises(RuntimeError):
            with parallel_task_queue() as queue:
                queue.enqueue_task(_fake_task, 1, a=2)
                queue.enqueue_task(_fake_exception)
