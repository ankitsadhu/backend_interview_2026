"""
tests/test_board.py — Board setup and query tests.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from chess_engine.board import Board
from chess_engine.models import Color, PieceType, Position


def test_initial_position_has_32_pieces():
    b = Board.standard()
    assert len(b.all_pieces()) == 32


def test_initial_white_pieces_count():
    b = Board.standard()
    assert len(b.find_pieces(Color.WHITE)) == 16


def test_initial_black_pieces_count():
    b = Board.standard()
    assert len(b.find_pieces(Color.BLACK)) == 16


def test_find_white_king():
    b = Board.standard()
    king_pos = b.find_king(Color.WHITE)
    assert king_pos == Position(0, 4)  # e1


def test_find_black_king():
    b = Board.standard()
    king_pos = b.find_king(Color.BLACK)
    assert king_pos == Position(7, 4)  # e8


def test_get_piece_e1_is_white_king():
    b = Board.standard()
    piece = b.get_piece(Position(0, 4))
    assert piece is not None
    assert piece.color == Color.WHITE
    assert piece.piece_type == PieceType.KING


def test_empty_square_returns_none():
    b = Board.standard()
    assert b.get_piece(Position(3, 3)) is None  # d4 is empty


def test_is_empty():
    b = Board.standard()
    assert b.is_empty(Position(4, 4))       # e5 is empty
    assert not b.is_empty(Position(0, 0))   # a1 has a rook


def test_is_enemy():
    b = Board.standard()
    assert b.is_enemy(Position(7, 0), Color.WHITE)  # black rook from white perspective
    assert not b.is_enemy(Position(0, 0), Color.WHITE)  # own rook


def test_clone_independence():
    b = Board.standard()
    clone = b.clone()
    # Removing a piece from clone shouldn't affect original
    clone.remove_piece(Position(0, 4))
    assert b.get_piece(Position(0, 4)) is not None
    assert clone.get_piece(Position(0, 4)) is None


def test_move_piece():
    b = Board.standard()
    captured = b.move_piece(Position(1, 4), Position(3, 4))  # e2-e4
    assert captured is None
    assert b.is_empty(Position(1, 4))
    assert b.get_piece(Position(3, 4)).piece_type == PieceType.PAWN


def test_fen_board_initial():
    b = Board.standard()
    fen = b.to_fen_board()
    assert fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"


def test_position_algebraic_roundtrip():
    for file_char in "abcdefgh":
        for rank in "12345678":
            pos = Position.from_algebraic(file_char + rank)
            assert pos.to_algebraic() == file_char + rank


def test_pawns_on_correct_ranks():
    b = Board.standard()
    for c in range(8):
        wp = b.get_piece(Position(1, c))
        assert wp is not None and wp.piece_type == PieceType.PAWN and wp.color == Color.WHITE
        bp = b.get_piece(Position(6, c))
        assert bp is not None and bp.piece_type == PieceType.PAWN and bp.color == Color.BLACK
