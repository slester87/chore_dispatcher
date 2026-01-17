import time
import threading

class Snowflake:
    # Bit allocation
    TIMESTAMP_BITS = 41
    NODE_BITS = 10
    SEQ_BITS = 12

    MAX_NODE_ID = (1 << NODE_BITS) - 1
    MAX_SEQ = (1 << SEQ_BITS) - 1

    # Bit shifts
    NODE_SHIFT = SEQ_BITS
    TIME_SHIFT = NODE_BITS + SEQ_BITS

    # Custom epoch (Jan 1, 2024 UTC, change if you like)
    EPOCH_MS = 1704067200000

    def __init__(self, node_id: int):
        if not (0 <= node_id <= self.MAX_NODE_ID):
            raise ValueError("node_id out of range")

        self.node_id = node_id
        self.last_ts = -1
        self.sequence = 0
        self.lock = threading.Lock()

    def _now_ms(self) -> int:
        return int(time.time() * 1000)

    def _wait_next_ms(self, ts):
        while True:
            now = self._now_ms()
            if now > ts:
                return now

    def next_id(self) -> int:
        with self.lock:
            ts = self._now_ms()

            if ts < self.last_ts:
                raise RuntimeError("Clock moved backwards")

            if ts == self.last_ts:
                self.sequence = (self.sequence + 1) & self.MAX_SEQ
                if self.sequence == 0:
                    ts = self._wait_next_ms(ts)
            else:
                self.sequence = 0

            self.last_ts = ts

            return (
                ((ts - self.EPOCH_MS) << self.TIME_SHIFT)
                | (self.node_id << self.NODE_SHIFT)
                | self.sequence
            )

