"""
library/library.py
------------------
Library — Facade / Public API

Exposes clean surface:
  add_book(), register_member(), borrow(), return_book(),
  search(), member_report(), overdue_report()

All heavy lifting is in services; Library just wires them together.
"""

from __future__ import annotations
from datetime import datetime

from .models.book    import Book, BookCopy, Genre
from .models.member  import Member
from .models.loan    import Loan
from .services.catalog          import BookCatalog
from .services.member_registry  import MemberRegistry
from .services.loan_manager     import LoanManager, AvailabilityCallback
from .strategies.fine           import FineStrategy


class Library:
    """
    Facade over BookCatalog, MemberRegistry, and LoanManager.
    This is the only class callers need to import.
    """

    def __init__(
        self,
        name:          str,
        fine_strategy: FineStrategy | None = None,
    ) -> None:
        self.name      = name
        self._catalog  = BookCatalog()
        self._registry = MemberRegistry()
        self._loans    = LoanManager(self._catalog, self._registry, fine_strategy)

    # ── catalog operations ────────────────────────────────────────────────────

    def add_book(self, book: Book, copies: int = 1) -> list[BookCopy]:
        added = self._catalog.add_book(book, copies)
        print(f"[CATALOG] Added: {book}  ({copies} cop{'y' if copies == 1 else 'ies'})")
        return added

    def add_copies(self, isbn: str, count: int = 1) -> list[BookCopy]:
        added = self._catalog.add_copies(isbn, count)
        print(f"[CATALOG] Added {count} more cop{'y' if count == 1 else 'ies'} to ISBN {isbn}")
        return added

    def search(self, query: str) -> list[Book]:
        results = self._catalog.search(query)
        print(f"[SEARCH] '{query}' -> {len(results)} result(s)")
        return results

    # ── member operations ─────────────────────────────────────────────────────

    def register_member(self, member: Member) -> Member:
        self._registry.register(member)
        print(f"[MEMBER] Registered: {member}")
        return member

    # ── loan operations ───────────────────────────────────────────────────────

    def borrow(self, member_id: str, isbn: str) -> Loan:
        loan   = self._loans.borrow(member_id, isbn)
        member = self._registry.get(member_id)
        book   = self._catalog.find_by_isbn(isbn)
        print(
            f"[BORROW] {member.name} borrowed '{book.title if book else isbn}' | "
            f"Due: {loan.due_date.strftime('%Y-%m-%d')} | {loan}"
        )
        return loan

    def return_book(
        self,
        loan_id:     str,
        return_date: datetime | None = None,
    ) -> float:
        fine = self._loans.return_book(loan_id, return_date)
        if fine > 0:
            print(f"[RETURN] Loan {loan_id} returned | Fine: Rs.{fine:.2f} (OVERDUE)")
        else:
            print(f"[RETURN] Loan {loan_id} returned | No fine")
        return fine

    def pay_fine(self, member_id: str, amount: float) -> float:
        remaining = self._loans.pay_fine(member_id, amount)
        member    = self._registry.get(member_id)
        print(f"[FINE]   {member.name} paid Rs.{amount:.2f} | Remaining: Rs.{remaining:.2f}")
        return remaining

    # ── observer hook ─────────────────────────────────────────────────────────

    def subscribe_availability(self, callback: AvailabilityCallback) -> None:
        """Subscribe to 'book available' events (isbn, member_id) -> None."""
        self._loans.subscribe(callback)

    # ── reporting ─────────────────────────────────────────────────────────────

    def print_inventory(self) -> None:
        sep = "-" * 72
        print(f"\n{sep}")
        print(f"  LIBRARY: {self.name}  --  Inventory")
        print(sep)
        report = self._catalog.availability_report()
        if not report:
            print("  (No books in catalog)")
        for row in report:
            print(
                f"  [{row['ISBN']}] {row['Title']} by {row['Author']}"
                f"  | Avail: {row['Available']} | Borrowed: {row['Borrowed']} "
                f"| Reserved: {row['Reserved']} | Lost: {row['Lost']}"
            )
        print(sep)

    def print_overdue_report(self) -> None:
        sep = "-" * 72
        print(f"\n{sep}")
        print(f"  OVERDUE LOANS")
        print(sep)
        loans = self._loans.overdue_loans()
        if not loans:
            print("  No overdue loans.")
        for loan in loans:
            member = self._registry.get(loan.member_id)
            book   = self._catalog.find_by_isbn(loan.isbn)
            overdue_days = loan.overdue_days()
            print(
                f"  {member.name} | '{book.title if book else loan.isbn}' | "
                f"Due: {loan.due_date.strftime('%Y-%m-%d')} | "
                f"Overdue: {overdue_days} day(s)"
            )
        print(sep)

    def print_member_report(self, member_id: str) -> None:
        sep = "-" * 72
        member  = self._registry.get(member_id)
        active  = self._loans.active_loans_for(member_id)
        history = self._loans.loan_history_for(member_id)
        fine    = self._loans.outstanding_fine(member_id)
        print(f"\n{sep}")
        print(f"  MEMBER REPORT: {member}")
        print(sep)
        print(f"  Active Loans   : {len(active)}")
        for l in active:
            book = self._catalog.find_by_isbn(l.isbn)
            print(f"    - '{book.title if book else l.isbn}'  {l}")
        print(f"  Returned Books : {len(history)}")
        print(f"  Outstanding Fine: Rs.{fine:.2f}")
        print(sep)
