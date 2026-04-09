#!/usr/bin/env python3
"""
Stress test script for the survey application.

Simulates many concurrent participants completing the survey by interacting
with the API endpoints, mimicking the same flow as the real UI.

Usage:
    uv run python stress_test.py https://safepex.com --participants 50 --delay 0.5
    uv run python stress_test.py http://localhost:8000 -n 100 -d 0.2 --ramp 5
"""

import argparse
import asyncio
import random
import string
import time
from datetime import datetime, timezone
from dataclasses import dataclass, field

import httpx


@dataclass
class Stats:
    """Tracks request-level statistics."""

    total_requests: int = 0
    successful: int = 0
    failed: int = 0
    errors: list = field(default_factory=list)
    latencies: list = field(default_factory=list)
    participants_completed: int = 0
    participants_failed: int = 0
    start_time: float = 0.0

    def record(self, latency: float, success: bool, error: str = ""):
        self.total_requests += 1
        self.latencies.append(latency)
        if success:
            self.successful += 1
        else:
            self.failed += 1
            if error:
                self.errors.append(error)

    def summary(self) -> str:
        elapsed = time.time() - self.start_time
        lines = [
            "",
            "=" * 60,
            "  STRESS TEST RESULTS",
            "=" * 60,
            f"  Duration:              {elapsed:.1f}s",
            f"  Total HTTP requests:   {self.total_requests}",
            f"  Successful:            {self.successful}",
            f"  Failed:                {self.failed}",
            f"  Requests/sec:          {self.total_requests / elapsed:.1f}"
            if elapsed > 0
            else "",
            f"  Participants completed:{self.participants_completed}",
            f"  Participants failed:   {self.participants_failed}",
        ]
        if self.latencies:
            sorted_lat = sorted(self.latencies)
            n = len(sorted_lat)
            lines += [
                "",
                "  Latency (seconds):",
                f"    Min:    {sorted_lat[0]:.3f}",
                f"    Avg:    {sum(sorted_lat) / n:.3f}",
                f"    Median: {sorted_lat[n // 2]:.3f}",
                f"    p95:    {sorted_lat[int(n * 0.95)]:.3f}",
                f"    p99:    {sorted_lat[int(n * 0.99)]:.3f}",
                f"    Max:    {sorted_lat[-1]:.3f}",
            ]
        if self.errors:
            unique_errors: dict[str, int] = {}
            for e in self.errors:
                unique_errors[e] = unique_errors.get(e, 0) + 1
            lines += ["", "  Errors:"]
            for err, count in sorted(unique_errors.items(), key=lambda x: -x[1])[:10]:
                lines += [f"    [{count}x] {err}"]
        lines.append("=" * 60)
        return "\n".join(lines)


def random_participant_id() -> str:
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"stress_{suffix}"


async def timed_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    stats: Stats,
    **kwargs,
) -> tuple[bool, dict | list | None]:
    """Make an HTTP request, record timing and success."""
    t0 = time.time()
    try:
        resp = await client.request(method, url, **kwargs)
        latency = time.time() - t0
        if resp.status_code >= 400:
            stats.record(
                latency,
                False,
                f"HTTP {resp.status_code} on {method} {url}: {resp.text[:120]}",
            )
            return False, None
        stats.record(latency, True)
        try:
            return True, resp.json()
        except Exception:
            return True, None
    except Exception as e:
        latency = time.time() - t0
        stats.record(latency, False, f"{type(e).__name__}: {e}")
        return False, None


async def simulate_participant(
    base_url: str,
    client: httpx.AsyncClient,
    stats: Stats,
    answer_delay: float,
    participant_id: str | None = None,
    realistic: bool = False,
):
    """Simulate one participant completing the entire survey."""
    pid = participant_id or random_participant_id()
    api = base_url.rstrip("/")

    # Realistic mode: simulate a kid reading instructions, thinking, etc.
    if realistic:
        # Reading the start page + typing participant ID (3-8s)
        await asyncio.sleep(random.uniform(3.0, 8.0))

    # 1. Start survey - get questions
    ok, data = await timed_request(
        client,
        "POST",
        f"{api}/api/survey/start",
        stats,
        json={"participant_id": pid},
    )
    if not ok or not isinstance(data, list):
        stats.participants_failed += 1
        print(f"  [FAIL] {pid}: could not start survey")
        return

    questions = data
    practice = [q for q in questions if q.get("is_practice")]
    real = [q for q in questions if not q.get("is_practice")]

    print(f"  [{pid}] Got {len(practice)} practice + {len(real)} real questions")

    if realistic:
        # Reading the instructions page (5-15s, kids read at different speeds)
        await asyncio.sleep(random.uniform(5.0, 15.0))

    # 2. Simulate answering practice questions (not sent to API, same as real UI)
    for _ in practice:
        if realistic:
            # First time swiping, figuring out the UI (3-10s)
            await asyncio.sleep(random.uniform(3.0, 10.0))
        else:
            await asyncio.sleep(random.uniform(0.05, min(answer_delay, 0.3)))

    if realistic:
        # Reading "practice done" confirmation screen + clicking button (2-5s)
        await asyncio.sleep(random.uniform(2.0, 5.0))

    # 3. Start real session
    now = datetime.now(timezone.utc).isoformat()
    ok, _ = await timed_request(
        client,
        "POST",
        f"{api}/api/survey/session/start",
        stats,
        json={"participant_id": pid, "started_at": now},
    )
    if not ok:
        stats.participants_failed += 1
        print(f"  [FAIL] {pid}: could not start session")
        return

    session_start = time.time()

    # 4. Answer real questions one by one
    for q in real:
        if realistic:
            # Looking at the media (GIF/image), reading question, deciding (2-10s)
            # Some kids are fast decisive swipers, some deliberate
            delay = random.triangular(2.0, 10.0, 4.0)
        else:
            delay = random.uniform(0.05, answer_delay)
        await asyncio.sleep(delay)

        answer = random.choices(
            ["yes", "no", "skip"],
            weights=[45, 45, 10] if realistic else [1, 1, 1],
        )[0]
        duration_ms = int(delay * 1000) + random.randint(200, 2000)

        ok, _ = await timed_request(
            client,
            "POST",
            f"{api}/api/survey/answer",
            stats,
            json={
                "participant_id": pid,
                "question_id": q["id"],
                "answer": answer,
                "duration_ms": duration_ms,
            },
        )
        if not ok:
            print(f"  [WARN] {pid}: failed to answer question {q['id']}")

    # 5. Complete session
    completed_at = datetime.now(timezone.utc).isoformat()
    duration_ms = int((time.time() - session_start) * 1000)

    ok, _ = await timed_request(
        client,
        "POST",
        f"{api}/api/survey/session/complete",
        stats,
        json={
            "participant_id": pid,
            "completed_at": completed_at,
            "duration_ms": duration_ms,
        },
    )
    if ok:
        stats.participants_completed += 1
        print(f"  [DONE] {pid} completed in {duration_ms / 1000:.1f}s")
    else:
        stats.participants_failed += 1
        print(f"  [FAIL] {pid}: could not complete session")


