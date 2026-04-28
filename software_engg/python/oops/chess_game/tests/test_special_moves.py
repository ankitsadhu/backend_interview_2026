"""
tests/test_special_moves.py — Castling, en passant, promotion tests.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from chess_engine.board import Board
from chess_engine.game import GameController
from chess_engine.models import Color, GameStatus, Piece, PieceType, Position
from chess_engine.move_validator import MoveValidator


# ============================================================
# Castling
# ============================================================

def test_kingside_castling():
    """White castles kingside: Ke1→g1, Rh1→f1."""
    b = Board()
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING))   # Ke1
    b.set_piece(Position(0, 7), Piece(Color.WHITE, PieceType.ROOK))   # Rh1
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    game = GameController(b)
    move = game.make_move_algebraic("e1", "g1")
    assert move.is_castling
    assert move.is_kingside
    # King should be on g1
    assert game.board.get_piece(Position(0, 6)).piece_type == PieceType.KING
    # Rook should be on f1
    assert game.board.get_piece(Position(0, 5)).piece_type == PieceType.ROOK
    # Original squares empty
    assert game.board.is_empty(Position(0, 4))
    assert game.board.is_empty(Position(0, 7))


def test_queenside_castling():
    """White castles queenside: Ke1→c1, Ra1→d1."""
    b = Board()
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING))   # Ke1
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.ROOK))   # Ra1
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    game = GameController(b)
    move = game.make_move_algebraic("e1", "c1")
    assert move.is_castling
    assert not move.is_kingside
    assert game.board.get_piece(Position(0, 2)).piece_type == PieceType.KING
    assert game.board.get_piece(Position(0, 3)).piece_type == PieceType.ROOK


def test_cannot_castle_after_king_moved():
    b = Board()
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING, has_moved=True))
    b.set_piece(Position(0, 7), Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    legal = MoveValidator.get_legal_moves(b, Color.WHITE)
    castling_moves = [m for m in legal if m.is_castling]
    assert len(castling_moves) == 0


def test_cannot_castle_through_occupied_square():
    b = Board()
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING))
    b.set_piece(Position(0, 7), Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece(Position(0, 5), Piece(Color.WHITE, PieceType.BISHOP))  # f1 occupied
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    legal = MoveValidator.get_legal_moves(b, Color.WHITE)
    castling_moves = [m for m in legal if m.is_castling]
    assert len(castling_moves) == 0


def test_cannot_castle_while_in_check():
    b = Board()
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING))   # Ke1
    b.set_piece(Position(0, 7), Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.ROOK))   # attacks e-file
    b.set_piece(Position(7, 0), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    legal = MoveValidator.get_legal_moves(b, Color.WHITE)
    castling_moves = [m for m in legal if m.is_castling]
    assert len(castling_moves) == 0


def test_cannot_castle_through_check():
    """King would pass through f1 attacked by bishop."""
    b = Board()
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING))
    b.set_piece(Position(0, 7), Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece(Position(2, 3), Piece(Color.BLACK, PieceType.BISHOP, has_moved=True))  # attacks f1
    b.set_piece(Position(7, 0), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    legal = MoveValidator.get_legal_moves(b, Color.WHITE)
    castling_moves = [m for m in legal if m.is_castling and m.is_kingside]
    assert len(castling_moves) == 0


# ============================================================
# En Passant
# ============================================================

def test_en_passant_capture():
    """After black pawn double-advances, white can capture en passant."""
    b = Board()
    # White pawn on e5
    b.set_piece(Position(4, 4), Piece(Color.WHITE, PieceType.PAWN, has_moved=True))
    # Black pawn on d7 (will double-advance to d5)
    b.set_piece(Position(6, 3), Piece(Color.BLACK, PieceType.PAWN))
    # Kings
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING, has_moved=True))
    b.set_piece(Position(7, 7), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    game = GameController(b)
    game.current_turn = Color.BLACK

    # Black plays d7-d5
    game.make_move_algebraic("d7", "d5")
    assert game.board.en_passant_target == Position(5, 3)  # d6

    # White captures en passant: e5xd6
    move = game.make_move_algebraic("e5", "d6")
    assert move.is_en_passant
    # d5 should now be empty (captured pawn removed)
    assert game.board.is_empty(Position(4, 3))
    # White pawn should be on d6
    assert game.board.get_piece(Position(5, 3)).piece_type == PieceType.PAWN


def test_en_passant_only_available_immediately():
    """En passant must be taken immediately or it's gone."""
    b = Board()
    b.set_piece(Position(4, 4), Piece(Color.WHITE, PieceType.PAWN, has_moved=True))
    b.set_piece(Position(6, 3), Piece(Color.BLACK, PieceType.PAWN))
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING, has_moved=True))
    b.set_piece(Position(7, 7), Piece(Color.BLACK, PieceType.KING, has_moved=True))
    # Extra pieces to make other moves available
    b.set_piece(Position(0, 7), Piece(Color.WHITE, PieceType.ROOK, has_moved=True))
    b.set_piece(Position(7, 0), Piece(Color.BLACK, PieceType.ROOK, has_moved=True))

    game = GameController(b)
    game.current_turn = Color.BLACK
    game.make_move_algebraic("d7", "d5")  # opens en passant

    # White plays a different move instead
    game.make_move_algebraic("h1", "h2")  # Rh2

    # Now en passant should NOT be available anymore
    assert game.board.en_passant_target is None


