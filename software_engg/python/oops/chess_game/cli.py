"""
cli.py — Rich-powered interactive Chess CLI.

Features:
  - Unicode board rendering with coloured squares
  - Move input in algebraic notation or coordinate form (e2e4)
  - Legal move highlighting
  - Move history panel
"""
from __future__ import annotations

import sys

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from chess_engine import (
    Board, Color, GameController, GameStatus,
    Move, NotationParser, PieceType, Position,
)

console = Console()


# ============================================================
# Board rendering
# ============================================================

LIGHT_SQUARE  = "#F0D9B5"
DARK_SQUARE   = "#B58863"
HIGHLIGHT_CLR = "#AADD55"
CHECK_CLR     = "#FF4444"


def render_board(
    game: GameController,
    perspective: Color = Color.WHITE,
    highlights: set | None = None,
) -> Table:
    """Render the board as a Rich Table with Unicode pieces."""
    board = game.board
    highlights = highlights or set()

    table = Table(
        box=None, show_header=False, show_footer=False,
        padding=0, show_edge=False,
    )
    # Column for rank labels + 8 for squares
    for _ in range(9):
        table.add_column(width=4, justify="center")

    rows = range(7, -1, -1) if perspective == Color.WHITE else range(8)
    for r in rows:
        cells: list[str | Text] = [Text(f" {r+1} ", style="bold dim")]
        for c in range(8):
            pos = Position(r, c)
            piece = board.get_piece(pos)
            is_light = (r + c) % 2 == 1
            bg = LIGHT_SQUARE if is_light else DARK_SQUARE

            if pos in highlights:
                bg = HIGHLIGHT_CLR

            king_pos = board.find_king(game.current_turn)
            in_check = game.status in (GameStatus.CHECK, GameStatus.CHECKMATE)
            if in_check and pos == king_pos:
                bg = CHECK_CLR

            symbol = piece.unicode_symbol if piece else " "
            fg = "white" if piece and piece.color == Color.WHITE else "black"
            cells.append(Text(f" {symbol} ", style=f"{fg} on {bg}"))

        table.add_row(*cells)

    # File labels
    file_labels = [Text("   ", style="dim")]
    for f in "abcdefgh":
        file_labels.append(Text(f" {f} ", style="bold dim"))
    table.add_row(*file_labels)

    return table


# ============================================================
# Move history
# ============================================================

def render_history(game: GameController) -> Panel:
    lines = []
    for i in range(0, len(game.move_history), 2):
        move_num = i // 2 + 1
        white_move = game.move_history[i].to_algebraic() if i < len(game.move_history) else ""
        black_move = game.move_history[i+1].to_algebraic() if i+1 < len(game.move_history) else ""
        lines.append(f"{move_num:>3}. {white_move:<8} {black_move}")

    text = "\n".join(lines[-20:]) if lines else "[dim]No moves yet[/]"
    return Panel(text, title="[bold]Move History[/]", border_style="cyan",
                 width=28, height=24)


# ============================================================
# Status display
# ============================================================

def render_status(game: GameController) -> str:
    status_map = {
        GameStatus.IN_PROGRESS      : f"[bold]{game.current_turn.value}'s turn[/]",
        GameStatus.CHECK            : f"[bold red]CHECK![/] {game.current_turn.value} to move",
        GameStatus.CHECKMATE        : f"[bold green]CHECKMATE![/] {game.winner.value} wins!",
        GameStatus.STALEMATE        : "[bold yellow]STALEMATE — Draw[/]",
        GameStatus.DRAW_50_MOVE     : "[bold yellow]DRAW — 50 move rule[/]",
        GameStatus.DRAW_REPETITION  : "[bold yellow]DRAW — Threefold repetition[/]",
        GameStatus.DRAW_INSUFFICIENT: "[bold yellow]DRAW — Insufficient material[/]",
    }
    return status_map.get(game.status, str(game.status))


# ============================================================
# Input parsing
# ============================================================

def parse_input(text: str, game: GameController) -> Move | None:
    """
    Accept moves in:
      - SAN:  e4, Nf3, O-O, exd5, e8=Q
      - Coordinate: e2e4, e7e8q (with optional promo char)
    """
    text = text.strip()
    if not text:
        return None

    # Try SAN first
    move = NotationParser.parse(text, game.board, game.current_turn)
    if move:
        return move

    # Try coordinate format (e2e4, e7e8q)
    if len(text) in (4, 5):
        try:
            from_pos = Position.from_algebraic(text[:2])
            to_pos   = Position.from_algebraic(text[2:4])
            promo    = None
            if len(text) == 5:
                promo_map = {"q": PieceType.QUEEN, "r": PieceType.ROOK,
                             "b": PieceType.BISHOP, "n": PieceType.KNIGHT}
                promo = promo_map.get(text[4].lower())
            # Validate
            legal = game.get_legal_moves()
            candidates = [m for m in legal if m.from_pos == from_pos and m.to_pos == to_pos]
            if promo:
                candidates = [m for m in candidates if m.promotion == promo]
            elif candidates and candidates[0].promotion:
                candidates = [m for m in candidates if m.promotion == PieceType.QUEEN]
            if candidates:
                return candidates[0]
        except ValueError:
            pass

    return None


# ============================================================
# Main game loop
# ============================================================

def main():
    console.print(Panel.fit(
        "[bold cyan]♔  Interactive Chess  ♚[/]\n"
        "[dim]Enter moves in algebraic (e4, Nf3, O-O) or coordinate (e2e4) notation[/]\n"
        "[dim]Commands: 'undo', 'legal', 'board', 'quit'[/]",
        border_style="cyan",
    ))

    game = GameController()

    while True:
        console.print()
        console.print(render_board(game))
        console.print(f"\n  {render_status(game)}")

        if game.is_game_over:
            console.print("\n[bold]Game Over![/]")
            break

        try:
            text = console.input(f"\n  [bold]{game.current_turn.value}[/]> ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye![/]")
            break

        if text.lower() == "quit":
            console.print("[dim]Goodbye![/]")
            break

        if text.lower() == "undo":
            undone = game.undo_move()
            if undone:
                console.print(f"  [yellow]↩ Undid {undone.to_algebraic()}[/]")
            else:
                console.print("  [dim]Nothing to undo[/]")
            continue

        if text.lower() in ("legal", "moves"):
            legal = game.get_legal_moves()
            moves_str = ", ".join(m.to_algebraic() for m in legal)
            console.print(f"  [cyan]{len(legal)} legal moves:[/] {moves_str}")
            continue

        if text.lower() == "board":
            console.print(render_board(game))
            continue

        if text.lower() == "history":
            console.print(render_history(game))
            continue

        move = parse_input(text, game)
        if move is None:
            console.print(f"  [red]Invalid move: '{text}'[/]  (type 'legal' to see options)")
            continue

        try:
            result = game.make_move(move.from_pos, move.to_pos, move.promotion)
            san = NotationParser.format_move(result)
            console.print(f"  [green]✓ {san}[/]")
        except ValueError as e:
            console.print(f"  [red]{e}[/]")


if __name__ == "__main__":
    main()
