"""
models/member.py
----------------
Member        - library member with borrow limits/loan duration by type
MemberType    - STUDENT | TEACHER | PREMIUM
MemberFactory - factory that wires the right policy per type
MemberPolicy  - encapsulates limits so adding a new type is one-liner
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import NamedTuple


class MemberType(Enum):
    STUDENT = "Student"
    TEACHER = "Teacher"
    PREMIUM = "Premium"


class MemberPolicy(NamedTuple):
    """Encodes the business rules for a member type."""
    max_books:        int   # simultaneous borrow limit
    loan_days:        int   # days before due
    fine_waiver_days: int   # grace days before fine kicks in


# Single place to change business rules per member type
_POLICIES: dict[MemberType, MemberPolicy] = {
    MemberType.STUDENT: MemberPolicy(max_books=3,  loan_days=14, fine_waiver_days=0),
    MemberType.TEACHER: MemberPolicy(max_books=5,  loan_days=30, fine_waiver_days=2),
    MemberType.PREMIUM: MemberPolicy(max_books=10, loan_days=60, fine_waiver_days=5),
}


@dataclass
class Member:
    member_id:   str
    name:        str
    email:       str
    member_type: MemberType
    policy:      MemberPolicy = field(init=False)

    # loan_ids currently active; managed externally by LoanManager
    active_loan_ids: list[str] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self.policy = _POLICIES[self.member_type]

    # ── computed properties ────────────────────────────────────────────────────

    @property
    def can_borrow(self) -> bool:
        return len(self.active_loan_ids) < self.policy.max_books

    @property
    def active_loans_count(self) -> int:
        return len(self.active_loan_ids)

    def __repr__(self) -> str:
        return (
            f"Member[{self.member_id}] {self.name} "
            f"({self.member_type.value}) | Loans: {self.active_loans_count}/{self.policy.max_books}"
        )


# ── Factory ────────────────────────────────────────────────────────────────────

class MemberFactory:
    @staticmethod
    def create(
        name:        str,
        email:       str,
        member_type: MemberType = MemberType.STUDENT,
    ) -> Member:
        member_id = "M-" + str(uuid.uuid4())[:6].upper()
        return Member(
            member_id   = member_id,
            name        = name,
            email       = email,
            member_type = member_type,
        )
