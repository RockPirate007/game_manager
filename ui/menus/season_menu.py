"""Меню сезона - таблица, календарь, симуляция."""

from typing import Any, Dict, List, Optional

from ..console import ConsoleUI
from ..widgets import (
    create_team_table,
    create_match_fixture,
    create_stats_display,
)


class SeasonMenu:
    """Меню сезона."""

    def __init__(self, console: ConsoleUI, season_data: Optional[Dict[str, Any]] = None):
        """
        Инициализация меню сезона.

        Args:
            console: Объект консоли
            season_data: Данные сезона
        """
        self.console = console
        self.season_data = season_data or self._default_season_data()

    def _default_season_data(self) -> Dict[str, Any]:
        """Данные сезона по умолчанию."""
        return {
            "season": "2025/2026",
            "league": "Премьер-лига",
            "current_matchday": 30,
            "total_matchdays": 38,
            "teams": [
                {"name": "Арсенал", "played": 30, "won": 22, "drawn": 5, "lost": 3, "goals_for": 68, "goals_against": 25, "points": 71, "form": "WWWWW"},
                {"name": "Манчестер Сити", "played": 30, "won": 21, "drawn": 6, "lost": 3, "goals_for": 72, "goals_against": 28, "points": 69, "form": "WDWWW"},
                {"name": "Ливерпуль", "played": 30, "won": 20, "drawn": 5, "lost": 5, "goals_for": 65, "goals_against": 30, "points": 65, "form": "LWWWW"},
                {"name": "Челси", "played": 30, "won": 18, "drawn": 7, "lost": 5, "goals_for": 58, "goals_against": 32, "points": 61, "form": "DWWWW"},
                {"name": "Тоттенхэм", "played": 30, "won": 17, "drawn": 6, "lost": 7, "goals_for": 55, "goals_against": 35, "points": 57, "form": "WDLWW"},
                {"name": "Манчестер Юнайтед", "played": 30, "won": 16, "drawn": 7, "lost": 7, "goals_for": 52, "goals_against": 38, "points": 55, "form": "DDWWW"},
                {"name": "Ньюкасл", "played": 30, "won": 15, "drawn": 8, "lost": 7, "goals_for": 50, "goals_against": 33, "points": 53, "form": "WDWDW"},
                {"name": "Брайтон", "played": 30, "won": 14, "drawn": 8, "lost": 8, "goals_for": 48, "goals_against": 35, "points": 50, "form": "WDWWL"},
            ],
            "fixtures": [
                {"matchday": 31, "date": "22 июня 2026", "home": "Арсенал", "away": "Манчестер Сити", "played": False},
                {"matchday": 32, "date": "29 июня 2026", "home": "Ливерпуль", "away": "Арсенал", "played": False},
                {"matchday": 33, "date": "6 июля 2026", "home": "Арсенал", "away": "Челси", "played": False},
            ],
            "season_stats": {
                "total_goals": 1250,
                "avg_goals_per_match": 2.7,
                "home_wins": 450,
                "draws": 200,
                "away_wins": 350,
                "total_attendance": 15000000,
            },
            "awards": {
                "top_scorer": {"name": "Холанд", "goals": 28, "club": "Манчестер Сити"},
                "top_assist": {"name": "Сака", "assists": 15, "club": "Арсенал"},
                "best_goalkeeper": {"name": "Куртуа", "club": "Челси"},
                "best_defender": {"name": "Салиба", "club": "Арсенал"},
                "best_midfielder": {"name": "Эдегор", "club": "Арсенал"},
                "player_of_the_season": {"name": "Эдегор", "club": "Арсенал"},
                "young_player": {"name": "Соколов", "club": "Наш клуб"},
                "best_manager": {"name": "Главный тренер", "club": "Наш клуб"},
            },
        }

    def display(self) -> Optional[str]:
        """
        Отобразить меню сезона.

        Returns:
            Команда
        """
        self.console.clear()
        self.console.print_header(
            f"📅 Сезон {self.season_data.get('season', '?')}",
            f"{self.season_data.get('league', '?')} | Тур {self.season_data.get('current_matchday', 0)}/{self.season_data.get('total_matchdays', 0)}"
        )

        # Опции
        self.console.print()
        self.console.print("[bold cyan]Разделы:[/]")
        self.console.print("  [bold cyan]1.[/] 🏆 Таблица лиги")
        self.console.print("  [bold cyan]2.[/] 📅 Календарь / Фикстуры")
        self.console.print("  [bold cyan]3.[/] ⚽ Симуляция тура")
        self.console.print("  [bold cyan]4.[/] 📊 Статистика сезона")
        self.console.print("  [bold cyan]5.[/] 🏅 Награды сезона")
        self.console.print("  [bold cyan]6.[/] ◀️ Назад")

        choice = self.console.input("\n[bold cyan]Ваш выбор: [/]")

        if choice == "1":
            return "table"
        elif choice == "2":
            return "fixtures"
        elif choice == "3":
            return "simulate"
        elif choice == "4":
            return "stats"
        elif choice == "5":
            return "awards"
        return "back"

    def show_table(self) -> None:
        """Показать таблицу лиги."""
        self.console.clear()
        self.console.print_header("🏆 Таблица лиги")

        teams = self.season_data.get("teams", [])
        table = create_team_table(
            teams,
            title=f"{self.season_data.get('league', '?')} - Сезон {self.season_data.get('season', '?')}",
            highlight_team=self.season_data.get("user_team"),
        )
        self.console.print(table)

        self.console.wait_for_key()

    def show_fixtures(self) -> None:
        """Показать календарь игр."""
        self.console.clear()
        self.console.print_header("📅 Календарь игр")

        fixtures = self.season_data.get("fixtures", [])
        current = self.season_data.get("current_matchday", 0)

        # Ближайшие матчи
        self.console.print(f"\n[bold cyan]Ближайшие матчи:[/]")
        for fix in fixtures:
            if not fix.get("played", False):
                status = "[bold green] предстоит[/]" if fix.get("matchday", 0) > current else "[yellow]текущий тур[/]"
                fixture = create_match_fixture(
                    home_team=fix.get("home", ""),
                    away_team=fix.get("away", ""),
                    matchday=fix.get("matchday"),
                    date=fix.get("date"),
                )
                self.console.print(fixture)

        # Прошедшие матчи (пример)
        self.console.print(f"\n[bold cyan]Последние результаты:[/]")
        demo_results = [
            {"home": "Арсенал", "away": "Эвертон", "home_score": 3, "away_score": 1, "matchday": 29},
            {"home": "Брентфорд", "away": "Арсенал", "home_score": 0, "away_score": 2, "matchday": 28},
            {"home": "Арсенал", "away": "Вулверхэмптон", "home_score": 2, "away_score": 0, "matchday": 27},
        ]

        for result in demo_results:
            fixture = create_match_fixture(
                home_team=result["home"],
                away_team=result["away"],
                home_score=result["home_score"],
                away_score=result["away_score"],
                matchday=result["matchday"],
            )
            self.console.print(fixture)

        self.console.wait_for_key()

    def simulate_matchday(self) -> None:
        """Симулировать тур."""
        self.console.clear()
        self.console.print_header("⚽ Симуляция тура")

        current = self.season_data.get("current_matchday", 0)
        total = self.season_data.get("total_matchdays", 0)

        if current >= total:
            self.console.print("\n  [dim]Сезон завершён.[/]")
            self.console.wait_for_key()
            return

        self.console.print(f"\n  [bold]Текущий тур:[/] {current}/{total}")
        self.console.print(f"  [bold]Следующий тур:[/] {current + 1}")

        if self.console.confirm(f"Симулировать тур {current + 1}?"):
            self.console.print("\n[bold cyan]Симуляция...[/]")

            # Имитация симуляции
            import time
            import random

            teams = self.season_data.get("teams", [])
            fixtures = self.season_data.get("fixtures", [])

            for fix in fixtures:
                if fix.get("matchday") == current + 1 and not fix.get("played"):
                    home = fix.get("home", "")
                    away = fix.get("away", "")

                    # Генерируем счет
                    home_score = random.randint(0, 4)
                    away_score = random.randint(0, 3)

                    fix["home_score"] = home_score
                    fix["away_score"] = away_score
                    fix["played"] = True

                    # Обновляем таблицу
                    home_team = next((t for t in teams if t["name"] == home), None)
                    away_team = next((t for t in teams if t["name"] == away), None)

                    if home_team and away_team:
                        home_team["played"] += 1
                        away_team["played"] += 1
                        home_team["goals_for"] += home_score
                        home_team["goals_against"] += away_score
                        away_team["goals_for"] += away_score
                        away_team["goals_against"] += home_score

                        if home_score > away_score:
                            home_team["won"] += 1
                            home_team["points"] += 3
                            away_team["lost"] += 1
                        elif home_score < away_score:
                            away_team["won"] += 1
                            away_team["points"] += 3
                            home_team["lost"] += 1
                        else:
                            home_team["drawn"] += 1
                            away_team["drawn"] += 1
                            home_team["points"] += 1
                            away_team["points"] += 1

                    fixture = create_match_fixture(
                        home_team=home,
                        away_team=away,
                        home_score=home_score,
                        away_score=away_score,
                    )
                    self.console.print(fixture)

                    time.sleep(0.5)

            self.season_data["current_matchday"] = current + 1
            self.console.print_success(f"Тур {current + 1} симулирован!")
        else:
            self.console.print("Симуляция отменена.")

        self.console.wait_for_key()

    def show_season_stats(self) -> None:
        """Показать статистику сезона."""
        self.console.clear()
        self.console.print_header("📊 Статистика сезона")

        stats = self.season_data.get("season_stats", {})

        from rich.table import Table

        table = Table(
            title="Статистика сезона",
            show_header=True,
            header_style="bold cyan",
            show_lines=True,
            expand=True,
        )
        table.add_column("Параметр", style="bold", min_width=25)
        table.add_column("Значение", justify="right", min_width=15)

        table.add_row("Всего голов", str(stats.get("total_goals", 0)))
        table.add_row("Голов за матч", f"{stats.get('avg_goals_per_match', 0):.2f}")
        table.add_row("Побед хозяев", str(stats.get("home_wins", 0)))
        table.add_row("Ничьих", str(stats.get("draws", 0)))
        table.add_row("Побед гостей", str(stats.get("away_wins", 0)))
        table.add_row("Общая посещаемость", f"{stats.get('total_attendance', 0):,}")

        self.console.print(table)

        # Лучшие бомбардиры (пример)
        self.console.print()
        self.console.print("[bold cyan]Лучшие бомбардиры:[/]")
        top_scorers = [
            {"name": "Холанд", "club": "Манчестер Сити", "goals": 28},
            {"name": "Саллах", "club": "Ливерпуль", "goals": 22},
            {"name": "Сон", "club": "Тоттенхэм", "goals": 20},
            {"name": "Попов", "club": "Наш клуб", "goals": 18},
        ]

        for i, player in enumerate(top_scorers, 1):
            self.console.print(f"  {i}. {player['name']} ({player['club']}) - {player['goals']} голов")

        self.console.wait_for_key()

    def show_awards(self) -> None:
        """Показать награды сезона."""
        self.console.clear()
        self.console.print_header("🏅 Награды сезона")

        awards = self.season_data.get("awards", {})

        from rich.table import Table

        table = Table(
            title="Награды сезона",
            show_header=True,
            header_style="bold yellow",
            show_lines=True,
            expand=True,
        )
        table.add_column("Награда", style="bold", min_width=25)
        table.add_column("Победитель", style="cyan", min_width=20)
        table.add_column("Дополнительно", style="dim", min_width=15)

        award_names = {
            "top_scorer": "Лучший бомбардир",
            "top_assist": "Лучший ассистент",
            "best_goalkeeper": "Лучший вратарь",
            "best_defender": "Лучший защитник",
            "best_midfielder": "Лучший полузащитник",
            "player_of_the_season": "Игрок сезона",
            "young_player": "Лучший молодой игрок",
            "best_manager": "Лучший тренер",
        }

        for key, name in award_names.items():
            winner = awards.get(key, {})
            if winner:
                extra = ""
                if "goals" in winner:
                    extra = f"{winner['goals']} голов"
                elif "assists" in winner:
                    extra = f"{winner['assists']} передач"
                table.add_row(
                    name,
                    f"{winner.get('name', '?')} ({winner.get('club', '?')})",
                    extra,
                )

        self.console.print(table)
        self.console.wait_for_key()
