"""
check_detector.py — Check, checkmate, stalemate, and draw detection.
"""
from __future__ import annotations

from typing import List, Optional

from .board import Board
from .models import Color, GameStatus, Move, Piece, PieceType, Position
from .pieces import PieceMoveGenerator


class CheckDetector:
    """Detects check, checkmate, stalemate, and insufficient material."""

    # ----------------------------------------------------------
    # Core: is a square attacked?
    # ----------------------------------------------------------

    @staticmethod
    def is_square_attacked(board: Board, pos: Position, by_color: Color) -> bool:
        """Is *pos* attacked by any piece of *by_color*?"""
        for src, piece in board.find_pieces(by_color):
            if _attacks_square(board, src, piece, pos):
                return True
        return False

    @staticmethod
    def get_attackers(board: Board, pos: Position, by_color: Color) -> List[Position]:
        """Return positions of all *by_color* pieces attacking *pos*."""
        return [
            src for src, piece in board.find_pieces(by_color)
            if _attacks_square(board, src, piece, pos)
        ]

    # ----------------------------------------------------------
    # Check
    # ----------------------------------------------------------

    @staticmethod
    def is_in_check(board: Board, color: Color) -> bool:
        """Is *color*'s king currently in check?"""
        king_pos = board.find_king(color)
        if king_pos is None:
            return False
        return CheckDetector.is_square_attacked(board, king_pos, color.opposite)

    # ----------------------------------------------------------
    # Checkmate / Stalemate
    # ----------------------------------------------------------

    @staticmethod
    def is_checkmate(board: Board, color: Color, legal_moves: Optional[List[Move]] = None) -> bool:
        """King is in check AND no legal moves available."""
        if not CheckDetector.is_in_check(board, color):
            return False
        if legal_moves is not None:
            return len(legal_moves) == 0
        # Compute legal moves ourselves (import-safe approach)
        from .move_validator import MoveValidator
        return len(MoveValidator.get_legal_moves(board, color)) == 0

    @staticmethod
    def is_stalemate(board: Board, color: Color, legal_moves: Optional[List[Move]] = None) -> bool:
        """NOT in check but no legal moves available."""
        if CheckDetector.is_in_check(board, color):
            return False
        if legal_moves is not None:
            return len(legal_moves) == 0
        from .move_validator import MoveValidator
        return len(MoveValidator.get_legal_moves(board, color)) == 0

    # ----------------------------------------------------------
    # Insufficient material draw
    # ----------------------------------------------------------

    @staticmethod
    def is_insufficient_material(board: Board) -> bool:
        """
        Detect drawn by insufficient material:
          K vs K
          K+B vs K
          K+N vs K
          K+B vs K+B (same color bishops)
        """
        pieces = board.all_pieces()
        non_kings = [(pos, p) for pos, p in pieces if p.piece_type != PieceType.KING]

        if len(non_kings) == 0:
            return True  # K vs K

        if len(non_kings) == 1:
            p = non_kings[0][1]
            if p.piece_type in (PieceType.BISHOP, PieceType.KNIGHT):
                return True

        if len(non_kings) == 2:
            types = {p.piece_type for _, p in non_kings}
            colors = {p.color for _, p in non_kings}
            if types == {PieceType.BISHOP} and len(colors) == 2:
                # Both sides have exactly one bishop — check same color squares
                positions = [pos for pos, _ in non_kings]
                square_colors = [(p.row + p.col) % 2 for p in positions]
                if square_colors[0] == square_colors[1]:
                    return True

        return False

    # ----------------------------------------------------------
    # Game status
    # ----------------------------------------------------------

    @staticmethod
    def get_game_status(
        board: Board,
        current_color: Color,
        legal_moves: Optional[List[Move]] = None,
        halfmove_clock: int = 0,
        position_count: int = 1,
    ) -> GameStatus:
        """Determine current game status."""
        if CheckDetector.is_checkmate(board, current_color, legal_moves):
            return GameStatus.CHECKMATE
        if CheckDetector.is_stalemate(board, current_color, legal_moves):
            return GameStatus.STALEMATE
        if CheckDetector.is_insufficient_material(board):
            return GameStatus.DRAW_INSUFFICIENT
        if halfmove_clock >= 100:   # 50 moves × 2 half-moves
            return GameStatus.DRAW_50_MOVE
        if position_count >= 3:
            return GameStatus.DRAW_REPETITION
        if CheckDetector.is_in_check(board, current_color):
            return GameStatus.CHECK
        return GameStatus.IN_PROGRESS


# ============================================================
# Internal: does a specific piece attack a target square?
# ============================================================

def _attacks_square(board: Board, src: Position, piece: Piece, target: Position) -> bool:
    """Does *piece* at *src* attack *target*?  (Does NOT require target to be enemy.)"""
    pt = piece.piece_type
    dr = target.row - src.row
    dc = target.col - src.col

    if pt == PieceType.PAWN:
        direction = 1 if piece.color == Color.WHITE else -1
        return dr == direction and abs(dc) == 1

    if pt == PieceType.KNIGHT:
        return (abs(dr), abs(dc)) in ((2, 1), (1, 2))

    if pt == PieceType.KING:
        return abs(dr) <= 1 and abs(dc) <= 1 and (dr != 0 or dc != 0)

    # Sliding pieces
    if pt == PieceType.BISHOP:
        if abs(dr) != abs(dc) or dr == 0:
            return False
        return _slide_clear(board, src, target, _sign(dr), _sign(dc))

    if pt == PieceType.ROOK:
        if dr != 0 and dc != 0:
            return False
        return _slide_clear(board, src, target, _sign(dr), _sign(dc))

    if pt == PieceType.QUEEN:
        if dr == 0 or dc == 0 or abs(dr) == abs(dc):
            return _slide_clear(board, src, target, _sign(dr), _sign(dc))
        return False

    return False


def _slide_clear(board: Board, src: Position, target: Position, dr: int, dc: int) -> bool:
    """Check that all squares between src and target (exclusive) are empty."""
    r, c = src.row + dr, src.col + dc
    while (r, c) != (target.row, target.col):
        if not Board.is_valid_pos(r, c):
            return False
        if board.get_piece(Position(r, c)) is not None:
            return False
        r += dr
        c += dc
    return True


def _sign(n: int) -> int:
    return (1 if n > 0 else -1) if n != 0 else 0
