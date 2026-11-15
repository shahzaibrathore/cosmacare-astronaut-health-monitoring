
"""Clinical rule engine tests."""

import math
import pytest

from app.engine import THRESHOLDS, _detect_alerts
from app.schemas import TelemetryCreate


# ============================================================
# HELPER FUNCTION
# ============================================================

def _mk(**overrides):
    base = {
        "crew_id": 1,
        "heart_rate": 75,
        "spo2": 98.0,
        "body_temp": 37.0,
        "systolic_bp": 120,
        "diastolic_bp": 80,
    }
    base.update(overrides)
    return TelemetryCreate(**base)


# ============================================================
# BASIC SPO2 TESTS
# ============================================================

@pytest.mark.parametrize(
    "spo2,expected",
    [
        (100.0, None),
        (95.0, None),
        (94.1, None),
        (94.0, "WARNING"),
        (93.0, "WARNING"),
        (90.1, "WARNING"),
        (90.0, "CRITICAL"),
        (89.9, "CRITICAL"),
        (80.0, "CRITICAL"),
    ],
)
def test_spo2_rules(spo2, expected):
    alerts = [
        a for a in _detect_alerts(_mk(spo2=spo2))
        if a.parameter == "spo2"
    ]

    if expected is None:
        assert alerts == []
    else:
        assert any(a.severity == expected for a in alerts)


# ============================================================
# BASIC HEART RATE TESTS
# ============================================================

@pytest.mark.parametrize(
    "hr,expected",
    [
        (75, None),
        (60, None),
        (50, None),
        (49, "WARNING"),
        (46, "WARNING"),
        (45, "WARNING"),
        (44, "CRITICAL"),
        (30, "CRITICAL"),
        (150, None),
        (151, "WARNING"),
        (159, "WARNING"),
        (160, "WARNING"),
        (161, "CRITICAL"),
        (220, "CRITICAL"),
    ],
)
def test_heart_rate_rules(hr, expected):
    alerts = [
        a for a in _detect_alerts(_mk(heart_rate=hr))
        if a.parameter == "heart_rate"
    ]

    if expected is None:
        assert alerts == []
    else:
        assert any(a.severity == expected for a in alerts)


# ============================================================
# BASIC TEMPERATURE TESTS
# ============================================================

@pytest.mark.parametrize(
    "temp,expected",
    [
        (37.0, None),
        (36.5, None),
        (35.5, None),
        (38.5, None),
        (38.6, "WARNING"),
        (38.9, "WARNING"),
        (39.0, "WARNING"),
        (39.1, "CRITICAL"),
        (42.0, "CRITICAL"),
        (35.4, "WARNING"),
        (35.1, "WARNING"),
        (35.0, "WARNING"),
        (34.9, "CRITICAL"),
        (33.0, "CRITICAL"),
    ],
)
def test_temperature_rules(temp, expected):
    alerts = [
        a for a in _detect_alerts(_mk(body_temp=temp))
        if a.parameter == "body_temp"
    ]

    if expected is None:
        assert alerts == []
    else:
        assert any(a.severity == expected for a in alerts)


# ============================================================
@pytest.mark.parametrize(
    "sys_,expected",
    [
        (120, None),
        (90, None),
        (160, None),
        (79, "CRITICAL"),
        (60, "CRITICAL"),
        (161, "CRITICAL"),
        (200, "CRITICAL"),
        (250, "CRITICAL"),
    ],
)
def test_systolic_rules(sys_, expected):
    alerts = [
        a for a in _detect_alerts(_mk(systolic_bp=sys_))
        if a.parameter == "systolic_bp"
    ]

    if expected is None:
        assert alerts == []
    else:
        assert any(a.severity == expected for a in alerts)


# ============================================================
# BASIC DIASTOLIC BP TESTS
# ============================================================

@pytest.mark.parametrize(
    "dia,expected",
    [
        (80, None),
        (60, None),
        (100, None),
        (49, "CRITICAL"),
        (40, "CRITICAL"),
        (101, "CRITICAL"),
        (150, "CRITICAL"),
    ],
)
def test_diastolic_rules(dia, expected):
    alerts = [
        a for a in _detect_alerts(_mk(diastolic_bp=dia))
        if a.parameter == "diastolic_bp"
    ]

    if expected is None:
        assert alerts == []
    else:
        assert any(a.severity == expected for a in alerts)


# ============================================================
# BASIC MULTIPLE ALERT TEST
# ============================================================

def test_multiple_alerts_detected():
    data = _mk(
        heart_rate=40,
        spo2=85.0,
        body_temp=40.0,
    )

    alerts = _detect_alerts(data)

    assert len(alerts) >= 3


