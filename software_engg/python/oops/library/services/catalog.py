"""
services/catalog.py
--------------------
BookCatalog — Repository pattern.

Manages the collection of Books (not copies).
Supports: add, remove, search by ISBN / title / author / genre.
Does NOT know about members, loans, or fines.
"""

from __future__ import annotations
from ..models.book import Book, BookCopy, Genre


class BookCatalog:
    """In-memory book repository with search capabilities."""

    def __init__(self) -> None:
        # isbn -> Book
        self._books: dict[str, Book] = {}

    # ── add / remove ──────────────────────────────────────────────────────────

    def add_book(self, book: Book, copies: int = 1) -> list[BookCopy]:
        """Add a new Book to the catalog with `copies` physical copies."""
        if book.isbn in self._books:
            raise ValueError(f"Book with ISBN '{book.isbn}' already exists.")
        self._books[book.isbn] = book
        return [book.add_copy() for _ in range(copies)]

    def add_copies(self, isbn: str, count: int = 1) -> list[BookCopy]:
        """Add extra physical copies to an existing book."""
        book = self._get_or_raise(isbn)
        return [book.add_copy() for _ in range(count)]

    def remove_book(self, isbn: str) -> None:
        if len(self._get_or_raise(isbn).available_copies()) < self._books[isbn].total_copies():
            raise ValueError(f"Cannot remove '{isbn}': some copies are currently borrowed.")
        del self._books[isbn]

    # ── find available copy ───────────────────────────────────────────────────

    def get_available_copy(self, isbn: str) -> BookCopy | None:
        """Return any available copy of the book (None if none available)."""
        book = self._books.get(isbn)
        copies = book.available_copies() if book else []
        return copies[0] if copies else None

    def get_copy(self, isbn: str, copy_id: str) -> BookCopy | None:
        book = self._books.get(isbn)
        return book.get_copy(copy_id) if book else None

    # ── search ────────────────────────────────────────────────────────────────

    def find_by_isbn(self, isbn: str) -> Book | None:
        return self._books.get(isbn)

    def find_by_title(self, query: str) -> list[Book]:
        q = query.lower()
        return [b for b in self._books.values() if q in b.title.lower()]

    def find_by_author(self, query: str) -> list[Book]:
        q = query.lower()
        return [b for b in self._books.values() if q in b.author.lower()]

    def find_by_genre(self, genre: Genre) -> list[Book]:
        return [b for b in self._books.values() if b.genre == genre]

    def search(self, query: str) -> list[Book]:
        """Broad search across title, author, and ISBN."""
        q = query.lower()
        return [
            b for b in self._books.values()
            if q in b.title.lower() or q in b.author.lower() or q in b.isbn.lower()
        ]

    # ── inventory ─────────────────────────────────────────────────────────────

    def availability_report(self) -> list[dict]:
        report = []
        for book in self._books.values():
            summary = book.copy_summary()
            summary["ISBN"]   = book.isbn
            summary["Title"]  = book.title
            summary["Author"] = book.author
            report.append(summary)
        return report

    def all_books(self) -> list[Book]:
        return list(self._books.values())

    # ── internal ──────────────────────────────────────────────────────────────

    def _get_or_raise(self, isbn: str) -> Book:
        book = self._books.get(isbn)
        if book is None:
            raise KeyError(f"Book with ISBN '{isbn}' not found in catalog.")
        return book