# ============================================================
# Promotion
# ============================================================

def test_pawn_promotion_to_queen():
    b = Board()
    b.set_piece(Position(6, 0), Piece(Color.WHITE, PieceType.PAWN, has_moved=True))  # a7
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING, has_moved=True))
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    game = GameController(b)
    move = game.make_move_algebraic("a7", "a8", promotion=PieceType.QUEEN)
    assert move.promotion == PieceType.QUEEN
    promoted = game.board.get_piece(Position(7, 0))
    assert promoted.piece_type == PieceType.QUEEN
    assert promoted.color == Color.WHITE


def test_pawn_promotion_to_knight():
    b = Board()
    b.set_piece(Position(6, 0), Piece(Color.WHITE, PieceType.PAWN, has_moved=True))
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING, has_moved=True))
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    game = GameController(b)
    move = game.make_move_algebraic("a7", "a8", promotion=PieceType.KNIGHT)
    promoted = game.board.get_piece(Position(7, 0))
    assert promoted.piece_type == PieceType.KNIGHT


def test_promotion_default_queen():
    """If no promotion piece specified, default to queen."""
    b = Board()
    b.set_piece(Position(6, 0), Piece(Color.WHITE, PieceType.PAWN, has_moved=True))
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING, has_moved=True))
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    game = GameController(b)
    move = game.make_move_algebraic("a7", "a8")  # no promo specified
    promoted = game.board.get_piece(Position(7, 0))
    assert promoted.piece_type == PieceType.QUEEN


# ============================================================
# Undo special moves
# ============================================================

def test_undo_castling():
    b = Board()
    b.set_piece(Position(0, 4), Piece(Color.WHITE, PieceType.KING))
    b.set_piece(Position(0, 7), Piece(Color.WHITE, PieceType.ROOK))
    b.set_piece(Position(7, 4), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    game = GameController(b)
    game.make_move_algebraic("e1", "g1")  # castle

    game.undo_move()

    # King back on e1
    assert game.board.get_piece(Position(0, 4)).piece_type == PieceType.KING
    assert not game.board.get_piece(Position(0, 4)).has_moved
    # Rook back on h1
    assert game.board.get_piece(Position(0, 7)).piece_type == PieceType.ROOK
    # g1 and f1 empty
    assert game.board.is_empty(Position(0, 6))
    assert game.board.is_empty(Position(0, 5))


def test_undo_en_passant():
    b = Board()
    b.set_piece(Position(4, 4), Piece(Color.WHITE, PieceType.PAWN, has_moved=True))
    b.set_piece(Position(6, 3), Piece(Color.BLACK, PieceType.PAWN))
    b.set_piece(Position(0, 0), Piece(Color.WHITE, PieceType.KING, has_moved=True))
    b.set_piece(Position(7, 7), Piece(Color.BLACK, PieceType.KING, has_moved=True))

    game = GameController(b)
    game.current_turn = Color.BLACK
    game.make_move_algebraic("d7", "d5")
    game.make_move_algebraic("e5", "d6")  # en passant

    game.undo_move()  # undo en passant

    # White pawn back on e5
    assert game.board.get_piece(Position(4, 4)).piece_type == PieceType.PAWN
    # Black pawn restored on d5
    assert game.board.get_piece(Position(4, 3)).piece_type == PieceType.PAWN
    # d6 empty
    assert game.board.is_empty(Position(5, 3))