def test_threshold_dictionary():
    assert THRESHOLDS["spo2_critical"] == 90.0
    assert THRESHOLDS["hr_low_critical"] == 45


# ============================================================
# 100 ADDITIONAL ADVANCED TEST CASES
# ============================================================

# 1. ADVANCED HEART RATE TESTS (20 CASES)

@pytest.mark.parametrize(
    "hr,expected",
    [
        (30, "CRITICAL"),
        (35, "CRITICAL"),
        (40, "CRITICAL"),
        (43, "CRITICAL"),
        (44, "CRITICAL"),
        (45, "WARNING"),
        (46, "WARNING"),
        (47, "WARNING"),
        (48, "WARNING"),
        (49, "WARNING"),
        (150, None),
        (151, "WARNING"),
        (155, "WARNING"),
        (159, "WARNING"),
        (160, "WARNING"),
        (161, "CRITICAL"),
        (170, "CRITICAL"),
        (180, "CRITICAL"),
        (200, "CRITICAL"),
        (220, "CRITICAL"),
    ],
)
def test_advanced_heart_rate_cases(hr, expected):
    alerts = [
        a for a in _detect_alerts(_mk(heart_rate=hr))
        if a.parameter == "heart_rate"
    ]

    if expected is None:
        assert alerts == []
    else:
        assert any(a.severity == expected for a in alerts)


# 2. ADVANCED SPO2 TESTS (20 CASES)

@pytest.mark.parametrize(
    "spo2,expected",
    [
        (80.0, "CRITICAL"),
        (85.0, "CRITICAL"),
        (88.0, "CRITICAL"),
        (89.0, "CRITICAL"),
        (90.0, "CRITICAL"),
        (90.1, "WARNING"),
        (91.0, "WARNING"),
        (92.0, "WARNING"),
        (93.0, "WARNING"),
        (94.0, "WARNING"),
        (94.1, None),
        (95.0, None),
        (96.0, None),
        (97.0, None),
        (98.0, None),
        (98.5, None),
        (99.0, None),
        (99.5, None),
        (99.9, None),
        (100.0, None),
    ],
)
def test_advanced_spo2_cases(spo2, expected):
    alerts = [
        a for a in _detect_alerts(_mk(spo2=spo2))
        if a.parameter == "spo2"
    ]

    if expected is None:
        assert alerts == []
    else:
        assert any(a.severity == expected for a in alerts)


# 3. ADVANCED BODY TEMPERATURE TESTS (20 CASES)

@pytest.mark.parametrize(
    "temp,expected",
    [
        (39.1, "CRITICAL"),
        (39.5, "CRITICAL"),
        (40.0, "CRITICAL"),
        (41.0, "CRITICAL"),
        (43.0, "CRITICAL"),
        (38.6, "WARNING"),
        (38.7, "WARNING"),
        (38.8, "WARNING"),
        (38.9, "WARNING"),
        (39.0, "WARNING"),
        (35.0, "WARNING"),
        (35.1, "WARNING"),
        (35.2, "WARNING"),
        (35.3, "WARNING"),
        (35.4, "WARNING"),
        (35.5, None),
        (36.0, None),
        (37.0, None),
        (38.0, None),
        (38.5, None),
    ],
)
def test_advanced_temperature_cases(temp, expected):
    alerts = [
        a for a in _detect_alerts(_mk(body_temp=temp))
        if a.parameter == "body_temp"
    ]

    if expected is None:
        assert alerts == []
    else:
        assert any(a.severity == expected for a in alerts)


# 4. ADVANCED BLOOD PRESSURE TESTS (20 CASES)

@pytest.mark.parametrize(
    "sys_,expected",
    [
        (60, "CRITICAL"),
        (65, "CRITICAL"),
        (70, "CRITICAL"),
        (75, "CRITICAL"),
        (79, "CRITICAL"),
        (161, "CRITICAL"),
        (170, "CRITICAL"),
        (180, "CRITICAL"),
        (200, "CRITICAL"),
        (250, "CRITICAL"),
    ],
)
def test_advanced_systolic_cases(sys_, expected):
    alerts = [
        a for a in _detect_alerts(_mk(systolic_bp=sys_))
        if a.parameter == "systolic_bp"
    ]

    assert any(a.severity == expected for a in alerts)


@pytest.mark.parametrize(
    "dia,expected",
    [
        (40, "CRITICAL"),
        (42, "CRITICAL"),
        (45, "CRITICAL"),
        (48, "CRITICAL"),
        (49, "CRITICAL"),
        (101, "CRITICAL"),
        (110, "CRITICAL"),
        (120, "CRITICAL"),
        (130, "CRITICAL"),
        (150, "CRITICAL"),
    ],
)
def test_advanced_diastolic_cases(dia, expected):
    alerts = [
        a for a in _detect_alerts(_mk(diastolic_bp=dia))
        if a.parameter == "diastolic_bp"
    ]

    assert any(a.severity == expected for a in alerts)


