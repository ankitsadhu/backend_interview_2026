"""
demo.py — Chess game demonstrations.

1. Scholar's Mate (4-move checkmate)
2. A longer game showing castling, captures, check
"""
from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from chess_engine import GameController, GameStatus, Color, PieceType, Position

console = Console()


# ============================================================
# Board renderer (simplified ASCII for demo)
# ============================================================

UNICODE = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",
}

LIGHT_BG = "#F0D9B5"
DARK_BG  = "#B58863"


def print_board(game: GameController, title: str = "") -> None:
    table = Table(box=None, show_header=False, padding=0, show_edge=False,
                  title=title if title else None)
    for _ in range(9):
        table.add_column(width=4, justify="center")

    for r in range(7, -1, -1):
        cells = [Text(f" {r+1} ", style="bold dim")]
        for c in range(8):
            piece = game.board.get_piece(Position(r, c))
            bg = LIGHT_BG if (r + c) % 2 == 1 else DARK_BG
            if piece:
                sym = piece.unicode_symbol
                fg = "white" if piece.color == Color.WHITE else "black"
            else:
                sym = " "
                fg  = "white"
            cells.append(Text(f" {sym} ", style=f"{fg} on {bg}"))
        table.add_row(*cells)

    files = [Text("   ")] + [Text(f" {f} ", style="bold dim") for f in "abcdefgh"]
    table.add_row(*files)
    console.print(table)


def status_text(game: GameController) -> str:
    s = game.status
    if s == GameStatus.CHECKMATE:
        return f"[bold green]CHECKMATE! {game.winner.value} wins![/]"
    if s == GameStatus.CHECK:
        return f"[bold red]CHECK![/] {game.current_turn.value} to move"
    if s == GameStatus.STALEMATE:
        return "[bold yellow]STALEMATE — Draw[/]"
    return f"[dim]{game.current_turn.value}'s turn[/]"


# ============================================================
# Demo 1: Scholar's Mate
# ============================================================

def demo_scholars_mate():
    console.print(Panel.fit(
        "[bold cyan]♔  Demo 1: Scholar's Mate  ♚[/]\n"
        "[dim]The fastest checkmate — just 4 moves![/]",
        border_style="cyan",
    ))

    game = GameController()
    print_board(game, "[dim]Starting position[/]")

    moves = [
        ("e2", "e4", "1. e4  — White opens with king's pawn"),
        ("e7", "e5", "1... e5 — Black mirrors"),
        ("f1", "c4", "2. Bc4 — Bishop targets f7"),
        ("b8", "c6", "2... Nc6 — Black develops knight"),
        ("d1", "h5", "3. Qh5 — Queen threatens f7 + e5"),
        ("g8", "f6", "3... Nf6 — Black tries to chase the queen"),
        ("h5", "f7", "4. Qxf7# — [bold red]CHECKMATE![/]"),
    ]

    for from_sq, to_sq, description in moves:
        console.print()
        result = game.make_move_algebraic(from_sq, to_sq)
        san = result.to_algebraic()
        console.print(f"  [bold]{san}[/]  {description}")
        print_board(game, status_text(game))

    console.print()
    console.print(Panel.fit(
        f"[bold green]Result: {game.status.value}[/]\n"
        f"Winner: [bold]{game.winner.value}[/] in {len(game.move_history)} moves",
        border_style="green",
    ))


# ============================================================
# Demo 2: Game with castling, captures, and check
# ============================================================

def demo_sample_game():
    console.print()
    console.print(Panel.fit(
        "[bold cyan]♔  Demo 2: Sample Game — Castling & Tactics  ♚[/]\n"
        "[dim]Featuring kingside castling, piece exchanges, and check[/]",
        border_style="cyan",
    ))

    game = GameController()

    moves = [
        # Opening — Italian Game
        ("e2", "e4", "1. e4"),
        ("e7", "e5", "1... e5"),
        ("g1", "f3", "2. Nf3"),
        ("b8", "c6", "2... Nc6"),
        ("f1", "c4", "3. Bc4"),
        ("f8", "c5", "3... Bc5"),
        # Castling
        ("e1", "g1", "4. O-O  — [cyan]White castles kingside![/]"),
        ("g8", "f6", "4... Nf6"),
        ("d2", "d3", "5. d3"),
        ("d7", "d6", "5... d6"),
        # Development and play
        ("c1", "g5", "6. Bg5  — Pinning knight to queen"),
        ("e8", "g8", "6... O-O — [cyan]Black castles too[/]"),
        ("b1", "c3", "7. Nc3"),
        ("h7", "h6", "7... h6"),
        ("g5", "h4", "8. Bh4"),
        ("c5", "b4", "8... Bb4"),
    ]

    for from_sq, to_sq, description in moves:
        result = game.make_move_algebraic(from_sq, to_sq)
        san = result.to_algebraic()
        console.print(f"  [bold]{san:<8}[/] {description}")

    console.print()
    print_board(game, f"After {len(game.move_history)} moves — {status_text(game)}")

    # Show legal moves
    legal = game.get_legal_moves()
    console.print(f"\n  [cyan]{game.current_turn.value} has {len(legal)} legal moves[/]")

    # Demonstrate undo
    console.print("\n  [yellow]↩ Undoing last 2 moves...[/]")
    game.undo_move()
    game.undo_move()
    print_board(game, f"After undo — {status_text(game)}")

    console.print(Panel.fit(
        f"[bold]Demo 2 complete[/] — {len(game.move_history)} moves played",
        border_style="green",
    ))


# ============================================================
# Demo 3: Stalemate
# ============================================================

def demo_stalemate():
    console.print()
    console.print(Panel.fit(
        "[bold cyan]♔  Demo 3: Stalemate Detection  ♚[/]\n"
        "[dim]A minimal position where Black has no legal moves[/]",
        border_style="cyan",
    ))

    from chess_engine.board import Board
    from chess_engine.models import Piece, PieceType as PT, Color as C

    # Custom position: White Kc6, Qa7; Black Ka8
    board = Board()
    board.set_piece(Position(7, 0), Piece(C.BLACK, PT.KING, has_moved=True))  # Ka8
    board.set_piece(Position(4, 2), Piece(C.WHITE, PT.KING, has_moved=True))  # Kc5
    board.set_piece(Position(5, 0), Piece(C.WHITE, PT.QUEEN, has_moved=True)) # Qa6

    game = GameController(board)
    game.current_turn = C.BLACK

    print_board(game, "Custom position — Black to move")

    # Force the stalemate status check
    legal = game.get_legal_moves()
    console.print(f"  Black has [bold]{len(legal)}[/] legal move(s)")
    console.print(f"  In check? [bold]{'Yes' if game.status == GameStatus.CHECK else 'No'}[/]")

    # Check if it's stalemate
    from chess_engine.check_detector import CheckDetector
    is_stale = CheckDetector.is_stalemate(board, C.BLACK, legal)
    console.print(f"  Stalemate? [bold yellow]{'Yes' if is_stale else 'No'}[/]")

    console.print(Panel.fit("[bold]Stalemate demo complete[/]", border_style="green"))


# ============================================================
# Main
# ============================================================

def main():
    console.rule("[bold cyan]♔  Chess Engine — Demos  ♚[/]")
    demo_scholars_mate()
    demo_sample_game()
    demo_stalemate()
    console.rule("[bold green]All demos complete[/]")


if __name__ == "__main__":
    main()