async def run_stress_test(
    base_url: str,
    num_participants: int,
    answer_delay: float,
    ramp_seconds: float,
    concurrency: int,
    realistic: bool = False,
):
    stats = Stats(start_time=time.time())

    mode = "REALISTIC (classroom)" if realistic else "synthetic"
    print(f"\nStress test [{mode}]: {num_participants} participants against {base_url}")
    if realistic:
        print(
            "  Simulating: kids typing IDs, reading instructions, looking at media, swiping"
        )
        print(
            f"  Ramp-up: {ramp_seconds}s (teacher says 'go' and kids start gradually)"
        )
    else:
        print(
            f"  Answer delay: up to {answer_delay}s | Ramp-up: {ramp_seconds}s | Concurrency: {concurrency}"
        )
    print()

    limits = httpx.Limits(
        max_connections=concurrency,
        max_keepalive_connections=concurrency,
    )
    timeout = httpx.Timeout(120.0)

    async with httpx.AsyncClient(
        limits=limits, timeout=timeout, follow_redirects=True
    ) as client:
        # Connectivity check
        try:
            resp = await client.get(base_url, timeout=httpx.Timeout(10.0))
            print(f"  Server reachable (HTTP {resp.status_code})")
        except Exception as e:
            print(f"ERROR: Cannot connect to {base_url}: {e}")
            return

        # Launch participants with ramp-up delay
        tasks = []
        if realistic:
            # Realistic: kids don't all start at the same instant.
            # Some click right away, most within 5-10s, stragglers up to ramp_seconds.
            for i in range(num_participants):
                # Triangular distribution: most kids start early, few stragglers
                start_delay = random.triangular(0, ramp_seconds, ramp_seconds * 0.2)
                task = asyncio.create_task(
                    _delayed_participant(
                        start_delay,
                        base_url,
                        client,
                        stats,
                        answer_delay,
                        realistic=True,
                    )
                )
                tasks.append(task)
        else:
            ramp_delay = (
                ramp_seconds / max(num_participants - 1, 1) if ramp_seconds > 0 else 0
            )
            for i in range(num_participants):
                task = asyncio.create_task(
                    simulate_participant(base_url, client, stats, answer_delay)
                )
                tasks.append(task)
                if ramp_delay > 0 and i < num_participants - 1:
                    await asyncio.sleep(ramp_delay)

        await asyncio.gather(*tasks, return_exceptions=True)

    print(stats.summary())


async def _delayed_participant(delay: float, *args, **kwargs):
    """Wait then start a participant — used for realistic ramp-up."""
    await asyncio.sleep(delay)
    await simulate_participant(*args, **kwargs)


def main():
    parser = argparse.ArgumentParser(
        description="Stress test the survey application with simulated participants",
    )
    parser.add_argument("url", help="Base URL of the survey (e.g. https://safepex.com)")
    parser.add_argument(
        "-n",
        "--participants",
        type=int,
        default=20,
        help="Number of simulated participants (default: 20)",
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=1.0,
        help="Max delay between answers in seconds, simulating think time (default: 1.0)",
    )
    parser.add_argument(
        "--ramp",
        type=float,
        default=5.0,
        help="Ramp-up period in seconds to spread participant starts (default: 5.0)",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=50,
        help="Max concurrent TCP connections (default: 50)",
    )
    parser.add_argument(
        "--realistic",
        action="store_true",
        help="Simulate realistic human behavior (reading, thinking, swiping delays)",
    )
    args = parser.parse_args()

    asyncio.run(
        run_stress_test(
            base_url=args.url,
            num_participants=args.participants,
            answer_delay=args.delay,
            ramp_seconds=args.ramp,
            concurrency=args.concurrency,
            realistic=args.realistic,
        )
    )


if __name__ == "__main__":
    main()
