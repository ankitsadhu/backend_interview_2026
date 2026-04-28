"""
strategies/fine.py
------------------
Strategy pattern for fine calculation.

Rules:
  - Fine waiver days are respected (from MemberPolicy)
  - Minimum fine = 0 (no negative fines)
  - Register custom strategies via FineFactory.register()
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from ..models.member import MemberType, MemberPolicy


class FineStrategy(ABC):
    """Calculates fine given overdue days, member policy, and member type."""

    @abstractmethod
    def calculate(
        self,
        overdue_days:  int,
        member_policy: MemberPolicy,
        member_type:   MemberType,
    ) -> float:
        ...


# ── Concrete Strategies ───────────────────────────────────────────────────────

class FlatRateFine(FineStrategy):
    """
    Rs. 5/day for everyone.
    Waiver days (from policy) are subtracted first.
    """
    RATE = 5.0

    def calculate(
        self,
        overdue_days:  int,
        member_policy: MemberPolicy,
        member_type:   MemberType,
    ) -> float:
        billable = max(0, overdue_days - member_policy.fine_waiver_days)
        return round(billable * self.RATE, 2)


class TieredFine(FineStrategy):
    """
    Per-type daily fine rate after waiver:
      STUDENT  -> Rs. 10/day
      TEACHER  -> Rs.  5/day  (+ 2-day waiver from policy)
      PREMIUM  -> Rs.  3/day  (+ 5-day waiver from policy)
    """
    _RATES: dict[MemberType, float] = {
        MemberType.STUDENT: 10.0,
        MemberType.TEACHER:  5.0,
        MemberType.PREMIUM:  3.0,
    }

    def calculate(
        self,
        overdue_days:  int,
        member_policy: MemberPolicy,
        member_type:   MemberType,
    ) -> float:
        billable = max(0, overdue_days - member_policy.fine_waiver_days)
        rate     = self._RATES[member_type]
        return round(billable * rate, 2)


# ── Factory / Registry ────────────────────────────────────────────────────────

class FineFactory:
    _registry: dict[str, FineStrategy] = {
        "flat":   FlatRateFine(),
        "tiered": TieredFine(),
    }

    @classmethod
    def get(cls, name: str = "tiered") -> FineStrategy:
        strategy = cls._registry.get(name.lower())
        if strategy is None:
            raise ValueError(
                f"Unknown fine strategy: '{name}'. Options: {list(cls._registry)}"
            )
        return strategy

    @classmethod
    def register(cls, name: str, strategy: FineStrategy) -> None:
        cls._registry[name.lower()] = strategy
