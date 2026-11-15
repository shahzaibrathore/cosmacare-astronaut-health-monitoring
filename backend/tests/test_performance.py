"""CosmaCare: Accuracy, Edge Cases, Performance and Memory Tests."""

import gc
import time
import tracemalloc

import pytest
from pydantic import ValidationError

from app.engine import _detect_alerts
from app.schemas import TelemetryCreate




TOTAL_SCENARIOS = 10_000_000


def make_data(**overrides):
    values = {
        "crew_id": 1,
        "heart_rate": 75,
        "spo2": 98.0,
        "body_temp": 37.0,
        "systolic_bp": 120,
        "diastolic_bp": 80,
    }
    values.update(overrides)
    return TelemetryCreate(**values)


def expected_alerts(data):
    expected = set()

    if data.spo2 <= 90:
        expected.add(("spo2", "CRITICAL"))
    elif data.spo2 <= 94:
        expected.add(("spo2", "WARNING"))

    if data.heart_rate < 45:
        expected.add(("heart_rate", "CRITICAL"))
    elif data.heart_rate < 50:
        expected.add(("heart_rate", "WARNING"))
    elif data.heart_rate > 160:
        expected.add(("heart_rate", "CRITICAL"))
    elif data.heart_rate > 150:
        expected.add(("heart_rate", "WARNING"))

    if data.body_temp > 39:
        expected.add(("body_temp", "CRITICAL"))
    elif data.body_temp > 38.5:
        expected.add(("body_temp", "WARNING"))
    elif data.body_temp < 35:
        expected.add(("body_temp", "CRITICAL"))
    elif data.body_temp < 35.5:
        expected.add(("body_temp", "WARNING"))

    if data.systolic_bp < 80 or data.systolic_bp > 160:
        expected.add(("systolic_bp", "CRITICAL"))

    if data.diastolic_bp < 50 or data.diastolic_bp > 100:
        expected.add(("diastolic_bp", "CRITICAL"))

    return expected


def actual_alerts(data):
    return {
        (alert.parameter, alert.severity)
        for alert in _detect_alerts(data)
    }


# BOUNDARY AND THRESHOLD TESTS

@pytest.mark.parametrize(
    "field,values",
    [
        ("heart_rate", [30, 44, 45, 49, 50, 150, 151, 160, 161, 220]),
        ("spo2", [50, 89.9, 90, 90.1, 94, 94.1, 100]),
        ("body_temp", [30, 34.9, 35, 35.4, 35.5, 38.5, 38.6, 39, 39.1, 43]),
        ("systolic_bp", [60, 79, 80, 160, 161, 250]),
        ("diastolic_bp", [40, 49, 50, 100, 101, 150]),
    ],
)
def test_threshold_boundaries(field, values):
    for value in values:
        data = make_data(**{field: value})
        assert actual_alerts(data) == expected_alerts(data)


# INVALID INPUT VALIDATION TESTS

@pytest.mark.parametrize(
    "field,value",
    [
        ("heart_rate", 29),
        ("heart_rate", 221),
        ("spo2", 49.9),
        ("spo2", 100.1),
        ("body_temp", 29.9),
        ("body_temp", 43.1),
        ("systolic_bp", 59),
        ("systolic_bp", 251),
        ("diastolic_bp", 39),
        ("diastolic_bp", 151),
        ("crew_id", 0),
    ],
)
def test_invalid_values_rejected(field, value):
    with pytest.raises(ValidationError):
        make_data(**{field: value})


# ONE MILLION SCENARIO BENCHMARK

def test_one_million_scenario_benchmark():
    gc.collect()

    tracemalloc.start()
    start_time = time.perf_counter()

    checked = 0
    failed = 0
    failure_examples = []

    for i in range(TOTAL_SCENARIOS):
        data = TelemetryCreate(
            crew_id=1,
            heart_rate=30 + ((i * 37) % 191),
            spo2=round(50 + ((i * 17) % 501) / 10, 1),
            body_temp=round(30 + ((i * 13) % 131) / 10, 1),
            systolic_bp=60 + ((i * 19) % 191),
            diastolic_bp=40 + ((i * 23) % 111),
        )

        expected = expected_alerts(data)
        actual = actual_alerts(data)

        if expected != actual:
            failed += 1

            if len(failure_examples) < 10:
                failure_examples.append(
                    (i + 1, expected, actual)
                )

        checked += 1

    elapsed = time.perf_counter() - start_time

    current_memory, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    speed = checked / elapsed if elapsed else 0

    print("\n")
    print("=" * 60)
    print("          COSMACARE BENCHMARK REPORT")
    print("=" * 60)
    print(f"Total scenarios       : {checked:,}")
    print(f"Passed scenarios      : {checked - failed:,}")
    print(f"Failed scenarios      : {failed:,}")
    print(f"Execution time        : {elapsed:.2f} seconds")
    print(f"Processing speed      : {speed:,.2f} scenarios/sec")
    print(f"Current Python memory : {current_memory / 1024**2:.2f} MB")
    print(f"Peak Python memory    : {peak_memory / 1024**2:.2f} MB")

    if failure_examples:
        print("\nFIRST FAILURE EXAMPLES:")
        for number, expected, actual in failure_examples:
            print(
                f"Scenario {number}: "
                f"Expected={expected}, Actual={actual}"
            )

    print("-" * 60)
    print("ACCURACY RESULT       :", "PASS" if failed == 0 else "FAIL")
    print("=" * 60)

    assert checked == TOTAL_SCENARIOS
    assert failed == 0


def test_generated_scenarios_stay_within_schema_limits():
    for i in range(1000):
        data = TelemetryCreate(
            crew_id=1,
            heart_rate=30 + ((i * 37) % 191),
            spo2=round(50 + ((i * 17) % 501) / 10, 1),
            body_temp=round(30 + ((i * 13) % 131) / 10, 1),
            systolic_bp=60 + ((i * 19) % 191),
            diastolic_bp=40 + ((i * 23) % 111),
        )

        assert 30 <= data.heart_rate <= 220
        assert 50 <= data.spo2 <= 100
        assert 30 <= data.body_temp <= 43
        assert 60 <= data.systolic_bp <= 250
        assert 40 <= data.diastolic_bp <= 150
