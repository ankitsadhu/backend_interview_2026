"""
notation.py — Algebraic notation parser and formatter.

Supports:
  - Piece moves:  Nf3, Bb5, Qd4
  - Pawn moves:   e4, d5
  - Captures:     Nxf3, exd5
  - Check/mate:   Nf3+, Qd4#
  - Castling:     O-O, O-O-O
  - Promotion:    e8=Q, e8=R+
  - Disambiguation: Rae1, R1a3, Qh4e1
"""
from __future__ import annotations

import re
from typing import List, Optional

from .board import Board
from .models import Color, Move, PieceType, Position
from .move_validator import MoveValidator


_PIECE_MAP = {
    "K": PieceType.KING, "Q": PieceType.QUEEN, "R": PieceType.ROOK,
    "B": PieceType.BISHOP, "N": PieceType.KNIGHT,
}

_RE_MOVE = re.compile(
    r'^(?P<piece>[KQRBN])?'
    r'(?P<from_file>[a-h])?(?P<from_rank>[1-8])?'
    r'(?P<capture>x)?'
    r'(?P<to_file>[a-h])(?P<to_rank>[1-8])'
    r'(?:=(?P<promo>[QRBN]))?'
    r'(?P<check>[+#])?$'
)


class NotationParser:
    """Parse and format Standard Algebraic Notation (SAN)."""

    @staticmethod
    def parse(text: str, board: Board, color: Color) -> Optional[Move]:
        """
        Parse an algebraic notation string and return the matching legal Move,
        or None if no match is found.
        """
        text = text.strip()

        # Castling
        if text in ("O-O", "0-0"):
            return NotationParser._find_castling(board, color, kingside=True)
        if text in ("O-O-O", "0-0-0"):
            return NotationParser._find_castling(board, color, kingside=False)

        m = _RE_MOVE.match(text)
        if not m:
            return None

        piece_type = _PIECE_MAP.get(m.group("piece"), PieceType.PAWN)
        to_file    = m.group("to_file")
        to_rank    = m.group("to_rank")
        to_pos     = Position.from_algebraic(to_file + to_rank)

        promo      = _PIECE_MAP.get(m.group("promo")) if m.group("promo") else None
        from_file  = m.group("from_file")
        from_rank  = m.group("from_rank")

        # Get all legal moves and filter
        legal = MoveValidator.get_legal_moves(board, color)
        candidates = [
            mv for mv in legal
            if mv.piece.piece_type == piece_type
            and mv.to_pos == to_pos
        ]

        if promo:
            candidates = [mv for mv in candidates if mv.promotion == promo]
        else:
            # For non-promotion moves, exclude promotion variants
            if piece_type == PieceType.PAWN:
                # If there are promotion candidates but no promo specified, filter to non-promo
                non_promo = [mv for mv in candidates if mv.promotion is None]
                if non_promo:
                    candidates = non_promo

        # Disambiguation
        if from_file:
            col = ord(from_file) - ord('a')
            candidates = [mv for mv in candidates if mv.from_pos.col == col]
        if from_rank:
            row = int(from_rank) - 1
            candidates = [mv for mv in candidates if mv.from_pos.row == row]

        if len(candidates) == 1:
            return candidates[0]
        return None

    @staticmethod
    def format_move(move: Move, legal_moves: Optional[List[Move]] = None) -> str:
        """
        Format a Move into SAN.  If legal_moves is provided,
        disambiguation is added when multiple same-type pieces
        can reach the same square.
        """
        if move.is_castling:
            san = "O-O" if move.is_kingside else "O-O-O"
        else:
            san = ""
            pt  = move.piece.piece_type

            if pt != PieceType.PAWN:
                san += pt.symbol  # K, Q, R, B, N

                # Disambiguation
                if legal_moves:
                    ambiguous = [
                        m for m in legal_moves
                        if m.piece.piece_type == pt
                        and m.to_pos == move.to_pos
                        and m.from_pos != move.from_pos
                    ]
                    if ambiguous:
                        same_file = any(m.from_pos.col == move.from_pos.col for m in ambiguous)
                        same_rank = any(m.from_pos.row == move.from_pos.row for m in ambiguous)
                        if not same_file:
                            san += chr(ord('a') + move.from_pos.col)
                        elif not same_rank:
                            san += str(move.from_pos.row + 1)
                        else:
                            san += move.from_pos.to_algebraic()

            # Capture
            if move.captured or move.is_en_passant:
                if pt == PieceType.PAWN:
                    san += chr(ord('a') + move.from_pos.col)
                san += "x"

            san += move.to_pos.to_algebraic()

            if move.promotion:
                san += "=" + move.promotion.symbol

        if move.gives_checkmate:
            san += "#"
        elif move.gives_check:
            san += "+"

        return san

    # ----------------------------------------------------------
    # Internal
    # ----------------------------------------------------------

    @staticmethod
    def _find_castling(board: Board, color: Color, kingside: bool) -> Optional[Move]:
        legal = MoveValidator.get_legal_moves(board, color)
        for m in legal:
            if m.is_castling and m.is_kingside == kingside:
                return m
        return None
