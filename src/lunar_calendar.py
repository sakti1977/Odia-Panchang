"""
Lunar-month structure for the panji: new moons, Amanta months with Adhika,
Purnimanta labels, tithi intervals and sankranti instants.

Month naming (standard panji rule, Surya-Siddhanta tradition)
-------------------------------------------------------------
An Amanta lunar month runs new moon → new moon and is named by the solar
transit (sankranti) that falls inside it:

    sidereal sign of the Sun at the month's opening new moon = r
    Amanta month index (Chaitra = 0)                         = (r + 1) % 12

  e.g. Sun in Meena (11) at the new moon → Chaitra (0).
  If the Sun is in the same sign at the opening and the closing new moon,
  no sankranti fell inside: that month is **Adhika** and shares its name
  with the following (nija) month. Festivals are never observed in Adhika.

Purnimanta (the Odia panji convention used by this product): the Shukla
paksha keeps the Amanta name; the Krishna paksha takes the *next* month's
name (it belongs to the month that closes at the next Purnima).

This replaced an older "Sun's sign at the closing Purnima" heuristic that was
a month off whenever the Sun sat near a sign boundary at full moon — which is
why 2022/2023/2025 needed Puri civil overrides and why ~60% of lunar festival
dates in 2020–2030 were wrong (see eval.md, E-FEST-REFERENCE).

All longitudes are Lahiri sidereal (src.engine); tithi depends only on the
Moon−Sun difference, so the ayanamsa cancels there.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from functools import lru_cache

from src.engine import _moon_longitude, _sun_longitude

SYNODIC_DAYS = 29.530588
_TOL_DAYS = 1.0 / 86400.0  # 1 s


def elongation(jd: float) -> float:
    """Moon − Sun, 0–360°."""
    return (_moon_longitude(jd) - _sun_longitude(jd)) % 360.0


def sun_sign(jd: float) -> int:
    """Sidereal sign of the Sun, 0 = Mesha … 11 = Meena."""
    return int(_sun_longitude(jd) // 30) % 12


def _bisect(f, lo: float, hi: float) -> float:
    """f(lo) < 0 <= f(hi); returns the root to ~1 s."""
    while hi - lo > _TOL_DAYS:
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return hi


def _elong_target(target: float, jd_guess: float) -> float:
    """JD near jd_guess (±~3 days) where elongation == target (deg)."""

    def f(jd: float) -> float:
        # signed angular distance in (−180, 180]
        return (elongation(jd) - target + 180.0) % 360.0 - 180.0

    lo, hi = jd_guess - 3.0, jd_guess + 3.0
    # walk until f changes sign (elongation rises ~12°/day)
    step = 0.25
    a = lo
    fa = f(a)
    while a < hi:
        b = a + step
        fb = f(b)
        if fa < 0 <= fb and fb - fa < 90:
            return _bisect(f, a, b)
        a, fa = b, fb
    raise RuntimeError(f"no elongation {target}° crossing near JD {jd_guess}")


def new_moon_on_or_before(jd: float) -> float:
    guess = jd - elongation(jd) / 360.0 * SYNODIC_DAYS
    nm = _elong_target(0.0, guess)
    if nm > jd:
        nm = _elong_target(0.0, nm - SYNODIC_DAYS)
    return nm


def next_new_moon(nm: float) -> float:
    return _elong_target(0.0, nm + SYNODIC_DAYS)


@dataclass(frozen=True)
class Lunation:
    start: float  # JD of opening new moon
    end: float  # JD of closing new moon
    amanta: int  # 0 = Chaitra … 11 = Phalguna
    adhika: bool

    def tithi_start(self, t: int) -> float:
        """Start JD of tithi t (1–30) in this lunation."""
        if t == 1:
            return self.start
        guess = self.start + (t - 1) * SYNODIC_DAYS / 30.0
        return _elong_target(12.0 * (t - 1), guess)

    def tithi_interval(self, t: int) -> tuple[float, float]:
        end = self.end if t == 30 else self.tithi_start(t + 1)
        return self.tithi_start(t), end

    def purnimanta(self, t: int) -> int:
        """Purnimanta month index for tithi t (1–30) of this (Amanta) lunation.
        An Adhika month keeps its own name in both pakshas (it runs new moon
        to new moon, as Drik labels it); otherwise Krishna takes the next name."""
        if self.adhika or t <= 15:
            return self.amanta
        return (self.amanta + 1) % 12


@lru_cache(maxsize=64)
def lunations_for_year(year: int) -> tuple[Lunation, ...]:
    """All lunations overlapping the civil year (with a month of margin)."""
    import swisseph as swe

    jd0 = swe.julday(year, 1, 1, 0.0) - 40.0
    jd1 = swe.julday(year + 1, 1, 1, 0.0) + 40.0
    nms = [new_moon_on_or_before(jd0)]
    while nms[-1] < jd1:
        nms.append(next_new_moon(nms[-1]))
    nms.append(next_new_moon(nms[-1]))
    signs = [sun_sign(nm) for nm in nms]
    out = []
    for i in range(len(nms) - 1):
        out.append(
            Lunation(
                start=nms[i],
                end=nms[i + 1],
                amanta=(signs[i] + 1) % 12,
                adhika=signs[i] == signs[i + 1],
            )
        )
    return tuple(out)


def lunation_at(jd: float) -> Lunation:
    import swisseph as swe

    year = swe.revjul(jd)[0]
    for y in (year, year - 1, year + 1):
        lus = lunations_for_year(y)
        starts = [lu.start for lu in lus]
        i = bisect_right(starts, jd) - 1
        if 0 <= i < len(lus) and lus[i].start <= jd < lus[i].end:
            return lus[i]
    raise RuntimeError(f"no lunation contains JD {jd}")


def masa_at(jd: float) -> tuple[int, bool]:
    """(Purnimanta month index, is_adhika) at a moment."""
    lu = lunation_at(jd)
    t = int(elongation(jd) // 12) + 1
    return lu.purnimanta(t), lu.adhika


@lru_cache(maxsize=64)
def sankrantis_for_year(year: int) -> tuple[tuple[int, float], ...]:
    """(sign entered 0–11, JD) for every solar transit in the civil year."""
    import swisseph as swe

    jd = swe.julday(year, 1, 1, 0.0) - 1.0
    jd_end = swe.julday(year + 1, 1, 1, 0.0) + 1.0
    out = []
    sign = sun_sign(jd)
    while jd < jd_end:
        nxt = (sign + 1) % 12
        target = nxt * 30.0

        def f(x: float, target: float = target) -> float:
            return (_sun_longitude(x) - target + 180.0) % 360.0 - 180.0

        lo = jd
        hi = jd + 1.0
        while f(hi) < 0:
            lo, hi = hi, hi + 1.0
        t = _bisect(f, lo, hi)
        out.append((nxt, t))
        jd, sign = t + 20.0, nxt
    return tuple(x for x in out if swe.julday(year, 1, 1, 0.0) - 1 <= x[1] < jd_end)
