"""Меню управления клубом."""

from typing import Any, Dict, Optional

from ..console import ConsoleUI
from ..widgets import (
    create_player_table,
    create_team_table,
    create_match_fixture,
    create_stats_display,
    create_financial_display,
    create_news_card,
)


class ClubMenu:
    """Меню управления клубом."""

    def __init__(self, console: ConsoleUI, club_data: Optional[Dict[str, Any]] = None):
        """
        Инициализация меню клуба.

        Args:
            console: Объект консоли
            club_data: Данные клуба
        """
        self.console = console
        self.club_data = club_data or self._default_club_data()
        self.options = [
            ("squad", "👥 Состав"),
            ("tactics", "📋 Тактика"),
            ("transfers", "💰 Трансферы"),
            ("finances", "💎 Финансы"),
            ("training", "🏋️ Тренировки"),
            ("youth", "⭐ Молодёжь"),
            ("calendar", "📅 Календарь"),
            ("news", "📰 Новости"),
            ("save", "💾 Сохранить"),
            ("settings", "⚙️ Настройки"),
            ("back", "◀️ Назад"),
        ]

    def _default_club_data(self) -> Dict[str, Any]:
        """Данные клуба по умолчанию."""
        return {
            "name": "Мой клуб",
            "league": "Премьер-лига",
            "position": 1,
            "points": 0,
            "balance": 50_000_000,
            "transfer_budget": 20_000_000,
            "wage_bill": 1_500_000,
            "stadium": "Стадион",
            "capacity": 50000,
            "fans": 25000,
            "form": "WWWWW",
            "next_match": {
                "home_team": "Мой клуб",
                "away_team": "Соперник",
                "matchday": 1,
                "date": "15 июня 2026",
            },
            "squad_count": 25,
            "avg_rating": 72,
            "morale": 75,
        }

    def display(self) -> None:
        """Отобразить меню клуба."""
        self.console.clear()

        club = self.club_data
        team_name = club.get("name", "Мой клуб")

        # Заголовок
        self.console.print_header(
            f"⚽ {team_name}",
            f"Лига: {club.get('league', '?')} | Позиция: {club.get('position', '?')} | Очки: {club.get('points', 0)}"
        )

        # Информация о клубе
        from rich.table import Table

        info_table = Table(show_header=False, show_lines=False, expand=True)
        info_table.add_column("Параметр", style="dim", width=20)
        info_table.add_column("Значение", style="bold", min_width=15)

        info_table.add_row("Баланс", f"£{club.get('balance', 0):,.0f}")
        info_table.add_row("Трансферный бюджет", f"£{club.get('transfer_budget', 0):,.0f}")
        info_table.add_row("ФОТ (неделя)", f"£{club.get('wage_bill', 0):,.0f}")
        info_table.add_row("Состав", f"{club.get('squad_count', 0)} игроков")
        info_table.add_row("Ср. рейтинг", str(club.get('avg_rating', 0)))
        info_table.add_row("Мораль", f"{club.get('morale', 0)}%")

        from rich.panel import Panel

        self.console.print_panel(info_table, title=f"[bold]{team_name}[/]", border_style="cyan")

        # Следующий матч
        next_match = club.get("next_match")
        if next_match:
            fixture = create_match_fixture(
                home_team=next_match.get("home_team", ""),
                away_team=next_match.get("away_team", ""),
                matchday=next_match.get("matchday"),
                date=next_match.get("date"),
            )
            self.console.print()
            self.console.print(fixture)

        # Форма команды
        form = club.get("form", "")
        if form:
            self.console.print()
            self.console.print(f"  [bold]Форма:[/] ", end="")
            from ...utils.formatters import format_form
            self.console.print(format_form(form))

        # Опции
        self.console.print()
        self.console.print("[bold cyan]Управление клубом:[/]")
        self.console.print()
        for i, (key, label) in enumerate(self.options, 1):
            self.console.print(f"  [bold cyan]{i:2d}.[/] {label}")

        self.console.print()
        self.console.print_centered("[dim]Выберите опцию:[/]")

    def run(self) -> Optional[str]:
        """
        Запустить меню клуба.

        Returns:
            Название выбранной секции или 'back' для возврата
        """
        while True:
            try:
                self.display()
                choice = self.console.input()

                if not choice:
                    continue

                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.options):
                        key, _ = self.options[idx]
                        if key == "back":
                            return "back"
                        return key
                    else:
                        self.console.print_warning("Неверный номер опции.")
                        self.console.wait_for_key()
                except ValueError:
                    self.console.print_warning("Введите номер опции.")
                    self.console.wait_for_key()

            except KeyboardInterrupt:
                return "back"

    def show_squad(self, players=None) -> None:
        """Показать состав команды."""
        self.console.clear()
        self.console.print_header("👥 Состав команды")

        if players:
            table = create_player_table(players, title="Основной состав")
            self.console.print(table)
        else:
            # Демо данные
            demo_players = [
                {"name": "Иванов Алексей", "position": "GK", "age": 28, "rating": 78, "value": 5_000_000},
                {"name": "Петров Дмитрий", "position": "CB", "age": 25, "rating": 82, "value": 15_000_000},
                {"name": "Сидоров Сергей", "position": "CB", "age": 30, "rating": 76, "value": 4_000_000},
                {"name": "Козлов Андрей", "position": "LB", "age": 24, "rating": 79, "value": 10_000_000},
                {"name": "Новиков Павел", "position": "RB", "age": 26, "rating": 80, "value": 12_000_000},
                {"name": "Морозов Владимир", "position": "CDM", "age": 27, "rating": 81, "value": 14_000_000},
                {"name": "Волков Максим", "position": "CM", "age": 23, "rating": 77, "value": 8_000_000},
                {"name": "Соколов Никита", "position": "CAM", "age": 22, "rating": 83, "value": 20_000_000},
                {"name": "Лебедев Артём", "position": "LW", "age": 21, "rating": 80, "value": 16_000_000},
                {"name": "Кузнецов Илья", "position": "RW", "age": 24, "rating": 78, "value": 9_000_000},
                {"name": "Попов Даниил", "position": "ST", "age": 25, "rating": 85, "value": 25_000_000},
            ]
            table = create_player_table(demo_players, title="Основной состав")
            self.console.print(table)

        self.console.wait_for_key()

    def show_tactics(self) -> None:
        """Показать тактику."""
        self.console.clear()
        self.console.print_header("📋 Тактика")
        self.console.print_warning("Переход в меню тактики...")
        self.console.wait_for_key()

    def show_transfers(self) -> None:
        """Показать трансферы."""
        self.console.clear()
        self.console.print_header("💰 Трансферы")
        self.console.print_warning("Переход в меню трансферов...")
        self.console.wait_for_key()

    def show_finances(self) -> None:
        """Показать финансы."""
        self.console.clear()
        self.console.print_header("💎 Финансы")

        finance_data = {
            "balance": self.club_data.get("balance", 0),
            "transfer_budget": self.club_data.get("transfer_budget", 0),
            "wage_bill": self.club_data.get("wage_bill", 0),
            "wage_budget": 2_000_000,
            "income": {
                "Телевидение": 15_000_000,
                "Билеты": 3_000_000,
                "Спонсорство": 5_000_000,
                "Трансферы": 0,
            },
            "expenses": {
                "Зарплаты": 78_000_000,
                "Трансферы": 10_000_000,
                "Инфраструктура": 2_000_000,
                "Академия": 1_000_000,
            },
        }

        panel = create_financial_display(finance_data)
        self.console.print(panel)
        self.console.wait_for_key()

    def show_training(self) -> None:
        """Показать тренировки."""
        self.console.clear()
        self.console.print_header("🏋️ Тренировки")
        self.console.print_warning("Переход в меню тренировок...")
        self.console.wait_for_key()

    def show_youth(self) -> None:
        """Показать молодёжную академию."""
        self.console.clear()
        self.console.print_header("⭐ Молодёжная академия")
        self.console.print_warning("Переход в меню молодёжи...")
        self.console.wait_for_key()

    def show_calendar(self) -> None:
        """Показать календарь."""
        self.console.clear()
        self.console.print_header("📅 Календарь игр")
        self.console.print_warning("Переход в календарь...")
        self.console.wait_for_key()

    def show_news(self) -> None:
        """Показать новости."""
        self.console.clear()
        self.console.print_header("📰 Новости клуба")
        self.console.print_warning("Переход в раздел новостей...")
        self.console.wait_for_key()

    def show_settings(self) -> None:
        """Показать настройки клуба."""
        self.console.clear()
        self.console.print_header("⚙️ Настройки клуба")
        self.console.print_warning("Настройки клуба ещё не реализованы.")
        self.console.wait_for_key()
