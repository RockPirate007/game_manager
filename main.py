#!/usr/bin/env python3
"""Game Manager — Текстовый футбольный менеджер"""

import sys
import os
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.console import ConsoleUI
from ui.menus.main_menu import MainMenu
from ui.menus.club_menu import ClubMenu
from ui.menus.match_menu import MatchMenu
from ui.menus.tactics_menu import TacticsMenu
from ui.menus.transfers_menu import TransfersMenu
from ui.menus.finance_menu import FinanceMenu
from ui.menus.news_menu import NewsMenu
from ui.menus.season_menu import SeasonMenu


def setup_signal_handlers():
    signal.signal(signal.SIGINT, lambda *_: (print("\n\nДо свидания! 👋"), sys.exit(0)))


def new_game_flow(console: ConsoleUI):
    """Новая игра: выбор клуба и старт сезона."""
    console.clear()
    console.print_header("⚽ НОВАЯ ИГРА ⚽")

    clubs = [
        "Manchester City", "Arsenal", "Liverpool", "Chelsea",
        "Manchester United", "Tottenham", "Newcastle", "Aston Villa",
        "Real Madrid", "Barcelona", "Atletico Madrid", "Real Sociedad",
    ]

    console.print("[bold]Выберите клуб:[/]")
    for i, club in enumerate(clubs, 1):
        console.print(f"  [cyan]{i}.[/] {club}")

    console.print()
    choice = console.input("[bold]Ваш выбор: [/]")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(clubs):
            selected = clubs[idx]
            console.print_success(f"Вы выбрали: {selected}")
            console.wait_for_key()

            club_menu = ClubMenu(console, {"club_name": selected})
            club_menu.run()
        else:
            console.print_error("Неверный номер")
    except ValueError:
        console.print_error("Введите число")


def load_game_flow(console: ConsoleUI):
    """Загрузка игры."""
    console.clear()
    console.print_header("📂 ЗАГРУЗКА ИГРЫ")
    console.print("[dim]Сохранённые игры не найдены.[/]")
    console.wait_for_key()


def settings_flow(console: ConsoleUI):
    """Настройки."""
    console.clear()
    console.print_header("⚙️ НАСТРОЙКИ")
    console.print("[dim]Настройки будут доступны в следующей версии.[/]")
    console.wait_for_key()


def about_flow(console: ConsoleUI):
    """Об игре."""
    console.clear()
    console.print_header("ℹ️ ОБ ИГРЕ")
    console.print("""
[bold]FOOTBALL MANAGER 2026[/bold]

Симулятор менеджера футбольного клуба.
Управляйте командой, выигрывайте трофеи и станьте легендой!

[bold cyan]Возможности:[/]
• Управление составом и тактикой
• Трансферы и скаутинг
• Финансы и инфраструктура
• Обучение молодёжи
• Проведение матчей в реальном времени
• Новости и пресс-конференции

[dim]Версия 2.0.0 | 2026[/]
""")
    console.wait_for_key()


def main():
    setup_signal_handlers()

    console = ConsoleUI()

    while True:
        try:
            console.clear()
            menu = MainMenu(console)
            result = menu.run()

            if result == "exit":
                print("\nДо свидания! 👋")
                break
            elif result == "new_game":
                new_game_flow(console)
            elif result == "load_game":
                load_game_flow(console)
            elif result == "settings":
                settings_flow(console)
            else:
                about_flow(console)

        except KeyboardInterrupt:
            print("\n\nДо свидания! 👋")
            break
        except Exception as e:
            console.print_error(f"Ошибка: {e}")
            console.wait_for_key()


if __name__ == "__main__":
    main()
