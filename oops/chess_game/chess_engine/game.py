"""
game.py — GameController: orchestrates the chess game.

Manages turns, move execution, undo, history, and game status.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .board import Board
from .check_detector import CheckDetector
from .models import Color, GameStatus, Move, Piece, PieceType, Position
from .move_validator import MoveValidator
from .pieces import PieceMoveGenerator


@dataclass
class _UndoRecord:
    """Snapshot needed to undo a move."""
    move             : Move
    en_passant_before: Optional[Position]
    halfmove_before  : int
    captured_piece   : Optional[Piece]
    moved_flag_before: bool


class GameController:
    """
    Full game orchestrator.

    Usage:
        game = GameController()
        legal = game.get_legal_moves()
        result = game.make_move(from_pos, to_pos)
    """

    def __init__(self, board: Optional[Board] = None) -> None:
        self.board          = board or Board.standard()
        self.current_turn   = Color.WHITE
        self.move_history   : List[Move]       = []
        self._undo_stack    : List[_UndoRecord] = []
        self.halfmove_clock = 0       # for 50-move rule
        self.fullmove_number= 1
        self._position_counts: Dict[str, int] = defaultdict(int)
        self._record_position()
        self._status        = GameStatus.IN_PROGRESS
        self._legal_moves_cache: Optional[List[Move]] = None

    # ----------------------------------------------------------
    # Properties
    # ----------------------------------------------------------

    @property
    def status(self) -> GameStatus:
        return self._status

    @property
    def is_game_over(self) -> bool:
        return self._status in (
            GameStatus.CHECKMATE, GameStatus.STALEMATE,
            GameStatus.DRAW_50_MOVE, GameStatus.DRAW_REPETITION,
            GameStatus.DRAW_INSUFFICIENT,
        )

    @property
    def winner(self) -> Optional[Color]:
        if self._status == GameStatus.CHECKMATE:
            return self.current_turn.opposite
        return None

    # ----------------------------------------------------------
    # Legal moves
    # ----------------------------------------------------------

    def get_legal_moves(self) -> List[Move]:
        if self._legal_moves_cache is None:
            self._legal_moves_cache = MoveValidator.get_legal_moves(
                self.board, self.current_turn
            )
        return self._legal_moves_cache

    def get_legal_moves_for(self, pos: Position) -> List[Move]:
        return [m for m in self.get_legal_moves() if m.from_pos == pos]

    # ----------------------------------------------------------
    # Make move
    # ----------------------------------------------------------

    def make_move(
        self,
        from_pos  : Position,
        to_pos    : Position,
        promotion : Optional[PieceType] = None,
    ) -> Move:
        """
        Execute a move.  Raises ValueError if illegal.
        Returns the executed Move with check/checkmate annotations.
        """
        if self.is_game_over:
            raise ValueError(f"Game is already over ({self._status.value})")

        piece = self.board.get_piece(from_pos)
        if piece is None:
            raise ValueError(f"No piece at {from_pos}")
        if piece.color != self.current_turn:
            raise ValueError(f"Not {piece.color.value}'s turn")

        # Find matching legal move
        legal = self.get_legal_moves()
        candidates = [
            m for m in legal
            if m.from_pos == from_pos and m.to_pos == to_pos
        ]

        if promotion:
            candidates = [m for m in candidates if m.promotion == promotion]
        elif any(m.promotion for m in candidates):
            # Default to queen promotion
            candidates = [m for m in candidates if m.promotion == PieceType.QUEEN]

        if not candidates:
            raise ValueError(
                f"Illegal move: {from_pos} → {to_pos} for {piece.piece_type.value}"
            )

        move = candidates[0]

        # Save undo state
        undo = _UndoRecord(
            move              = move,
            en_passant_before = self.board.en_passant_target,
            halfmove_before   = self.halfmove_clock,
            captured_piece    = move.captured.copy() if move.captured else None,
            moved_flag_before = piece.has_moved,
        )
        self._undo_stack.append(undo)

        # Execute on board
        self._execute_move(move)

        # Update clocks
        if move.captured or piece.piece_type == PieceType.PAWN:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        if self.current_turn == Color.BLACK:
            self.fullmove_number += 1

        # Switch turn
        self.current_turn = self.current_turn.opposite
        self._legal_moves_cache = None

        # Annotate check/checkmate
        opponent_legal = self.get_legal_moves()
        if CheckDetector.is_in_check(self.board, self.current_turn):
            if len(opponent_legal) == 0:
                move.gives_checkmate = True
            else:
                move.gives_check = True

        # Update status
        self._record_position()
        pos_count = self._position_counts.get(self.board.to_fen_board(), 1)
        self._status = CheckDetector.get_game_status(
            self.board, self.current_turn, opponent_legal,
            self.halfmove_clock, pos_count,
        )

        self.move_history.append(move)
        return move

    def make_move_algebraic(self, from_str: str, to_str: str,
                            promotion: Optional[PieceType] = None) -> Move:
        """Convenience: make_move using algebraic strings like 'e2', 'e4'."""
        return self.make_move(
            Position.from_algebraic(from_str),
            Position.from_algebraic(to_str),
            promotion,
        )

    # ----------------------------------------------------------
    # Undo
    # ----------------------------------------------------------

    def undo_move(self) -> Optional[Move]:
        if not self._undo_stack:
            return None

        undo = self._undo_stack.pop()
        move = undo.move

        # Reverse turn
        self.current_turn = self.current_turn.opposite
        if self.current_turn == Color.BLACK:
            self.fullmove_number -= 1

        # Restore piece to original position
        piece = self.board.remove_piece(move.to_pos)
        if piece:
            piece.has_moved = undo.moved_flag_before
        self.board.set_piece(move.from_pos, piece)

        # Restore promotion — put back the pawn
        if move.promotion and piece:
            piece.piece_type = PieceType.PAWN

        # Restore captured piece
        if move.is_en_passant:
            # Put captured pawn back on its row
            captured_pos = Position(move.from_pos.row, move.to_pos.col)
            self.board.set_piece(captured_pos, undo.captured_piece)
        elif undo.captured_piece:
            self.board.set_piece(move.to_pos, undo.captured_piece)

        # Reverse castling rook
        if move.is_castling:
            row = move.from_pos.row
            if move.is_kingside:
                rook = self.board.remove_piece(Position(row, 5))
                if rook:
                    rook.has_moved = False
                self.board.set_piece(Position(row, 7), rook)
            else:
                rook = self.board.remove_piece(Position(row, 3))
                if rook:
                    rook.has_moved = False
                self.board.set_piece(Position(row, 0), rook)

        # Restore state
        self.board.en_passant_target = undo.en_passant_before
        self.halfmove_clock = undo.halfmove_before
        self.move_history.pop()
        self._legal_moves_cache = None

        # Recompute status
        legal = self.get_legal_moves()
        pos_count = self._position_counts.get(self.board.to_fen_board(), 1)
        self._status = CheckDetector.get_game_status(
            self.board, self.current_turn, legal,
            self.halfmove_clock, pos_count,
        )

        return move

    # ----------------------------------------------------------
    # Internal
    # ----------------------------------------------------------

    def _execute_move(self, move: Move) -> None:
        """Apply move to the real board."""
        board = self.board

        # En passant capture — remove captured pawn from its actual square
        if move.is_en_passant:
            captured_pos = Position(move.from_pos.row, move.to_pos.col)
            board.remove_piece(captured_pos)

        # Move the piece
        board.remove_piece(move.from_pos)
        moved_piece = move.piece.copy()
        moved_piece.has_moved = True

        # Promotion
        if move.promotion:
            moved_piece.piece_type = move.promotion

        board.set_piece(move.to_pos, moved_piece)

        # Castling — also move the rook
        if move.is_castling:
            row = move.from_pos.row
            if move.is_kingside:
                rook = board.remove_piece(Position(row, 7))
                if rook:
                    rook.has_moved = True
                    board.set_piece(Position(row, 5), rook)
            else:
                rook = board.remove_piece(Position(row, 0))
                if rook:
                    rook.has_moved = True
                    board.set_piece(Position(row, 3), rook)

        # Set en passant target
        if (move.piece.piece_type == PieceType.PAWN
                and abs(move.to_pos.row - move.from_pos.row) == 2):
            ep_row = (move.from_pos.row + move.to_pos.row) // 2
            board.en_passant_target = Position(ep_row, move.from_pos.col)
        else:
            board.en_passant_target = None

    def _record_position(self) -> None:
        fen = self.board.to_fen_board()
        self._position_counts[fen] += 1
