import asyncio
import time
import statistics
import httpx

URL = "http://127.0.0.1:8000/telemetry/"
TOTAL_REQUESTS = 1000
CONCURRENCY = 100

PAYLOAD = {
    "crew_id": 1,
    "heart_rate": 75,
    "spo2": 98.0,
    "body_temp": 37.0,
    "systolic_bp": 120,
    "diastolic_bp": 80
}

async def main():
    limits = httpx.Limits(
        max_connections=CONCURRENCY,
        max_keepalive_connections=CONCURRENCY
    )

    timeout = httpx.Timeout(60.0)

    async with httpx.AsyncClient(
        limits=limits,
        timeout=timeout
    ) as client:

        print("Preparing test database...")

        # Ensure crew exists before concurrent requests
        response = await client.post(URL, json=PAYLOAD)

        if response.status_code != 201:
            print("Setup failed:", response.status_code, response.text)
            return

        print("Starting 100 concurrent requests...")

        latencies = []
        results = []

        async def send_request():
            start = time.perf_counter()

            try:
                response = await client.post(URL, json=PAYLOAD)
                elapsed = time.perf_counter() - start

                latencies.append(elapsed)
                results.append(response.status_code)

                if response.status_code != 201:
                    print("HTTP error:", response.status_code, response.text[:150])

            except Exception as error:
                elapsed = time.perf_counter() - start
                latencies.append(elapsed)
                results.append("ERROR")
                print(f"Request error: {type(error).__name__}: {error!r}")

        start_time = time.perf_counter()

        await asyncio.gather(
            *(send_request() for _ in range(TOTAL_REQUESTS))
        )

        total_time = time.perf_counter() - start_time

    successful = sum(1 for x in results if x == 201)
    failed = TOTAL_REQUESTS - successful

    sorted_times = sorted(latencies)

    def percentile(p):
        index = min(int(len(sorted_times) * p), len(sorted_times) - 1)
        return sorted_times[index] * 1000

    print("\n========== COSMACARE LOAD TEST ==========")
    print("Total requests       :", TOTAL_REQUESTS)
    print("Concurrent requests  :", CONCURRENCY)
    print("Successful requests  :", successful)
    print("Failed requests      :", failed)
    print("Total time           :", round(total_time, 3), "seconds")
    print("Requests per second  :", round(successful / total_time, 2))
    print("Average response     :", round(statistics.mean(latencies) * 1000, 2), "ms")
    print("Median response      :", round(statistics.median(latencies) * 1000, 2), "ms")
    print("95th percentile      :", round(percentile(0.95), 2), "ms")
    print("Maximum response     :", round(max(latencies) * 1000, 2), "ms")
    print("=========================================")

asyncio.run(main())



