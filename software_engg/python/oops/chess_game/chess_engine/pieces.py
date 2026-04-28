"""
pieces.py — Pseudo-legal move generation for each piece type.

These are "raw" moves: they respect piece movement rules and board
boundaries but do NOT filter out moves that leave the king in check.
That filtering is done by MoveValidator.
"""
from __future__ import annotations

from typing import List, Optional

from .models import Color, Move, Piece, PieceType, Position
from .board import Board


# ============================================================
# Sliding helpers
# ============================================================

def _slide(board: Board, pos: Position, piece: Piece,
           directions: List[tuple], max_steps: int = 8) -> List[Move]:
    """Generate moves along sliding directions (bishop/rook/queen)."""
    moves = []
    for dr, dc in directions:
        for step in range(1, max_steps + 1):
            r, c = pos.row + dr * step, pos.col + dc * step
            if not Board.is_valid_pos(r, c):
                break
            target = Position(r, c)
            occupant = board.get_piece(target)
            if occupant is None:
                moves.append(Move(pos, target, piece))
            elif occupant.color != piece.color:
                moves.append(Move(pos, target, piece, captured=occupant))
                break
            else:
                break  # friendly piece blocks
    return moves


# ============================================================
# Per-piece generators
# ============================================================

def _pawn_moves(board: Board, pos: Position, piece: Piece) -> List[Move]:
    moves: List[Move] = []
    direction = 1 if piece.color == Color.WHITE else -1
    start_row = 1 if piece.color == Color.WHITE else 6
    promo_row = 7 if piece.color == Color.WHITE else 0

    # ----- Forward one -----
    fwd = Position(pos.row + direction, pos.col)
    if fwd.is_valid() and board.is_empty(fwd):
        if fwd.row == promo_row:
            for pt in (PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT):
                moves.append(Move(pos, fwd, piece, promotion=pt))
        else:
            moves.append(Move(pos, fwd, piece))

        # ----- Forward two (only if forward one was empty) -----
        if pos.row == start_row:
            fwd2 = Position(pos.row + 2 * direction, pos.col)
            if fwd2.is_valid() and board.is_empty(fwd2):
                moves.append(Move(pos, fwd2, piece))

    # ----- Diagonal captures -----
    for dc in (-1, 1):
        diag = Position(pos.row + direction, pos.col + dc)
        if not diag.is_valid():
            continue

        target = board.get_piece(diag)
        if target and target.color != piece.color:
            if diag.row == promo_row:
                for pt in (PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT):
                    moves.append(Move(pos, diag, piece, captured=target, promotion=pt))
            else:
                moves.append(Move(pos, diag, piece, captured=target))

        # ----- En passant -----
        if board.en_passant_target and diag == board.en_passant_target:
            # The captured pawn is on our row, target's column
            captured_pos = Position(pos.row, diag.col)
            captured_pawn = board.get_piece(captured_pos)
            if captured_pawn and captured_pawn.color != piece.color:
                moves.append(Move(
                    pos, diag, piece,
                    captured=captured_pawn,
                    is_en_passant=True,
                ))

    return moves


def _knight_moves(board: Board, pos: Position, piece: Piece) -> List[Move]:
    moves = []
    offsets = [
        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
        (1, -2), (1, 2), (2, -1), (2, 1),
    ]
    for dr, dc in offsets:
        r, c = pos.row + dr, pos.col + dc
        if not Board.is_valid_pos(r, c):
            continue
        target = Position(r, c)
        occupant = board.get_piece(target)
        if occupant is None:
            moves.append(Move(pos, target, piece))
        elif occupant.color != piece.color:
            moves.append(Move(pos, target, piece, captured=occupant))
    return moves


def _bishop_moves(board: Board, pos: Position, piece: Piece) -> List[Move]:
    return _slide(board, pos, piece, [(-1, -1), (-1, 1), (1, -1), (1, 1)])


def _rook_moves(board: Board, pos: Position, piece: Piece) -> List[Move]:
    return _slide(board, pos, piece, [(-1, 0), (1, 0), (0, -1), (0, 1)])


def _queen_moves(board: Board, pos: Position, piece: Piece) -> List[Move]:
    return _slide(board, pos, piece, [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ])


def _king_moves(board: Board, pos: Position, piece: Piece) -> List[Move]:
    moves = []
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            r, c = pos.row + dr, pos.col + dc
            if not Board.is_valid_pos(r, c):
                continue
            target = Position(r, c)
            occupant = board.get_piece(target)
            if occupant is None:
                moves.append(Move(pos, target, piece))
            elif occupant.color != piece.color:
                moves.append(Move(pos, target, piece, captured=occupant))

    # ----- Castling -----
    if not piece.has_moved:
        moves.extend(_castling_moves(board, pos, piece))

    return moves


def _castling_moves(board: Board, pos: Position, piece: Piece) -> List[Move]:
    """Generate castling pseudo-legal moves.
    
    Legality (king not in check, not moving through check) is verified
    later by MoveValidator.  Here we only check:
      - King and rook have not moved
      - Squares between them are empty
    """
    moves = []
    row = pos.row  # 0 for white, 7 for black

    # Kingside (rook on col 7)
    rook_ks = board.get_piece(Position(row, 7))
    if (rook_ks and rook_ks.piece_type == PieceType.ROOK
            and rook_ks.color == piece.color and not rook_ks.has_moved):
        if board.is_empty(Position(row, 5)) and board.is_empty(Position(row, 6)):
            moves.append(Move(
                pos, Position(row, 6), piece,
                is_castling=True, is_kingside=True,
            ))

    # Queenside (rook on col 0)
    rook_qs = board.get_piece(Position(row, 0))
    if (rook_qs and rook_qs.piece_type == PieceType.ROOK
            and rook_qs.color == piece.color and not rook_qs.has_moved):
        if (board.is_empty(Position(row, 1))
                and board.is_empty(Position(row, 2))
                and board.is_empty(Position(row, 3))):
            moves.append(Move(
                pos, Position(row, 2), piece,
                is_castling=True, is_kingside=False,
            ))

    return moves


# ============================================================
# Public API
# ============================================================

_GENERATORS = {
    PieceType.PAWN  : _pawn_moves,
    PieceType.KNIGHT: _knight_moves,
    PieceType.BISHOP: _bishop_moves,
    PieceType.ROOK  : _rook_moves,
    PieceType.QUEEN : _queen_moves,
    PieceType.KING  : _king_moves,
}


class PieceMoveGenerator:
    """Generates pseudo-legal moves for any piece on the board."""

    @staticmethod
    def generate(board: Board, pos: Position) -> List[Move]:
        piece = board.get_piece(pos)
        if piece is None:
            return []
        gen = _GENERATORS.get(piece.piece_type)
        if gen is None:
            return []
        return gen(board, pos, piece)

    @staticmethod
    def generate_all(board: Board, color: Color) -> List[Move]:
        """All pseudo-legal moves for the given color."""
        moves = []
        for pos, piece in board.find_pieces(color):
            moves.extend(PieceMoveGenerator.generate(board, pos))
        return moves
