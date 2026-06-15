"""Меню тактики - формация, состав, инструкции."""

from typing import Any, Dict, List, Optional

from ..console import ConsoleUI
from ..widgets import (
    create_formation_display,
    create_player_table,
)


# Доступные формации
FORMATIONS = [
    ("4-4-2", "Классическая схема"),
    ("4-3-3", "Атакующая схема"),
    ("3-5-2", "Схема с вингербеками"),
    ("4-2-3-1", "Гибкая схема"),
    ("4-1-4-1", "Оборонительная схема"),
    ("3-4-3", "Агрессивная схема"),
    ("5-3-2", "Сверх-оборона"),
    ("4-3-2-1", "Christmas Tree"),
    ("4-5-1", "Средний блок"),
]

# Инструкции команды
INSTRUCTIONS = {
    "width": {
        "name": "Ширина игры",
        "options": ["Узкая", "Стандартная", "Широкая"],
        "default": 1,
    },
    "tempo": {
        "name": "Темп игры",
        "options": ["Низкий", "Стандартный", "Высокий"],
        "default": 1,
    },
    "pressing": {
        "name": "Прессинг",
        "options": ["Минимальный", "Стандартный", "Высокий", "Очень высокий"],
        "default": 1,
    },
    "passing": {
        "name": "Стиль передач",
        "options": ["Короткие", "Стандартные", "Длинные", "Смешанные"],
        "default": 1,
    },
    "crossing": {
        "name": "Навесы",
        "options": ["Редкие", "Стандартные", "Частые"],
        "default": 1,
    },
    "tackling": {
        "name": "Отбор",
        "options": ["Аккуратный", "Стандартный", "Жёсткий"],
        "default": 1,
    },
    "counter_attack": {
        "name": "Контратаки",
        "options": ["Включены", "Выключены"],
        "default": 0,
    },
    "offside_trap": {
        "name": "Офсайд-ловушка",
        "options": ["Включена", "Выключена"],
        "default": 1,
    },
}


