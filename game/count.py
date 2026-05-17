import time
import threading


class GameCounter:
    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.move_count = 0
        self.is_running = False
        self._timer_thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            self.start_time = time.time()
            self.elapsed_time = 0
            self.move_count = 0
            self.is_running = True
            self._stop_event.clear()
            self._timer_thread = threading.Thread(target=self._update_timer, daemon=True)
            self._timer_thread.start()

    def stop(self):
        with self._lock:
            self.is_running = False
            self._stop_event.set()
            if self._timer_thread:
                self._timer_thread.join(timeout=1)

    def _update_timer(self):
        while not self._stop_event.is_set():
            if self.start_time and self.is_running:
                self.elapsed_time = time.time() - self.start_time
            time.sleep(0.1)

    def increment_move(self):
        with self._lock:
            self.move_count += 1

    def get_time(self):
        with self._lock:
            return self.elapsed_time

    def get_moves(self):
        with self._lock:
            return self.move_count

    def get_formatted_time(self):
        seconds = int(self.get_time())
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def reset(self):
        self.stop()
        self.elapsed_time = 0
        self.move_count = 0
        self.is_running = False
