import contextlib
import cStringIO
import sys
import threading
import time
import unittest

import enaml


@contextlib.contextmanager
def redirect_stderr(new_stderr=None):
    """
    Context manager to temporarily redirect stderr output
    to another source.  If given, 'new_stderr' should be a file-like object.

    """
    if new_stderr is None:
        new_stderr = cStringIO.StringIO()
    old_stderr = sys.stderr
    sys.stderr = new_stderr
    try:
        yield new_stderr
    finally:
        sys.stderr = old_stderr


class TestQtApplication(unittest.TestCase):
    def test_exceptions_in_scheduled_tasks(self):

        success = threading.Event()

        def on_success(app):
            success.set()
            app._qt_app.exit()

        def on_failure(app):
            app._qt_app.exit()

        def main(app):
            time.sleep(0.5)
            for _ in xrange(10):
                app.schedule(lambda: 1/0)
            time.sleep(0.5)
            app.schedule(on_success, (app,))

        app = enaml.default_toolkit().app
        app.initialize()

        # Ensure we eventually exit the UI mainloop even if the test fails.
        app.timer(10000, on_failure, app)
        t = threading.Thread(target=main, args=(app,))
        app.schedule(t.start)

        with redirect_stderr():
            app.start_event_loop()

        self.assertTrue(
            success.is_set(),
            "scheduled task not executed",
        )


if __name__ == '__main__':
    unittest.main()
