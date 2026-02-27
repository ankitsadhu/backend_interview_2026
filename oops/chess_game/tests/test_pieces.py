"""
tests/test_pieces.py — Pseudo-legal and legal move generation tests.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from chess_engine.board import Board
from chess_engine.models import Color, Piece, PieceType, Position
from chess_engine.pieces import PieceMoveGenerator
from chess_engine.move_validator import MoveValidator


# ============================================================
# Pawn
# ============================================================

def test_pawn_initial_two_moves():
    """White pawn on e2 should have 2 moves (e3, e4)."""
    b = Board.standard()
    moves = PieceMoveGenerator.generate(b, Position(1, 4))  # e2
    assert len(moves) == 2
    to_squares = {m.to_pos for m in moves}
    assert Position(2, 4) in to_squares  # e3
    assert Position(3, 4) in to_squares  # e4


def test_pawn_blocked():
    """Pawn with a piece directly in front can't move forward."""
    b = Board()
    b.set_piece(Position(1, 0), Piece(Color.WHITE, PieceType.PAWN))
    b.set_piece(Position(2, 0), Piece(Color.BLACK, PieceType.PAWN))  # blocks
    moves = PieceMoveGenerator.generate(b, Position(1, 0))
    assert len(moves) == 0


def test_pawn_capture_diagonal():
    b = Board()
    b.set_piece(Position(3, 3), Piece(Color.WHITE, PieceType.PAWN, has_moved=True))
    b.set_piece(Position(4, 4), Piece(Color.BLACK, PieceType.PAWN, has_moved=True))
    moves = PieceMoveGenerator.generate(b, Position(3, 3))
    captures = [m for m in moves if m.captured]
    assert len(captures) == 1
    assert captures[0].to_pos == Position(4, 4)


def test_pawn_promotion_generates_4_options():
    """Pawn on 7th rank moving to 8th should produce 4 promotion variants."""
    b = Board()
    b.set_piece(Position(6, 0), Piece(Color.WHITE, PieceType.PAWN, has_moved=True))
    moves = PieceMoveGenerator.generate(b, Position(6, 0))
    promos = [m for m in moves if m.promotion]
    assert len(promos) == 4
    promo_types = {m.promotion for m in promos}
    assert promo_types == {PieceType.QUEEN, PieceType.ROOK, PieceType.BISHOP, PieceType.KNIGHT}


# ============================================================
# Knight
# ============================================================

def test_knight_center_8_moves():
    """Knight in center (d4) with empty board → 8 moves."""
    b = Board()
    b.set_piece(Position(3, 3), Piece(Color.WHITE, PieceType.KNIGHT))
    moves = PieceMoveGenerator.generate(b, Position(3, 3))
    assert len(moves) == 8


def test_knight_corner_2_moves():
    """Knight on a1 → only 2 moves."""
    b = Board()
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KNIGHT))
    moves = PieceMoveGenerator.generate(b, Position(0, 0))
    assert len(moves) == 2


def test_knight_initial_b1():
    """Knight on b1 at game start → 2 legal moves (a3, c3)."""
    b = Board.standard()
    moves = MoveValidator.get_legal_moves_for_piece(b, Position(0, 1))
    assert len(moves) == 2


# ============================================================
# Bishop
# ============================================================

def test_bishop_center_empty_board():
    """Bishop on d4, empty board → 13 squares."""
    b = Board()
    b.set_piece(Position(3, 3), Piece(Color.WHITE, PieceType.BISHOP))
    moves = PieceMoveGenerator.generate(b, Position(3, 3))
    assert len(moves) == 13


def test_bishop_blocked_by_friendly():
    b = Board()
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.BISHOP))
    b.set_piece(Position(1, 1), Piece(Color.WHITE, PieceType.PAWN))  # blocks
    moves = PieceMoveGenerator.generate(b, Position(0, 0))
    assert len(moves) == 0


# ============================================================
# Rook
# ============================================================

def test_rook_center_empty_board():
    """Rook on d4, empty board → 14 squares."""
    b = Board()
    b.set_piece(Position(3, 3), Piece(Color.WHITE, PieceType.ROOK))
    moves = PieceMoveGenerator.generate(b, Position(3, 3))
    assert len(moves) == 14


def test_rook_initial_a1_no_legal_moves():
    """Rook on a1 at start is completely blocked by pawns + knight."""
    b = Board.standard()
    moves = MoveValidator.get_legal_moves_for_piece(b, Position(0, 0))
    assert len(moves) == 0


# ============================================================
# Queen
# ============================================================

def test_queen_center_empty_board():
    """Queen on d4, empty board → 27 squares."""
    b = Board()
    b.set_piece(Position(3, 3), Piece(Color.WHITE, PieceType.QUEEN))
    moves = PieceMoveGenerator.generate(b, Position(3, 3))
    assert len(moves) == 27


# ============================================================
# King
# ============================================================

def test_king_center_empty_board():
    """King on d4, empty board → 8 squares."""
    b = Board()
    b.set_piece(Position(3, 3), Piece(Color.WHITE, PieceType.KING))
    moves = PieceMoveGenerator.generate(b, Position(3, 3))
    assert len(moves) == 8


def test_king_initial_no_legal_moves():
    """King on e1 at game start → 0 legal moves (all blocked)."""
    b = Board.standard()
    moves = MoveValidator.get_legal_moves_for_piece(b, Position(0, 4))
    assert len(moves) == 0


# ============================================================
# Total initial legal moves
# ============================================================

def test_white_has_20_initial_legal_moves():
    """White has exactly 20 legal moves from the start position."""
    b = Board.standard()
    moves = MoveValidator.get_legal_moves(b, Color.WHITE)
    assert len(moves) == 20
