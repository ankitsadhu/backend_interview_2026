"""
move_validator.py — Legal move filtering.

Takes pseudo-legal moves from PieceMoveGenerator and filters
out any move that would leave the moving player's king in check.
Also enforces castling legality (can't castle through/out-of check).
"""
from __future__ import annotations

from typing import List, Optional

from .board import Board
from .check_detector import CheckDetector
from .models import Color, Move, PieceType, Position
from .pieces import PieceMoveGenerator


class MoveValidator:
    """Filters pseudo-legal moves to produce strictly legal moves."""

    @staticmethod
    def get_legal_moves(board: Board, color: Color) -> List[Move]:
        """Return all legal moves for *color*."""
        pseudo = PieceMoveGenerator.generate_all(board, color)
        legal: List[Move] = []
        for move in pseudo:
            if MoveValidator._is_legal(board, move, color):
                legal.append(move)
        return legal

    @staticmethod
    def get_legal_moves_for_piece(board: Board, pos: Position) -> List[Move]:
        """Legal moves for the piece at *pos*."""
        piece = board.get_piece(pos)
        if piece is None:
            return []
        pseudo = PieceMoveGenerator.generate(board, pos)
        return [m for m in pseudo if MoveValidator._is_legal(board, m, piece.color)]

    @staticmethod
    def is_legal_move(board: Board, move: Move) -> bool:
        return MoveValidator._is_legal(board, move, move.piece.color)

    # ----------------------------------------------------------
    # Internal
    # ----------------------------------------------------------

    @staticmethod
    def _is_legal(board: Board, move: Move, color: Color) -> bool:
        """A move is legal if it does not leave own king in check,
        and if castling, the king doesn't move through check."""

        # ---- Castling extra checks ----
        if move.is_castling:
            # Can't castle while in check
            if CheckDetector.is_in_check(board, color):
                return False
            # Can't castle through check
            row = move.from_pos.row
            if move.is_kingside:
                transit = Position(row, 5)  # f1/f8
            else:
                transit = Position(row, 3)  # d1/d8
            if CheckDetector.is_square_attacked(board, transit, color.opposite):
                return False
            # Destination will be checked by the general "would be in check" test below

        # ---- General: does this move leave our king in check? ----
        return not MoveValidator._would_be_in_check(board, move, color)

    @staticmethod
    def _would_be_in_check(board: Board, move: Move, color: Color) -> bool:
        """Simulate the move on a cloned board and check if own king is in check."""
        sim = board.clone()

        # Execute the move on the simulation board
        sim.remove_piece(move.from_pos)
        sim.set_piece(move.to_pos, move.piece.copy())

        # En passant — remove the captured pawn from its actual square
        if move.is_en_passant:
            captured_pos = Position(move.from_pos.row, move.to_pos.col)
            sim.remove_piece(captured_pos)

        # Castling — also move the rook
        if move.is_castling:
            row = move.from_pos.row
            if move.is_kingside:
                rook = sim.remove_piece(Position(row, 7))
                sim.set_piece(Position(row, 5), rook)
            else:
                rook = sim.remove_piece(Position(row, 0))
                sim.set_piece(Position(row, 3), rook)

        # Promotion
        if move.promotion:
            from .models import Piece
            sim.set_piece(move.to_pos, Piece(color, move.promotion, has_moved=True))

        return CheckDetector.is_in_check(sim, color)
