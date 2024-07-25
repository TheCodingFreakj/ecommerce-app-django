from line_profiler import LineProfiler
import functools

def profile_view(func):
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        profiler = LineProfiler()
        profiler.add_function(func)
        profiler.enable_by_count()
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable_by_count()
            profiler.print_stats()
        return result
    return sync_wrapper


