"""
services/member_registry.py
---------------------------
MemberRegistry — manages members (CRUD + lookup).
Completely decoupled from books and loans.
"""

from __future__ import annotations
from ..models.member import Member


class MemberRegistry:
    def __init__(self) -> None:
        self._members: dict[str, Member] = {}

    def register(self, member: Member) -> Member:
        if member.member_id in self._members:
            raise ValueError(f"Member '{member.member_id}' already registered.")
        self._members[member.member_id] = member
        return member

    def get(self, member_id: str) -> Member:
        m = self._members.get(member_id)
        if m is None:
            raise KeyError(f"Member '{member_id}' not found.")
        return m

    def find_by_name(self, query: str) -> list[Member]:
        q = query.lower()
        return [m for m in self._members.values() if q in m.name.lower()]

    def all_members(self) -> list[Member]:
        return list(self._members.values())

    def deactivate(self, member_id: str) -> None:
        m = self.get(member_id)
        if m.active_loans_count > 0:
            raise ValueError(
                f"Cannot deactivate '{member_id}': has {m.active_loans_count} active loan(s)."
            )
        del self._members[member_id]
