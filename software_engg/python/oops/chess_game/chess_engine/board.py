"""
board.py — Chess board representation.

Row 0 = rank 1 (white back rank), Row 7 = rank 8 (black back rank).
Col 0 = file a, Col 7 = file h.
"""
from __future__ import annotations

import copy
from typing import Dict, List, Optional, Tuple

from .models import Color, Piece, PieceType, Position


class Board:
    """8×8 chess board with piece placement and query helpers."""

    def __init__(self) -> None:
        self._grid: List[List[Optional[Piece]]] = [
            [None for _ in range(8)] for _ in range(8)
        ]
        # En passant target square (set after a pawn double-advance)
        self.en_passant_target: Optional[Position] = None

    # ----------------------------------------------------------
    # Setup
    # ----------------------------------------------------------

    def setup_initial(self) -> None:
        """Place pieces in the standard starting position."""
        # Back ranks
        back_rank = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP, PieceType.QUEEN,
            PieceType.KING, PieceType.BISHOP, PieceType.KNIGHT, PieceType.ROOK,
        ]
        for col, pt in enumerate(back_rank):
            self._grid[0][col] = Piece(Color.WHITE, pt)
            self._grid[7][col] = Piece(Color.BLACK, pt)

        # Pawns
        for col in range(8):
            self._grid[1][col] = Piece(Color.WHITE, PieceType.PAWN)
            self._grid[6][col] = Piece(Color.BLACK, PieceType.PAWN)

    @classmethod
    def standard(cls) -> "Board":
        b = cls()
        b.setup_initial()
        return b

    # ----------------------------------------------------------
    # Piece access
    # ----------------------------------------------------------

    @staticmethod
    def is_valid_pos(row: int, col: int) -> bool:
        return 0 <= row <= 7 and 0 <= col <= 7

    def get_piece(self, pos: Position) -> Optional[Piece]:
        if not pos.is_valid():
            return None
        return self._grid[pos.row][pos.col]

    def set_piece(self, pos: Position, piece: Optional[Piece]) -> None:
        self._grid[pos.row][pos.col] = piece

    def remove_piece(self, pos: Position) -> Optional[Piece]:
        p = self._grid[pos.row][pos.col]
        self._grid[pos.row][pos.col] = None
        return p

    def move_piece(self, from_pos: Position, to_pos: Position) -> Optional[Piece]:
        """Move a piece, returning any captured piece."""
        captured = self.remove_piece(to_pos)
        piece    = self.remove_piece(from_pos)
        if piece:
            piece.has_moved = True
            self.set_piece(to_pos, piece)
        return captured

    # ----------------------------------------------------------
    # Queries
    # ----------------------------------------------------------

    def find_king(self, color: Color) -> Optional[Position]:
        for r in range(8):
            for c in range(8):
                p = self._grid[r][c]
                if p and p.color == color and p.piece_type == PieceType.KING:
                    return Position(r, c)
        return None

    def find_pieces(self, color: Color) -> List[Tuple[Position, Piece]]:
        result = []
        for r in range(8):
            for c in range(8):
                p = self._grid[r][c]
                if p and p.color == color:
                    result.append((Position(r, c), p))
        return result

    def all_pieces(self) -> List[Tuple[Position, Piece]]:
        result = []
        for r in range(8):
            for c in range(8):
                p = self._grid[r][c]
                if p:
                    result.append((Position(r, c), p))
        return result

    def is_empty(self, pos: Position) -> bool:
        return self.get_piece(pos) is None

    def is_enemy(self, pos: Position, color: Color) -> bool:
        p = self.get_piece(pos)
        return p is not None and p.color != color

    def is_friendly(self, pos: Position, color: Color) -> bool:
        p = self.get_piece(pos)
        return p is not None and p.color == color

    # ----------------------------------------------------------
    # Copy
    # ----------------------------------------------------------

    def clone(self) -> "Board":
        new_board = Board()
        for r in range(8):
            for c in range(8):
                p = self._grid[r][c]
                new_board._grid[r][c] = p.copy() if p else None
        new_board.en_passant_target = self.en_passant_target
        return new_board

    # ----------------------------------------------------------
    # Display
    # ----------------------------------------------------------

    def to_ascii(self, perspective: Color = Color.WHITE) -> str:
        lines = []
        rows = range(7, -1, -1) if perspective == Color.WHITE else range(8)
        for r in rows:
            rank_str = f" {r + 1} "
            for c in range(8):
                p = self._grid[r][c]
                rank_str += f" {p.symbol if p else '.'} "
            lines.append(rank_str)
        lines.append("    a   b   c   d   e   f   g   h")
        return "\n".join(lines)

    def to_fen_board(self) -> str:
        """FEN board string (no turn/castling/etc.)."""
        rows = []
        for r in range(7, -1, -1):
            empty = 0
            row_str = ""
            for c in range(8):
                p = self._grid[r][c]
                if p is None:
                    empty += 1
                else:
                    if empty > 0:
                        row_str += str(empty)
                        empty = 0
                    row_str += p.symbol
            if empty > 0:
                row_str += str(empty)
            rows.append(row_str)
        return "/".join(rows)

    def __str__(self) -> str:
        return self.to_ascii()

    def __repr__(self) -> str:
        return f"Board(fen={self.to_fen_board()})"