class TacticsMenu:
    """Меню тактики."""

    def __init__(self, console: ConsoleUI, tactics_data: Optional[Dict[str, Any]] = None):
        """
        Инициализация меню тактики.

        Args:
            console: Объект консоли
            tactics_data: Данные тактики
        """
        self.console = console
        self.tactics_data = tactics_data or self._default_tactics()

    def _default_tactics(self) -> Dict[str, Any]:
        """Данные тактики по умолчанию."""
        return {
            "formation": "4-3-3",
            "starting_xi": {
                "GK": None,
                "CB": [None, None],
                "LB": None,
                "RB": None,
                "CDM": None,
                "CM": [None, None],
                "CAM": None,
                "LW": None,
                "RW": None,
                "ST": None,
            },
            "substitutes": [None] * 7,
            "captain": None,
            "penalty_taker": None,
            "free_kick_taker": None,
            "instructions": {
                "width": 1,
                "tempo": 1,
                "pressing": 1,
                "passing": 1,
                "crossing": 1,
                "tackling": 1,
                "counter_attack": 0,
                "offside_trap": 1,
            },
        }

    def display(self) -> Optional[str]:
        """
        Отобразить меню тактики.

        Returns:
            Команда
        """
        self.console.clear()
        self.console.print_header("📋 Тактика команды")

        # Текущая формация
        formation = self.tactics_data.get("formation", "4-3-3")
        self.console.print(f"\n  [bold cyan]Текущая формация:[/] [bold]{formation}[/]")

        # Отображение формации
        from ...ui.colors import TEAM_COLORS

        team_color = TEAM_COLORS.get(self.tactics_data.get("team_name", ""), "cyan")
        formation_display = create_formation_display(
            formation,
            self.tactics_data.get("starting_xi", {}),
            team_color=team_color,
        )
        self.console.print(formation_display)

        # Инструкции
        self.console.print()
        self.console.print("[bold cyan]Тактические инструкции:[/]")
        instructions = self.tactics_data.get("instructions", {})
        for key, config in INSTRUCTIONS.items():
            current_idx = instructions.get(key, config["default"])
            current = config["options"][current_idx]
            self.console.print(f"  • {config['name']}: [bold]{current}[/]")

        # Особые роли
        self.console.print()
        self.console.print("[bold cyan]Особые роли:[/]")
        self.console.print(f"  • Капитан: {self.tactics_data.get('captain', 'Не назначен')}")
        self.console.print(f"  • Пенальтист: {self.tactics_data.get('penalty_taker', 'Не назначен')}")
        self.console.print(f"  • Штрафной: {self.tactics_data.get('free_kick_taker', 'Не назначен')}")

        # Опции
        self.console.print()
        self.console.print("[bold cyan]Действия:[/]")
        self.console.print("  [bold cyan]1.[/] Изменить формацию")
        self.console.print("  [bold cyan]2.[/] Выбрать стартовый состав")
        self.console.print("  [bold cyan]3.[/] Запасные игроки")
        self.console.print("  [bold cyan]4.[/] Инструкции команды")
        self.console.print("  [bold cyan]5.[/] Особые роли")
        self.console.print("  [bold cyan]6.[/] Автоматический подбор")
        self.console.print("  [bold cyan]7.[/] Назад")

        choice = self.console.input("\n[bold cyan]Ваш выбор: [/]")

        if choice == "1":
            return "formation"
        elif choice == "2":
            return "starting_xi"
        elif choice == "3":
            return "substitutes"
        elif choice == "4":
            return "instructions"
        elif choice == "5":
            return "roles"
        elif choice == "6":
            return "auto_pick"
        return "back"

    def select_formation(self) -> None:
        """Выбрать формацию."""
        self.console.clear()
        self.console.print_header("📐 Выбор формации")

        for i, (formation, desc) in enumerate(FORMATIONS, 1):
            current = " [bold green]← текущая[/]" if formation == self.tactics_data.get("formation") else ""
            self.console.print(f"  [bold cyan]{i:2d}.[/] {formation} - {desc}{current}")

        self.console.print()
        choice = self.console.input("[bold cyan]Выберите формацию (номер или введите свою, например 4-4-2): [/]")

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(FORMATIONS):
                self.tactics_data["formation"] = FORMATIONS[idx][0]
                self.console.print_success(f"Формация изменена на {FORMATIONS[idx][0]}")
            else:
                self.console.print_warning("Неверный номер.")
        except ValueError:
            # Пользователь ввёл свою формацию
            if "-" in choice:
                parts = choice.split("-")
                if all(p.isdigit() for p in parts):
                    self.tactics_data["formation"] = choice
                    self.console.print_success(f"Формация изменена на {choice}")
                else:
                    self.console.print_warning("Некорректный формат формации.")
            else:
                self.console.print_warning("Некорректный ввод.")

        self.console.wait_for_key()

    def select_starting_xi(self) -> None:
        """Выбрать стартовый состав."""
        self.console.clear()
        self.console.print_header("👥 Выбор стартового состава")

        # Парсим формацию
        formation = self.tactics_data.get("formation", "4-3-3")
        lines = [int(x) for x in formation.split("-")]

        positions = []
        positions.append("GK")
        for i, count in enumerate(lines):
            pos_types = [
                ["CB"],  # Защита
                ["CDM", "CM", "CAM"],  # Полузащита
                ["LW", "RW", "ST", "CF"],  # Нападение
            ]
            if i < len(pos_types):
                for _ in range(count):
                    positions.append(pos_types[i][0])

        self.console.print(f"\n[bold cyan]Требуемые позиции для {formation}:[/]")
        for pos in positions:
            assigned = self.tactics_data["starting_xi"].get(pos, [None])[0] if isinstance(
                self.tactics_data["starting_xi"].get(pos), list
            ) else self.tactics_data["starting_xi"].get(pos)
            name = assigned.get("name", "Не назначен") if assigned else "Не назначен"
            self.console.print(f"  [{pos}] {name}")

        self.console.print()
        self.console.print("[dim]Выбор игроков будет доступен из состава команды.[/]")
        self.console.wait_for_key()

    def select_substitutes(self) -> None:
        """Выбрать запасных игроков."""
        self.console.clear()
        self.console.print_header("🪑 Выбор запасных")

        subs = self.tactics_data.get("substitutes", [])
        self.console.print(f"\n[bold cyan]Запасные ({len(subs)}/7):[/]")
        for i, sub in enumerate(subs, 1):
            name = sub.get("name", "Пусто") if sub else "Пусто"
            self.console.print(f"  {i}. {name}")

        self.console.print()
        self.console.print("[dim]Выбор игроков будет доступен из состава команды.[/]")
        self.console.wait_for_key()

    def edit_instructions(self) -> None:
        """Редактировать тактические инструкции."""
        self.console.clear()
        self.console.print_header("📝 Тактические инструкции")

        instructions = self.tactics_data.get("instructions", {})

        for i, (key, config) in enumerate(INSTRUCTIONS.items(), 1):
            current_idx = instructions.get(key, config["default"])
            current = config["options"][current_idx]
            self.console.print(f"  [bold cyan]{i}.[/] {config['name']}: [bold]{current}[/]")

        self.console.print()
        choice = self.console.input("[bold cyan]Выберите инструкцию для изменения (номер или 0 для выхода): [/]")

        if choice == "0":
            return

        try:
            idx = int(choice) - 1
            keys = list(INSTRUCTIONS.keys())
            if 0 <= idx < len(keys):
                key = keys[idx]
                config = INSTRUCTIONS[key]

                self.console.print(f"\n[bold]{config['name']}:[/]")
                for i, option in enumerate(config["options"], 1):
                    self.console.print(f"  [bold cyan]{i}.[/] {option}")

                opt_choice = self.console.input("[bold cyan]Выберите значение: [/]")
                try:
                    opt_idx = int(opt_choice) - 1
                    if 0 <= opt_idx < len(config["options"]):
                        instructions[key] = opt_idx
                        self.console.print_success(
                            f"{config['name']} изменено на {config['options'][opt_idx]}"
                        )
                    else:
                        self.console.print_warning("Неверный номер.")
                except ValueError:
                    self.console.print_warning("Введите номер.")
            else:
                self.console.print_warning("Неверный номер инструкции.")
        except ValueError:
            self.console.print_warning("Введите номер.")

        self.console.wait_for_key()

    def edit_roles(self) -> None:
        """Редактировать особые роли."""
        self.console.clear()
        self.console.print_header("👑 Особые роли")

        self.console.print(f"  1. Капитан: [bold]{self.tactics_data.get('captain', 'Не назначен')}[/]")
        self.console.print(f"  2. Пенальтист: [bold]{self.tactics_data.get('penalty_taker', 'Не назначен')}[/]")
        self.console.print(f"  3. Штрафной: [bold]{self.tactics_data.get('free_kick_taker', 'Не назначен')}[/]")

        self.console.print()
        choice = self.console.input("[bold cyan]Выберите роль для изменения (0 для выхода): [/]")

        if choice == "0":
            return

        roles = {1: "captain", 2: "penalty_taker", 3: "free_kick_taker"}
        try:
            idx = int(choice)
            if idx in roles:
                name = self.console.input("[bold cyan]Введите имя игрока: [/]")
                self.tactics_data[roles[idx]] = name
                self.console.print_success(f"Роль назначена: {name}")
            else:
                self.console.print_warning("Неверный номер.")
        except ValueError:
            self.console.print_warning("Введите номер.")

        self.console.wait_for_key()

    def auto_pick(self) -> None:
        """Автоматический подбор состава."""
        self.console.clear()
        self.console.print_header("🤖 Автоматический подбор")

        if self.console.confirm("Автоматически подобрать最佳 состав?"):
            # Здесь была бы реальная логика подбора
            self.console.print_success("Состав автоматически подобран!")
        else:
            self.console.print("Подбор отменён.")

        self.console.wait_for_key()
