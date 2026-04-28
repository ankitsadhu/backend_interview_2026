"""
services/loan_manager.py
------------------------
LoanManager — owns borrow / return lifecycle.
Also implements Observer (waitlist) pattern:
  when a copy is returned, notify the first waiting member.

Depends on:
  - BookCatalog     (find & update copies)
  - MemberRegistry  (find & update members)
  - FineStrategy    (calculate fines on return)
"""

from __future__ import annotations
from collections import defaultdict, deque
from datetime import datetime
from typing import Callable

from ..models.book   import BookCopyStatus
from ..models.loan   import Loan
from ..models.member import Member
from ..strategies.fine import FineStrategy, FineFactory
from .catalog          import BookCatalog
from .member_registry  import MemberRegistry


# Observer callback type: called when a book becomes available again
AvailabilityCallback = Callable[[str, str], None]  # (isbn, member_id)


class LoanManager:
    """
    Coordinates borrow / return operations.

    Key rules:
      - Member cannot exceed max_books limit
      - Member with outstanding fines > threshold cannot borrow (configurable)
      - Waitlist: if no copy available, member joins queue for that ISBN
      - On return, fines are calculated; waitlist is notified
    """

    MAX_OUTSTANDING_FINE = 500.0  # Rs. — members with more cannot borrow

    def __init__(
        self,
        catalog:  BookCatalog,
        registry: MemberRegistry,
        fine_strategy: FineStrategy | None = None,
    ) -> None:
        self._catalog  = catalog
        self._registry = registry
        self._fine     = fine_strategy or FineFactory.get("tiered")

        # loan_id -> Loan
        self._active_loans:   dict[str, Loan]  = {}
        # loan history (returned loans)
        self._loan_history:   list[Loan]       = []
        # member_id -> total unpaid fines
        self._fines:          dict[str, float] = defaultdict(float)
        # isbn -> queue of waiting member_ids
        self._waitlist:       dict[str, deque[str]] = defaultdict(deque)
        # observer subscribers
        self._subscribers:    list[AvailabilityCallback] = []

    # ── observer subscription ─────────────────────────────────────────────────

    def subscribe(self, callback: AvailabilityCallback) -> None:
        self._subscribers.append(callback)

    # ── borrow ────────────────────────────────────────────────────────────────

    def borrow(self, member_id: str, isbn: str) -> Loan:
        """
        Attempt to borrow a book.
        - Validates member eligibility
        - Finds an available copy
        - If no copy: adds member to waitlist and raises
        - Returns a Loan on success
        """
        member = self._registry.get(member_id)
        self._check_eligibility(member)

        copy = self._catalog.get_available_copy(isbn)
        if copy is None:
            self._waitlist[isbn].append(member_id)
            raise RuntimeError(
                f"No copy of ISBN '{isbn}' available. "
                f"'{member.name}' added to waitlist (position {len(self._waitlist[isbn])})."
            )

        # transition copy state
        copy.transition(BookCopyStatus.BORROWED)

        # create loan
        loan = Loan.create(
            member_id = member_id,
            isbn      = isbn,
            copy_id   = copy.copy_id,
            loan_days = member.policy.loan_days,
        )
        self._active_loans[loan.loan_id] = loan
        member.active_loan_ids.append(loan.loan_id)

        return loan

    # ── return ────────────────────────────────────────────────────────────────

    def return_book(
        self,
        loan_id:     str,
        return_date: datetime | None = None,
    ) -> float:
        """
        Process a book return.
        - Releases copy (available again)
        - Computes fine if overdue
        - Notifies waitlist if anyone is waiting
        - Returns fine amount (0.0 if on time)
        """
        loan   = self._get_active_loan(loan_id)
        member = self._registry.get(loan.member_id)
        copy   = self._catalog.get_copy(loan.isbn, loan.copy_id)

        if copy is None:
            raise RuntimeError(f"Data inconsistency: copy {loan.copy_id} not found.")

        # release copy
        copy.transition(BookCopyStatus.AVAILABLE)

        # compute fine
        overdue_days = loan.overdue_days(return_date)
        fine = self._fine.calculate(overdue_days, member.policy, member.member_type)
        if fine > 0:
            self._fines[member.member_id] += fine

        # clean up loan
        del self._active_loans[loan_id]
        member.active_loan_ids.remove(loan_id)
        self._loan_history.append(loan)

        # notify waitlist
        self._notify_waitlist(loan.isbn)

        return fine

    # ── fine management ───────────────────────────────────────────────────────

    def outstanding_fine(self, member_id: str) -> float:
        return self._fines.get(member_id, 0.0)

    def pay_fine(self, member_id: str, amount: float) -> float:
        """Pay (partial or full) fine. Returns remaining balance."""
        current = self._fines.get(member_id, 0.0)
        if amount > current:
            raise ValueError(f"Payment Rs.{amount} exceeds outstanding fine Rs.{current:.2f}.")
        self._fines[member_id] = round(current - amount, 2)
        return self._fines[member_id]

    # ── queries ───────────────────────────────────────────────────────────────

    def active_loans_for(self, member_id: str) -> list[Loan]:
        return [l for l in self._active_loans.values() if l.member_id == member_id]

    def loan_history_for(self, member_id: str) -> list[Loan]:
        return [l for l in self._loan_history if l.member_id == member_id]

    def overdue_loans(self) -> list[Loan]:
        return [l for l in self._active_loans.values() if l.is_overdue]

    def waitlist_for(self, isbn: str) -> list[str]:
        return list(self._waitlist.get(isbn, []))

    # ── internal helpers ──────────────────────────────────────────────────────

    def _check_eligibility(self, member: Member) -> None:
        if not member.can_borrow:
            raise ValueError(
                f"'{member.name}' has reached borrow limit "
                f"({member.policy.max_books} books)."
            )
        fine = self._fines.get(member.member_id, 0.0)
        if fine > self.MAX_OUTSTANDING_FINE:
            raise ValueError(
                f"'{member.name}' has outstanding fine Rs.{fine:.2f} "
                f"(limit Rs.{self.MAX_OUTSTANDING_FINE}). Please clear dues first."
            )

    def _get_active_loan(self, loan_id: str) -> Loan:
        loan = self._active_loans.get(loan_id)
        if loan is None:
            raise KeyError(f"Active loan '{loan_id}' not found.")
        return loan

    def _notify_waitlist(self, isbn: str) -> None:
        queue = self._waitlist.get(isbn)
        if queue:
            next_member_id = queue.popleft()
            for sub in self._subscribers:
                sub(isbn, next_member_id)