# 5. MULTIPLE ALERT DETECTION TESTS (10 CASES)

@pytest.mark.parametrize(
    "overrides,expected_parameters",
    [
        ({"heart_rate": 40}, {"heart_rate"}),
        ({"spo2": 85.0}, {"spo2"}),
        ({"body_temp": 40.0}, {"body_temp"}),
        ({"systolic_bp": 70}, {"systolic_bp"}),
        ({"diastolic_bp": 45}, {"diastolic_bp"}),
        (
            {"heart_rate": 40, "spo2": 85.0},
            {"heart_rate", "spo2"},
        ),
        (
            {"body_temp": 40.0, "systolic_bp": 170},
            {"body_temp", "systolic_bp"},
        ),
        (
            {"heart_rate": 170, "spo2": 90.0, "body_temp": 34.0},
            {"heart_rate", "spo2", "body_temp"},
        ),
        (
            {
                "heart_rate": 40,
                "spo2": 85.0,
                "body_temp": 40.0,
                "systolic_bp": 70,
                "diastolic_bp": 45,
            },
            {
                "heart_rate",
                "spo2",
                "body_temp",
                "systolic_bp",
                "diastolic_bp",
            },
        ),
        ({}, set()),
    ],
)
def test_advanced_multiple_alert_cases(overrides, expected_parameters):
    alerts = _detect_alerts(_mk(**overrides))

    actual_parameters = {a.parameter for a in alerts}

    assert actual_parameters == expected_parameters


# 6. NORMAL READINGS AND EDGE CASE TESTS (10 CASES)

@pytest.mark.parametrize(
    "overrides",
    [
        {"heart_rate": 75, "spo2": 98.0},
        {"heart_rate": 100, "spo2": 99.0},
        {"body_temp": 37.0},
        {"body_temp": 36.5, "heart_rate": 80},
        {"systolic_bp": 120, "diastolic_bp": 80},
        {"systolic_bp": 140, "diastolic_bp": 90},
        {"heart_rate": 100, "spo2": 97.5, "body_temp": 37.2},
        {"heart_rate": 60, "spo2": 95.0, "body_temp": 36.0},
        {
            "heart_rate": 90,
            "spo2": 98.5,
            "body_temp": 37.5,
            "systolic_bp": 130,
            "diastolic_bp": 85,
        },
        {
            "heart_rate": 75,
            "spo2": 96.0,
            "body_temp": 35.5,
            "systolic_bp": 160,
            "diastolic_bp": 100,
        },
    ],
)
def test_advanced_normal_readings(overrides):
    alerts = _detect_alerts(_mk(**overrides))

    assert alerts == []


# ============================================================
# COSMACARE - 1000 ADVANCED AUTOMATED TEST CASES
# ============================================================

def get_expected_heart_rate(value):
    if value < 45 or value > 160:
        return "CRITICAL"
    elif value < 50 or value > 150:
        return "WARNING"
    return None


def get_expected_spo2(value):
    if value <= 90:
        return "CRITICAL"
    elif value <= 94:
        return "WARNING"
    return None


def get_expected_temperature(value):
    if value < 35 or value > 39:
        return "CRITICAL"
    elif value < 35.5 or value > 38.5:
        return "WARNING"
    return None


def get_expected_systolic(value):
    if value < 80 or value > 160:
        return "CRITICAL"
    return None


def get_expected_diastolic(value):
    if value < 50 or value > 100:
        return "CRITICAL"
    return None


# Generate exactly 1000 test cases:
# 200 Heart Rate + 200 SpO2 + 200 Temperature
# + 200 Systolic BP + 200 Diastolic BP

TEST_CASES_1000 = []

# Heart Rate: values remain between 30 and 220.
for i in range(200):
    value = 30 + (i % 191)
    TEST_CASES_1000.append(
        ("heart_rate", value, get_expected_heart_rate(value))
    )

# SpO2: values remain between 70 and 100.
for i in range(200):
    value = round(70 + (i % 151) * 0.2, 2)
    TEST_CASES_1000.append(
        ("spo2", value, get_expected_spo2(value))
    )

# Temperature: values remain between 33 and 42.95.
for i in range(200):
    value = round(33 + i * 0.05, 2)
    TEST_CASES_1000.append(
        ("body_temp", value, get_expected_temperature(value))
    )

# Systolic BP: valid range 60 to 250.
for i in range(200):
    value = 60 + (i % 191)
    TEST_CASES_1000.append(
        ("systolic_bp", value, get_expected_systolic(value))
    )

