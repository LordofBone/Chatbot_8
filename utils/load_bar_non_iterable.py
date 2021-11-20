import concurrent.futures
import functools
import time

from tqdm import tqdm

"""
Thanks to:
https://stackoverflow.com/questions/59013308/python-progress-bar-for-non-loop-function
I added in 'description', 'leave=True' and 'ascii_bar=True' into the function parameters
"""


def progress_bar(expected_time, description, leave=True, increments=10, ascii_bar=True, colour_bar_set=None):
    def _progress_bar(func):

        def timed_progress_bar(future, expected_time_progress, increments_progress=increments):
            """
            Display progress bar for expected_time_progress seconds.
            Complete early if future completes.
            Wait for future if it doesn't complete in expected_time_progress.
            """
            interval = expected_time_progress / increments_progress

            with tqdm(total=increments_progress, postfix=description, leave=leave, ascii=ascii_bar,
                      colour=colour_bar_set, dynamic_ncols=True) as p_bar:
                for i in range(increments_progress - 1):
                    if future.done():
                        # finish the progress bar
                        # not sure if there's a cleaner way to do this?
                        p_bar.update(increments_progress - i)
                        return
                    else:
                        time.sleep(interval)
                        p_bar.update()
                # if the future still hasn't completed, wait for it.
                future.result()
                p_bar.update()

        @functools.wraps(func)
        def _func(*args, **kwargs):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(func, *args, **kwargs)
                timed_progress_bar(future, expected_time, increments)

            return future.result()

        return _func

    return _progress_bar
