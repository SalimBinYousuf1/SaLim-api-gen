import time
from typing import Dict


class APIThrottler:
    def __init__(self, rate_limit: int, time_period: int):
        self.rate_limit = rate_limit
        self.time_period = time_period
        self.request_times: Dict[str, float] = {}

    def throttle(self, endpoint: str):
        current_time = time.time()
        if endpoint in self.request_times:
            time_passed = current_time - self.request_times[endpoint]
            if time_passed < self.time_period:
                time_to_wait = self.time_period - time_passed
                time.sleep(time_to_wait)

        self.request_times[endpoint] = time.time()


class DynamicAPIThrottler(APIThrottler):
    def __init__(self, initial_rate_limit: int, initial_time_period: int):
        super().__init__(initial_rate_limit, initial_time_period)
        self.successful_requests = 0
        self.failed_requests = 0

    def update_rate_limit(self):
        success_rate = (
            self.successful_requests / (self.successful_requests + self.failed_requests)
            if (self.successful_requests + self.failed_requests) > 0
            else 1
        )
        if success_rate > 0.95:
            self.rate_limit = min(
                self.rate_limit * 2, 100
            )  # Increase rate limit, max 100 requests per period
        elif success_rate < 0.8:
            self.rate_limit = max(
                self.rate_limit // 2, 1
            )  # Decrease rate limit, min 1 request per period

    def throttle(self, endpoint: str):
        super().throttle(endpoint)
        self.update_rate_limit()

    def record_request_result(self, success: bool):
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
