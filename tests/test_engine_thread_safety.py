"""
Regression test for a thread-local Swiss Ephemeris sidereal-mode bug.

swe.set_sid_mode(SIDM_LAHIRI) is set once at src/engine.py import time, but
pyswisseph keeps that mode thread-local in the underlying C library, not
process-global. FastAPI/Starlette runs every sync `def` route handler in a
worker thread pool, so any live (non-DB) panchang computed inside a request
handler was silently running under Swiss Ephemeris's *default* sidereal
mode (Fagan-Bradley) instead of Lahiri. A constant ayanamsa offset cancels
out of moon-sun differences, so tithi/karana were unaffected — but
nakshatra, soura_masa, chandra_masa, and yoga (absolute-longitude or
sum-based) were all quietly wrong whenever served off the main thread,
which in production is virtually always.

Fixed by having _sun_longitude/_moon_longitude call swe.set_sid_mode() on
every invocation (src.engine._set_lahiri_mode) rather than relying on
which thread happened to first import the module.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

from src.engine import compute_panchang


def test_compute_panchang_identical_from_a_worker_thread():
    """The exact reproduction: a plain ThreadPoolExecutor call (what
    FastAPI/Starlette uses under the hood for sync route handlers) must
    give byte-identical results to a main-thread call."""

    def compute():
        return compute_panchang(date(2026, 9, 19))

    main_result = compute()
    with ThreadPoolExecutor(max_workers=1) as ex:
        worker_result = ex.submit(compute).result()

    assert worker_result == main_result


def test_compute_panchang_identical_from_a_worker_thread_no_prior_import():
    """Stronger form: a *fresh* worker thread that has never touched
    swisseph before, for a handful of dates including ones with no
    sunrise (fallback anchor) and both edges of the seeded range."""
    dates = [date(2026, 9, 19), date(2026, 1, 18), date(2020, 1, 1), date(2030, 12, 31)]

    def compute_all():
        return [compute_panchang(d) for d in dates]

    main_results = compute_all()
    with ThreadPoolExecutor(max_workers=1) as ex:
        worker_results = ex.submit(compute_all).result()

    for d, main_r, worker_r in zip(dates, main_results, worker_results):
        assert worker_r == main_r, f"mismatch for {d}"
