"""
models/loan.py
--------------
Loan is an immutable value object created on borrow and resolved on return.
It is the audit trail — never mutated after creation.
"""

from __future__ import annotations
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class Loan:
    loan_id:     str
    member_id:   str
    isbn:        str
    copy_id:     str
    borrow_date: datetime
    due_date:    datetime

    @staticmethod
    def create(member_id: str, isbn: str, copy_id: str, loan_days: int) -> "Loan":
        now = datetime.now()
        return Loan(
            loan_id     = "L-" + str(uuid.uuid4())[:8].upper(),
            member_id   = member_id,
            isbn        = isbn,
            copy_id     = copy_id,
            borrow_date = now,
            due_date    = now + timedelta(days=loan_days),
        )

    @property
    def is_overdue(self) -> bool:
        return datetime.now() > self.due_date

    def overdue_days(self, return_date: datetime | None = None) -> int:
        """Returns number of days past due (0 if not overdue)."""
        end = return_date or datetime.now()
        delta = end - self.due_date
        return max(0, delta.days)

    def __repr__(self) -> str:
        status = "OVERDUE" if self.is_overdue else "OK"
        return (
            f"Loan[{self.loan_id}] "
            f"Member={self.member_id} Copy={self.copy_id} "
            f"Due={self.due_date.strftime('%Y-%m-%d')} [{status}]"
        )
