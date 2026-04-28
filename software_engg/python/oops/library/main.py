# -*- coding: utf-8 -*-
"""
main.py -- Demo driver for Library Management System
Run: python -m library.main
"""

from datetime import datetime, timedelta

from library.builder       import LibraryBuilder
from library.models.book   import Genre
from library.models.member import MemberType, MemberFactory


# ── 1. Observer: notify when a waitlisted book becomes available ──────────────

def availability_notifier(isbn: str, member_id: str) -> None:
    print(f"  [NOTIFY] Book ISBN={isbn} is now available! Notifying member {member_id}.")


# ── 2. Build the library ──────────────────────────────────────────────────────

lib = (
    LibraryBuilder("MAANG Engineers Public Library")
    .with_fine_strategy("tiered")
    .add_book("978-0-13-468599-1", "Clean Code",                    "Robert C. Martin", Genre.TECHNOLOGY, copies=2)
    .add_book("978-0-13-235088-4", "The Pragmatic Programmer",      "David Thomas",     Genre.TECHNOLOGY, copies=1)
    .add_book("978-0-13-110362-7", "The C Programming Language",    "Kernighan & Ritchie", Genre.TECHNOLOGY, copies=1)
    .add_book("978-0-06-112008-4", "To Kill a Mockingbird",          "Harper Lee",      Genre.FICTION,    copies=2)
    .add_book("978-0-06-093546-9", "Think and Grow Rich",            "Napoleon Hill",   Genre.SELF_HELP,  copies=1)
    .add_member("Alice Kumar",   "alice@email.com",  MemberType.STUDENT)
    .add_member("Bob Sharma",    "bob@email.com",    MemberType.TEACHER)
    .add_member("Carol Singh",   "carol@email.com",  MemberType.PREMIUM)
    .build()
)

lib.subscribe_availability(availability_notifier)

# Grab member objects for convenience
alice = lib._registry.find_by_name("Alice Kumar")[0]
bob   = lib._registry.find_by_name("Bob Sharma")[0]
carol = lib._registry.find_by_name("Carol Singh")[0]


# ── 3. Show initial inventory ─────────────────────────────────────────────────

lib.print_inventory()


# ── 4. Borrow books ───────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("  BORROWING")
print("=" * 60)

loan_alice_clean = lib.borrow(alice.member_id, "978-0-13-468599-1")   # Clean Code (copy 1)
loan_bob_clean   = lib.borrow(bob.member_id,   "978-0-13-468599-1")   # Clean Code (copy 2)
loan_alice_prag  = lib.borrow(alice.member_id, "978-0-13-235088-4")   # Pragmatic Programmer
loan_carol_mock  = lib.borrow(carol.member_id, "978-0-06-112008-4")   # To Kill a Mockingbird


# ── 5. Attempt to borrow a fully-borrowed book → waitlist ────────────────────

print("\n" + "=" * 60)
print("  WAITLIST TEST")
print("=" * 60)

try:
    # No copies of Pragmatic Programmer left — Alice already has the only copy
    lib.borrow(carol.member_id, "978-0-13-235088-4")
except RuntimeError as e:
    print(f"  [INFO] {e}")


# ── 6. Member reports ─────────────────────────────────────────────────────────

lib.print_member_report(alice.member_id)
lib.print_member_report(bob.member_id)


# ── 7. Return on time (no fine) ───────────────────────────────────────────────

print("\n" + "=" * 60)
print("  RETURNS")
print("=" * 60)

# Bob returns Clean Code on time
fine = lib.return_book(loan_bob_clean.loan_id)

# Carol returns Mockingbird on time
fine = lib.return_book(loan_carol_mock.loan_id)


# ── 8. Return overdue (fine scenario) ────────────────────────────────────────

print("\n" + "=" * 60)
print("  OVERDUE RETURN (simulated 20 days late)")
print("=" * 60)

fake_return_date = datetime.now() + timedelta(days=alice.policy.loan_days + 20)

fine = lib.return_book(loan_alice_clean.loan_id, return_date=fake_return_date)
print(f"  => Alice's fine for 20 overdue days: Rs.{fine:.2f}")

# Alice pays part of the fine
lib.pay_fine(alice.member_id, 100.0)


# ── 9. Overdue report ─────────────────────────────────────────────────────────

lib.print_overdue_report()


# ── 10. Book cannot be borrowed with high outstanding fine ───────────────────

print("\n" + "=" * 60)
print("  FINE BLOCK TEST")
print("=" * 60)

# Simulate Alice having a very large fine directly
lib._loans._fines[alice.member_id] = 600.0
try:
    lib.borrow(alice.member_id, "978-0-06-112008-4")
except ValueError as e:
    print(f"  [BLOCKED] {e}")

# Clear fine and try again
lib._loans._fines[alice.member_id] = 0.0
loan_alice_retry = lib.borrow(alice.member_id, "978-0-06-112008-4")
print(f"  [OK] Alice can borrow after clearing fine: {loan_alice_retry}")


# ── 11. Search demo ───────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("  SEARCH")
print("=" * 60)

results = lib.search("clean")
for r in results:
    print(f"  {r}")

results = lib.search("Robert")
for r in results:
    print(f"  {r}")


# ── 12. Final inventory ───────────────────────────────────────────────────────

lib.print_inventory()
lib.print_member_report(alice.member_id)
