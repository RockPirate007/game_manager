"""Меню матча - до матча, во время матча, полувремя, после матча."""

import time
from typing import Any, Dict, List, Optional

from ..console import ConsoleUI
from ..widgets import (
    create_match_fixture,
    create_player_table,
    create_stats_display,
    create_event_card,
    create_comparison_bar,
)


class MatchMenu:
    """Меню матча с различными фазами."""

    def __init__(self, console: ConsoleUI, match_data: Optional[Dict[str, Any]] = None):
        """
        Инициализация меню матча.

        Args:
            console: Объект консоли
            match_data: Данные матча
        """
        self.console = console
        self.match_data = match_data or self._default_match_data()

    def _default_match_data(self) -> Dict[str, Any]:
        """Данные матча по умолчанию."""
        return {
            "home_team": "Арсенал",
            "away_team": "Челси",
            "home_score": 0,
            "away_score": 0,
            "minute": 0,
            "venue": "Эмирейтс",
            "attendance": 60000,
            "weather": "Облачно, 18°C",
            "home_lineup": {
                "GK": [{"name": "Райс", "rating": 78}],
                "CB": [
                    {"name": "Салиба", "rating": 85},
                    {"name": "Габриэл", "rating": 83},
                ],
                "LB": [{"name": "Зинченко", "rating": 80}],
                "RB": [{"name": "Томиясу", "rating": 79}],
                "CDM": [{"name": "Партей", "rating": 82}],
                "CM": [
                    {"name": "Эдегор", "rating": 88},
                    {"name": "Одегаард", "rating": 84},
                ],
                "LW": [{"name": "Мартинелли", "rating": 82}],
                "RW": [{"name": "Сака", "rating": 86}],
                "ST": [{"name": "Хаверц", "rating": 81}],
            },
            "away_lineup": {
                "GK": [{"name": "Куртуа", "rating": 87}],
                "CB": [
                    {"name": "Сильва", "rating": 84},
                    {"name": "Кулебали", "rating": 82},
                ],
                "LB": [{"name": "Кукурелья", "rating": 78}],
                "RB": [{"name": "Джеймс", "rating": 83}],
                "CDM": [{"name": "Канте", "rating": 81}],
                "CM": [
                    {"name": "Энцо", "rating": 80},
                    {"name": "Кайседо", "rating": 79},
                ],
                "LW": [{"name": "Стерлинг", "rating": 80}],
                "RW": [{"name": "Палинья", "rating": 77}],
                "ST": [{"name": "Холанд", "rating": 91}],
            },
            "stats": {
                "possession": [55, 45],
                "shots": [12, 8],
                "shots_on_target": [5, 3],
                "corners": [6, 4],
                "fouls": [8, 10],
                "yellow_cards": [1, 2],
                "red_cards": [0, 0],
                "offsides": [2, 1],
                "passes": [450, 380],
                "pass_accuracy": [87.5, 84.2],
            },
            "events": [],
        }

    def display_prematch(self) -> Optional[str]:
        """
        Отобразить информацию перед матчем.

        Returns:
            Команда ('start', 'tactics', 'back')
        """
        self.console.clear()

        match = self.match_data
        home = match.get("home_team", "")
        away = match.get("away_team", "")

        # Заголовок матча
        self.console.print_header(
            f"⚽ Матч дня",
            f"{match.get('venue', '?')} | Зрители: {match.get('attendance', 0):,}"
        )

        # Панель матча
        fixture = create_match_fixture(
            home_team=home,
            away_team=away,
            matchday=match.get("matchday"),
            date=match.get("date"),
            venue=match.get("venue"),
        )
        self.console.print(fixture)

        # Сравнение команд
        self.console.print()
        self.console.print("[bold cyan]Сравнение команд:[/]")

        home_stats = match.get("home_stats", {})
        away_stats = match.get("away_stats", {})

        comparisons = [
            ("Атака", home_stats.get("attack", 75), away_stats.get("attack", 75)),
            ("Защита", home_stats.get("defense", 75), away_stats.get("defense", 75)),
            ("Полузащита", home_stats.get("midfield", 75), away_stats.get("midfield", 75)),
            ("Физика", home_stats.get("physical", 75), away_stats.get("physical", 75)),
            ("Тактика", home_stats.get("tactics", 75), away_stats.get("tactics", 75)),
        ]

        for label, home_val, away_val in comparisons:
            bar = create_comparison_bar(home_val, away_val, label, width=15)
            self.console.print(bar)

        # Составы
        self.console.print()
        self.console.print("[bold cyan]Составы:[/]")

        home_lineup = match.get("home_lineup", {})
        away_lineup = match.get("away_lineup", {})

        from rich.columns import Columns

        home_table = create_player_table(
            self._flatten_lineup(home_lineup),
            title=f"📝 {home}",
            show_value=False,
        )
        away_table = create_player_table(
            self._flatten_lineup(away_lineup),
            title=f"📝 {away}",
            show_value=False,
        )

        self.console.print(Columns([home_table, away_table], expand=True))

        # Опции
        self.console.print()
        self.console.print("[bold cyan]Действия:[/]")
        self.console.print("  [bold cyan]1.[/] Начать матч")
        self.console.print("  [bold cyan]2.[/] Тактика")
        self.console.print("  [bold cyan]3.[/] Назад")

        choice = self.console.input("\n[bold cyan]Ваш выбор: [/]")

        if choice == "1":
            return "start"
        elif choice == "2":
            return "tactics"
        else:
            return "back"

    def display_live(self, minute: int = 0, events: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Отобразить live ход матча.

        Args:
            minute: Текущая минута
            events: Список событий

        Returns:
            Команда
        """
        self.console.clear()

        match = self.match_data
        home = match.get("home_team", "")
        away = match.get("away_team", "")
        home_score = match.get("home_score", 0)
        away_score = match.get("away_score", 0)

        # Заголовок с比分
        self.console.print_header(
            f"⚽ {home} {home_score} : {away_score} {away}",
            f"Минута: {minute}' | {match.get('venue', '?')}"
        )

        # Последние события
        if events:
            self.console.print()
            self.console.print("[bold cyan]События:[/]")
            for event in events[-5:]:  # Последние 5 событий
                panel = create_event_card(
                    event_type=event.get("type", ""),
                    minute=event.get("minute", 0),
                    description=event.get("description", ""),
                    team=event.get("team", ""),
                )
                self.console.print(panel)

        # Мини-статистика
        self.console.print()
        stats = match.get("stats", {})
        self.console.print(
            f"  [dim]Владение:[/] [cyan]{stats.get('possession', [50, 50])[0]}%[/] - "
            f"[magenta]{stats.get('possession', [50, 50])[1]}%[/]"
        )
        self.console.print(
            f"  [dim]Удары:[/] [cyan]{stats.get('shots', [0, 0])[0]}[/] - "
            f"[magenta]{stats.get('shots', [0, 0])[1]}[/]"
        )
        self.console.print(
            f"  [dim]Угловые:[/] [cyan]{stats.get('corners', [0, 0])[0]}[/] - "
            f"[magenta]{stats.get('corners', [0, 0])[1]}[/]"
        )

        # Опции во время матча
        self.console.print()
        self.console.print("[bold cyan]Управление:[/]")
        self.console.print("  [bold cyan]1.[/] Следующая минута")
        self.console.print("  [bold cyan]2.[/] Замена")
        self.console.print("  [bold cyan]3.[/] Тактика")
        self.console.print("  [bold cyan]4.[/] Пауза")

        choice = self.console.input("\n[bold cyan]Ваш выбор: [/]")

        if choice == "1":
            return "next_minute"
        elif choice == "2":
            return "substitution"
        elif choice == "3":
            return "tactics"
        elif choice == "4":
            return "pause"
        return "continue"

    def display_halftime(self, stats: Optional[Dict] = None) -> Optional[str]:
        """
        Отобразить информацию по перерыву.

        Args:
            stats: Статистика первого тайма

        Returns:
            Команда
        """
        self.console.clear()

        match = self.match_data
        home = match.get("home_team", "")
        away = match.get("away_team", "")
        home_score = match.get("home_score", 0)
        away_score = match.get("away_score", 0)

        self.console.print_header(
            f"⏸️ ПОЛУВРЕМЯ",
            f"{home} {home_score} : {away_score} {away}"
        )

        # Статистика тайма
        if stats is None:
            stats = match.get("stats", {})

        stats_table = create_stats_display(
            stats,
            title="Статистика первого тайма",
            home_name=home,
            away_name=away,
        )
        self.console.print(stats_table)

        # Аналитика
        self.console.print()
        self.console.print("[bold cyan]Аналитика:[/]")

        possession = stats.get("possession", [50, 50])
        if possession[0] > 55:
            self.console.print(f"  • [cyan]{home}[/]主导了 владение мячом")
        elif possession[1] > 55:
            self.console.print(f"  • [magenta]{away}[/]主导了 владение мячом")
        else:
            self.console.print("  • Владение мячом примерно равное")

        shots = stats.get("shots", [0, 0])
        if shots[0] > shots[1] + 3:
            self.console.print(f"  • [cyan]{home}[/] создаёт больше моментов")
        elif shots[1] > shots[0] + 3:
            self.console.print(f"  • [magenta]{away}[/] создаёт больше моментов")

        # Опции
        self.console.print()
        self.console.print("[bold cyan]Действия:[/]")
        self.console.print("  [bold cyan]1.[/] Начать второй тайм")
        self.console.print("  [bold cyan]2.[/] Тактика / Замены")
        self.console.print("  [bold cyan]3.[/] Статистика")

        choice = self.console.input("\n[bold cyan]Ваш выбор: [/]")

        if choice == "1":
            return "second_half"
        elif choice == "2":
            return "tactics"
        elif choice == "3":
            return "stats"
        return "continue"

    def display_fulltime(self, events: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Отобразить информацию после матча.

        Args:
            events: Все события матча

        Returns:
            Команда
        """
        self.console.clear()

        match = self.match_data
        home = match.get("home_team", "")
        away = match.get("away_team", "")
        home_score = match.get("home_score", 0)
        away_score = match.get("away_score", 0)

        self.console.print_header(
            f"🏁 МАТЧ ОКОНЧЕН",
            f"{home} {home_score} : {away_score} {away}"
        )

        # Итоговая панель
        fixture = create_match_fixture(
            home_team=home,
            away_team=away,
            home_score=home_score,
            away_score=away_score,
        )
        self.console.print(fixture)

        # Статистика матча
        stats = match.get("stats", {})
        stats_table = create_stats_display(
            stats,
            title="Итоговая статистика",
            home_name=home,
            away_name=away,
        )
        self.console.print(stats_table)

        # События матча
        if events:
            self.console.print()
            self.console.print("[bold cyan]Ключевые моменты:[/]")
            for event in events:
                if event.get("type") in ("goal", "red_card", "penalty"):
                    panel = create_event_card(
                        event_type=event.get("type", ""),
                        minute=event.get("minute", 0),
                        description=event.get("description", ""),
                        team=event.get("team", ""),
                    )
                    self.console.print(panel)

        # Лучший игрок
        self.console.print()
        self.console.print("[bold yellow]⭐ Лучший игрок матча:[/]")
        # TODO: Реализовать выбор лучшего игрока

        # Опции
        self.console.print()
        self.console.print("[bold cyan]Действия:[/]")
        self.console.print("  [bold cyan]1.[/] Пресс-конференция")
        self.console.print("  [bold cyan]2.[/] Оценки игроков")
        self.console.print("  [bold cyan]3.[/] Продолжить")

        choice = self.console.input("\n[bold cyan]Ваш выбор: [/]")

        if choice == "1":
            return "press_conference"
        elif choice == "2":
            return "player_ratings"
        else:
            return "continue"

    def _flatten_lineup(self, lineup: Dict) -> List[Dict]:
        """Развернуть состав из позиций в плоский список."""
        players = []
        for position, pos_players in lineup.items():
            for p in pos_players:
                p["position"] = position
                players.append(p)
        return players

    def simulate_match_event(self) -> Dict[str, Any]:
        """
        Симулировать событие матча.

        Returns:
            Словарь с событием
        """
        import random

        event_types = [
            ("goal", 10),
            ("shot", 25),
            ("save", 20),
            ("foul", 15),
            ("corner", 12),
            ("offside", 8),
            ("nothing", 10),
        ]

        total = sum(w for _, w in event_types)
        rand = random.randint(1, total)
        cumulative = 0

        for event_type, weight in event_types:
            cumulative += weight
            if rand <= cumulative:
                if event_type == "goal":
                    team = random.choice(["home", "away"])
                    return {
                        "type": "goal",
                        "minute": self.match_data.get("minute", 0),
                        "team": team,
                        "description": f"Гол! Счёт меняется!",
                        "team_scored": team,
                    }
                elif event_type == "foul":
                    card = random.choice(["yellow", "none", "none"])
                    return {
                        "type": "yellow_card" if card == "yellow" else "foul",
                        "minute": self.match_data.get("minute", 0),
                        "team": random.choice(["home", "away"]),
                        "description": "Нарушение правил" if card == "none" else "Жёлтая карточка",
                    }
                else:
                    return {
                        "type": event_type,
                        "minute": self.match_data.get("minute", 0),
                        "team": random.choice(["home", "away"]),
                        "description": event_type,
                    }

        return {"type": "nothing", "minute": self.match_data.get("minute", 0), "team": "", "description": ""}
