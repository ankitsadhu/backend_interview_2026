"""
tests/test_check_detection.py — Check, checkmate, stalemate, draw tests.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from chess_engine.board import Board
from chess_engine.check_detector import CheckDetector
from chess_engine.game import GameController
from chess_engine.models import Color, GameStatus, Piece, PieceType, Position
from chess_engine.move_validator import MoveValidator


# ============================================================
# Check detection
# ============================================================

def test_initial_position_not_in_check():
    b = Board.standard()
    assert not CheckDetector.is_in_check(b, Color.WHITE)
    assert not CheckDetector.is_in_check(b, Color.BLACK)


def test_check_by_rook():
    b = Board()
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING))
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.ROOK))   # rook on same file
    b.set_piece(Position(7, 0), Piece(Color.BLACK, PieceType.KING))
    assert CheckDetector.is_in_check(b, Color.WHITE)


def test_check_by_bishop():
    b = Board()
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING))   # Ka1
    b.set_piece(Position(3, 3), Piece(Color.BLACK, PieceType.BISHOP)) # Bd4 — diagonal
    b.set_piece(Position(7, 7), Piece(Color.BLACK, PieceType.KING))
    assert CheckDetector.is_in_check(b, Color.WHITE)


def test_check_by_knight():
    b = Board()
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING))   # Ke1
    b.set_piece(Position(2, 3), Piece(Color.BLACK, PieceType.KNIGHT)) # Nd3 — L-shape
    b.set_piece(Position(7, 0), Piece(Color.BLACK, PieceType.KING))
    assert CheckDetector.is_in_check(b, Color.WHITE)


def test_check_by_pawn():
    b = Board()
    b.set_piece(Position(3, 3), Piece(Color.WHITE, PieceType.KING))   # Kd4
    b.set_piece(Position(4, 4), Piece(Color.BLACK, PieceType.PAWN, has_moved=True))  # Pe5
    b.set_piece(Position(7, 0), Piece(Color.BLACK, PieceType.KING))
    assert CheckDetector.is_in_check(b, Color.WHITE)


def test_no_check_pawn_forward():
    """Pawn in front of king does NOT give check (pawn only attacks diagonally)."""
    b = Board()
    b.set_piece(Position(3, 3), Piece(Color.WHITE, PieceType.KING))
    b.set_piece(Position(4, 3), Piece(Color.BLACK, PieceType.PAWN, has_moved=True))
    b.set_piece(Position(7, 0), Piece(Color.BLACK, PieceType.KING))
    assert not CheckDetector.is_in_check(b, Color.WHITE)


# ============================================================
# Checkmate
# ============================================================

def test_scholars_mate_is_checkmate():
    """Replay Scholar's Mate and verify checkmate."""
    game = GameController()
    game.make_move_algebraic("e2", "e4")  # 1. e4
    game.make_move_algebraic("e7", "e5")  # 1... e5
    game.make_move_algebraic("f1", "c4")  # 2. Bc4
    game.make_move_algebraic("b8", "c6")  # 2... Nc6
    game.make_move_algebraic("d1", "h5")  # 3. Qh5
    game.make_move_algebraic("g8", "f6")  # 3... Nf6
    game.make_move_algebraic("h5", "f7")  # 4. Qxf7#

    assert game.status == GameStatus.CHECKMATE
    assert game.winner == Color.WHITE


def test_back_rank_mate():
    """Classic back-rank mate: rook delivers on 8th rank."""
    b = Board()
    # White Ka1, Rh1; Black Kf8 boxed in by own pawns e7,f7,g7
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING, has_moved=True))  # Ka1
    b.set_piece(Position(0, 7), Piece(Color.WHITE, PieceType.ROOK, has_moved=True))  # Rh1
    b.set_piece(Position(7, 5), Piece(Color.BLACK, PieceType.KING, has_moved=True))  # Kf8
    b.set_piece(Position(6, 4), Piece(Color.BLACK, PieceType.PAWN, has_moved=True))  # e7
    b.set_piece(Position(6, 5), Piece(Color.BLACK, PieceType.PAWN, has_moved=True))  # f7
    b.set_piece(Position(6, 6), Piece(Color.BLACK, PieceType.PAWN, has_moved=True))  # g7

    game = GameController(b)
    game.make_move_algebraic("h1", "h8")  # Rh8#

    assert game.status == GameStatus.CHECKMATE
    assert game.winner == Color.WHITE


# ============================================================
# Stalemate
# ============================================================

def test_stalemate_king_only():
    """K+Q vs K in a stalemate position."""
    # Black Ka8, White Kc6 + Qb6
    # a7 covered by Qb6 (diagonal), b7 covered by Kc6+Qb6, b8 covered by Kc6+Qb6
    # Qb6 does NOT check Ka8 (different file, rank, diagonal)
    b = Board()
    b.set_piece(Position(7, 0), Piece(Color.BLACK, PieceType.KING, has_moved=True))  # Ka8
    b.set_piece(Position(5, 2), Piece(Color.WHITE, PieceType.KING, has_moved=True))  # Kc6
    b.set_piece(Position(5, 1), Piece(Color.WHITE, PieceType.QUEEN, has_moved=True)) # Qb6

    legal = MoveValidator.get_legal_moves(b, Color.BLACK)
    assert len(legal) == 0
    assert not CheckDetector.is_in_check(b, Color.BLACK)
    assert CheckDetector.is_stalemate(b, Color.BLACK, legal)


# ============================================================
# Insufficient material
# ============================================================

def test_insufficient_king_vs_king():
    b = Board()
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING))
    b.set_piece(Position(7, 7), Piece(Color.BLACK, PieceType.KING))
    assert CheckDetector.is_insufficient_material(b)


def test_insufficient_king_bishop_vs_king():
    b = Board()
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING))
    b.set_piece(Position(0, 2), Piece(Color.WHITE, PieceType.BISHOP))
    b.set_piece(Position(7, 7), Piece(Color.BLACK, PieceType.KING))
    assert CheckDetector.is_insufficient_material(b)


def test_insufficient_king_knight_vs_king():
    b = Board()
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING))
    b.set_piece(Position(2, 1), Piece(Color.WHITE, PieceType.KNIGHT))
    b.set_piece(Position(7, 7), Piece(Color.BLACK, PieceType.KING))
    assert CheckDetector.is_insufficient_material(b)


def test_sufficient_king_rook_vs_king():
    b = Board()
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING))
    b.set_piece(Position(0, 7), Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece(Position(7, 7), Piece(Color.BLACK, PieceType.KING))
    assert not CheckDetector.is_insufficient_material(b)


# ============================================================
# Move doesn't leave own king in check
# ============================================================

def test_pinned_piece_cant_move():
    """Bishop pinned to king by enemy rook — cannot move off the pin line."""
    b = Board()
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING))    # Ka1
    b.set_piece(Position(0, 3), Piece(Color.WHITE, PieceType.BISHOP))  # Bd1 — on rank 1
    b.set_piece(Position(0, 7), Piece(Color.BLACK, PieceType.ROOK))    # Rh1 — pins bishop
    b.set_piece(Position(7, 7), Piece(Color.BLACK, PieceType.KING))

    legal = MoveValidator.get_legal_moves_for_piece(b, Position(0, 3))
    # Bishop can only move ALONG the rank (to block / stay on pin line)
    # But bishop moves diagonally, so it cannot stay on rank 1 → 0 legal moves
    assert len(legal) == 0