# Diastolic BP: valid range 40 to 150.
for i in range(200):
    value = 40 + (i % 111)
    TEST_CASES_1000.append(
        ("diastolic_bp", value, get_expected_diastolic(value))
    )


@pytest.mark.parametrize(
    "parameter,value,expected",
    TEST_CASES_1000,
    ids=[
        f"{parameter}_{value}"
        for parameter, value, expected in TEST_CASES_1000
    ],
)
def test_1000_advanced_health_monitoring_cases(
    parameter, value, expected
):
    data = _mk(**{parameter: value})

    alerts = _detect_alerts(data)

    matching_alerts = [
        alert for alert in alerts
        if alert.parameter == parameter
    ]

    if expected is None:
        assert matching_alerts == [], (
            f"{parameter}={value}: Expected no alert, "
            f"but received {matching_alerts}"
        )
    else:
        assert any(
            alert.severity == expected
            for alert in matching_alerts
        ), (
            f"{parameter}={value}: Expected {expected}, "
            f"received {matching_alerts}"
        )


def test_exactly_1000_cases_generated():
    assert len(TEST_CASES_1000) == 1000


# ============================================================
# COSMACARE - 10,000 ADVANCED AUTOMATED TEST CASES
# ============================================================

def expected_hr(v):
    if v < 45 or v > 160:
        return "CRITICAL"
    if v < 50 or v > 150:
        return "WARNING"
    return None


def expected_spo2(v):
    if v <= 90:
        return "CRITICAL"
    if v <= 94:
        return "WARNING"
    return None


def expected_temp(v):
    if v < 35 or v > 39:
        return "CRITICAL"
    if v < 35.5 or v > 38.5:
        return "WARNING"
    return None


def expected_sys(v):
    if v < 80 or v > 160:
        return "CRITICAL"
    return None


def expected_dia(v):
    if v < 50 or v > 100:
        return "CRITICAL"
    return None


def get_expected(parameter, value):
    rules = {
        "heart_rate": expected_hr,
        "spo2": expected_spo2,
        "body_temp": expected_temp,
        "systolic_bp": expected_sys,
        "diastolic_bp": expected_dia,
    }
    return rules[parameter](value)


# Generate 10,000 deterministic health scenarios.
# Every scenario checks all five health parameters.

ADVANCED_CASES = []

for i in range(10000):
    heart_rate = 40 + ((i * 37) % 131)

    spo2 = round(85 + ((i * 17) % 151) / 10, 1)

    body_temp = round(34 + ((i * 13) % 61) / 10, 1)

    systolic_bp = 70 + ((i * 19) % 101)

    diastolic_bp = 40 + ((i * 23) % 71)

    ADVANCED_CASES.append({
        "crew_id": 1,
        "heart_rate": heart_rate,
        "spo2": spo2,
        "body_temp": body_temp,
        "systolic_bp": systolic_bp,
        "diastolic_bp": diastolic_bp,
    })


@pytest.mark.parametrize(
    "case_number,scenario",
    list(enumerate(ADVANCED_CASES, start=1)),
    ids=[
        f"CosmaCare_Scenario_{i}"
        for i in range(1, 10001)
    ],
)
def test_10000_advanced_health_scenarios(case_number, scenario):
    data = _mk(**scenario)

    alerts = _detect_alerts(data)

    parameters = [
        "heart_rate",
        "spo2",
        "body_temp",
        "systolic_bp",
        "diastolic_bp",
    ]

    for parameter in parameters:
        value = scenario[parameter]
        expected = get_expected(parameter, value)

        matching_alerts = [
            alert for alert in alerts
            if alert.parameter == parameter
        ]

        if expected is None:
            assert matching_alerts == [], (
                f"Scenario {case_number}: Unexpected alert "
                f"for {parameter}={value}"
            )
        else:
            assert any(
                alert.severity == expected
                for alert in matching_alerts
            ), (
                f"Scenario {case_number}: {parameter}={value}, "
                f"Expected={expected}, Actual={matching_alerts}"
            )


def test_total_generated_scenarios():
    assert len(ADVANCED_CASES) == 10000


def test_all_scenarios_have_five_health_parameters():
    for scenario in ADVANCED_CASES:
        assert all(
            key in scenario
            for key in [
                "heart_rate",
                "spo2",
                "body_temp",
                "systolic_bp",
                "diastolic_bp",
            ]
        )


def test_all_generated_values_are_finite():
    for scenario in ADVANCED_CASES:
        for parameter in [
            "heart_rate",
            "spo2",
            "body_temp",
            "systolic_bp",
            "diastolic_bp",
        ]:
            assert math.isfinite(scenario[parameter])


