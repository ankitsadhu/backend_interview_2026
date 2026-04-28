"""
models.py — Core data models for the Chess engine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ============================================================
# Enumerations
# ============================================================

class Color(Enum):
    WHITE = "WHITE"
    BLACK = "BLACK"

    @property
    def opposite(self) -> "Color":
        return Color.BLACK if self == Color.WHITE else Color.WHITE

    def __str__(self) -> str:
        return self.value


class PieceType(Enum):
    PAWN   = "PAWN"
    KNIGHT = "KNIGHT"
    BISHOP = "BISHOP"
    ROOK   = "ROOK"
    QUEEN  = "QUEEN"
    KING   = "KING"

    @property
    def symbol(self) -> str:
        """Single-letter algebraic symbol (pawn = empty)."""
        return {"PAWN": "", "KNIGHT": "N", "BISHOP": "B",
                "ROOK": "R", "QUEEN": "Q", "KING": "K"}[self.value]

    def __str__(self) -> str:
        return self.value


class GameStatus(Enum):
    IN_PROGRESS       = "IN_PROGRESS"
    CHECK             = "CHECK"
    CHECKMATE         = "CHECKMATE"
    STALEMATE         = "STALEMATE"
    DRAW_50_MOVE      = "DRAW_50_MOVE"
    DRAW_REPETITION   = "DRAW_REPETITION"
    DRAW_INSUFFICIENT = "DRAW_INSUFFICIENT"


# ============================================================
# Position
# ============================================================

@dataclass(frozen=True)
class Position:
    """Board position.  row=0 is rank 1 (white's back rank), col=0 is file 'a'."""
    row: int   # 0-7
    col: int   # 0-7

    def is_valid(self) -> bool:
        return 0 <= self.row <= 7 and 0 <= self.col <= 7

    def to_algebraic(self) -> str:
        return chr(ord('a') + self.col) + str(self.row + 1)

    @classmethod
    def from_algebraic(cls, s: str) -> "Position":
        if len(s) != 2:
            raise ValueError(f"Invalid algebraic position: '{s}'")
        col = ord(s[0].lower()) - ord('a')
        row = int(s[1]) - 1
        pos = cls(row, col)
        if not pos.is_valid():
            raise ValueError(f"Position out of bounds: '{s}'")
        return pos

    def __str__(self) -> str:
        return self.to_algebraic()

    def __repr__(self) -> str:
        return f"Position({self.to_algebraic()})"


# ============================================================
# Piece
# ============================================================

@dataclass
class Piece:
    color     : Color
    piece_type: PieceType
    has_moved : bool = False

    @property
    def symbol(self) -> str:
        """Single char: uppercase for white, lowercase for black."""
        symbols = {
            PieceType.PAWN  : 'P', PieceType.KNIGHT: 'N',
            PieceType.BISHOP: 'B', PieceType.ROOK  : 'R',
            PieceType.QUEEN : 'Q', PieceType.KING  : 'K',
        }
        s = symbols[self.piece_type]
        return s if self.color == Color.WHITE else s.lower()

    @property
    def unicode_symbol(self) -> str:
        white = {
            PieceType.KING: '♔', PieceType.QUEEN: '♕',
            PieceType.ROOK: '♖', PieceType.BISHOP: '♗',
            PieceType.KNIGHT: '♘', PieceType.PAWN: '♙',
        }
        black = {
            PieceType.KING: '♚', PieceType.QUEEN: '♛',
            PieceType.ROOK: '♜', PieceType.BISHOP: '♝',
            PieceType.KNIGHT: '♞', PieceType.PAWN: '♟',
        }
        return white[self.piece_type] if self.color == Color.WHITE else black[self.piece_type]

    def copy(self) -> "Piece":
        return Piece(self.color, self.piece_type, self.has_moved)

    def __str__(self) -> str:
        return self.symbol


# ============================================================
# Move
# ============================================================

@dataclass
class Move:
    from_pos      : Position
    to_pos        : Position
    piece         : Piece
    captured      : Optional[Piece]   = None
    promotion     : Optional[PieceType] = None
    is_castling   : bool               = False
    is_kingside   : bool               = False   # only relevant if is_castling
    is_en_passant : bool               = False
    gives_check   : bool               = False
    gives_checkmate: bool              = False

    def to_algebraic(self) -> str:
        """Simple algebraic representation."""
        if self.is_castling:
            return "O-O" if self.is_kingside else "O-O-O"

        parts = []
        # Piece letter
        if self.piece.piece_type != PieceType.PAWN:
            parts.append(self.piece.piece_type.symbol)
        elif self.captured:
            parts.append(self.from_pos.to_algebraic()[0])  # file for pawn capture

        # Capture
        if self.captured or self.is_en_passant:
            parts.append("x")

        # Destination
        parts.append(self.to_pos.to_algebraic())

        # Promotion
        if self.promotion:
            parts.append("=")
            parts.append(self.promotion.symbol)

        # Check/checkmate
        if self.gives_checkmate:
            parts.append("#")
        elif self.gives_check:
            parts.append("+")

        return "".join(parts)

    def __str__(self) -> str:
        return self.to_algebraic()

    def __repr__(self) -> str:
        return f"Move({self.to_algebraic()})"
