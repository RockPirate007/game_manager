"""Меню трансферов - рынок, предложения, шортлист."""

from typing import Any, Dict, List, Optional

from ..console import ConsoleUI
from ..widgets import create_player_table


class TransfersMenu:
    """Меню трансферов."""

    def __init__(self, console: ConsoleUI, transfer_data: Optional[Dict[str, Any]] = None):
        """
        Инициализация меню трансферов.

        Args:
            console: Объект консоли
            transfer_data: Данные трансферов
        """
        self.console = console
        self.transfer_data = transfer_data or self._default_transfer_data()

    def _default_transfer_data(self) -> Dict[str, Any]:
        """Данные трансферов по умолчанию."""
        return {
            "transfer_budget": 20_000_000,
            "wage_budget": 200_000,
            "shortlist": [],
            "incoming_bids": [],
            "outgoing_bids": [],
            "free_agents": [
                {"name": "Свободный агент 1", "position": "ST", "age": 28, "rating": 75, "value": 0, "wage": 50000},
                {"name": "Свободный агент 2", "position": "CM", "age": 30, "rating": 72, "value": 0, "wage": 40000},
            ],
            "loan_market": [
                {"name": "Игрок аренды 1", "position": "CB", "age": 22, "rating": 70, "value": 3_000_000, "loan_fee": 500000},
                {"name": "Игрок аренды 2", "position": "LW", "age": 20, "rating": 68, "value": 2_000_000, "loan_fee": 300000},
            ],
            "transfer_history": [],
        }

    def display(self) -> Optional[str]:
        """
        Отобразить меню трансферов.

        Returns:
            Команда
        """
        self.console.clear()
        self.console.print_header("💰 Трансферный рынок")

        budget = self.transfer_data.get("transfer_budget", 0)
        wage = self.transfer_data.get("wage_budget", 0)
        self.console.print(f"\n  [bold]Трансферный бюджет:[/] £{budget:,.0f}")
        self.console.print(f"  [bold]Зарплатный бюджет:[/] £{wage:,.0f}/нед.")

        # Опции
        self.console.print()
        self.console.print("[bold cyan]Разделы:[/]")
        self.console.print("  [bold cyan]1.[/] 🔍 Поиск игроков")
        self.console.print("  [bold cyan]2.[/] 📋 Шортлист")
        self.console.print("  [bold cyan]3.[/] 🆓 Свободные агенты")
        self.console.print("  [bold cyan]4.[/] 🤝 Рынок аренд")
        self.console.print("  [bold cyan]5.[/] 📥 входящие предложения")
        self.console.print("  [bold cyan]6.[/] 📤 Исходящие предложения")
        self.console.print("  [bold cyan]7.[/] 📜 История трансферов")
        self.console.print("  [bold cyan]8.[/] ⚪ Предложить контракт")
        self.console.print("  [bold cyan]9.[/] ◀️ Назад")

        choice = self.console.input("\n[bold cyan]Ваш выбор: [/]")

        if choice == "1":
            return "search"
        elif choice == "2":
            return "shortlist"
        elif choice == "3":
            return "free_agents"
        elif choice == "4":
            return "loan_market"
        elif choice == "5":
            return "incoming_bids"
        elif choice == "6":
            return "outgoing_bids"
        elif choice == "7":
            return "history"
        elif choice == "8":
            return "offer_contract"
        return "back"

    def search_players(self) -> None:
        """Поиск игроков на рынке."""
        self.console.clear()
        self.console.print_header("🔍 Поиск игроков")

        # Фильтры
        self.console.print("\n[bold cyan]Фильтры поиска:[/]")
        self.console.print("  1. По позиции")
        self.console.print("  2. По рейтингу")
        self.console.print("  3. По цене")
        self.console.print("  4. По возрасту")
        self.console.print("  5. По национальности")
        self.console.print("  6. Показать всех")

        filter_choice = self.console.input("\n[bold cyan]Выберите фильтр: [/]")

        # Демо данные для поиска
        demo_players = [
            {"name": "Ищемый игрок 1", "position": "ST", "age": 25, "rating": 80, "value": 15_000_000, "club": "Другой клуб"},
            {"name": "Ищемый игрок 2", "position": "CM", "age": 23, "rating": 76, "value": 8_000_000, "club": "Ещё клуб"},
            {"name": "Ищемый игрок 3", "position": "CB", "age": 27, "rating": 82, "value": 20_000_000, "club": "Третий клуб"},
        ]

        self.console.print()
        table = create_player_table(demo_players, title="Результаты поиска")
        self.console.print(table)

        # Выбор игрока
        self.console.print()
        choice = self.console.input("[bold cyan]Введите номер игрока для действий (0 для выхода): [/]")
        if choice != "0":
            self.console.print("  1. Сделать предложение")
            self.console.print("  2. Добавить в шортлист")
            self.console.print("  3. Наблюдать")
            action = self.console.input("[bold cyan]Действие: [/]")
            if action == "1":
                self.make_bid(demo_players[0] if choice == "1" else None)
            elif action == "2":
                self.add_to_shortlist(demo_players[0] if choice == "1" else None)

        self.console.wait_for_key()

    def view_shortlist(self) -> None:
        """Просмотреть шортлист."""
        self.console.clear()
        self.console.print_header("📋 Шортлист")

        shortlist = self.transfer_data.get("shortlist", [])
        if not shortlist:
            self.console.print("\n  [dim]Шортлист пуст. Добавьте игроков из поиска.[/]")
        else:
            table = create_player_table(shortlist, title="Шортлист")
            self.console.print(table)

        self.console.wait_for_key()

    def view_free_agents(self) -> None:
        """Просмотреть свободных агентов."""
        self.console.clear()
        self.console.print_header("🆓 Свободные агенты")

        agents = self.transfer_data.get("free_agents", [])
        if not agents:
            self.console.print("\n  [dim]Нет доступных свободных агентов.[/]")
        else:
            table = create_player_table(agents, title="Свободные агенты", show_value=False)
            self.console.print(table)

            self.console.print()
            choice = self.console.input("[bold cyan]Введите номер игрока для действий (0 для выхода): [/]")
            if choice != "0" and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(agents):
                    self.console.print(f"  1. Предложить контракт")
                    self.console.print(f"  2. Наблюдать")
                    action = self.console.input("[bold cyan]Действие: [/]")
                    if action == "1":
                        self.offer_contract(agents[idx])

        self.console.wait_for_key()

    def view_loan_market(self) -> None:
        """Просмотреть рынок аренд."""
        self.console.clear()
        self.console.print_header("🤝 Рынок аренд")

        loans = self.transfer_data.get("loan_market", [])
        if not loans:
            self.console.print("\n  [dim]Нет доступных игроков для аренды.[/]")
        else:
            table = create_player_table(loans, title="Доступные для аренды")
            self.console.print(table)

            self.console.print()
            choice = self.console.input("[bold cyan]Введите номер игрока для действий (0 для выхода): [/]")
            if choice != "0" and choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(loans):
                    self.console.print(f"  1. Предложить аренду")
                    self.console.print(f"  2. Наблюдать")
                    action = self.console.input("[bold cyan]Действие: [/]")
                    if action == "1":
                        self.offer_loan(loans[idx])

        self.console.wait_for_key()

    def view_incoming_bids(self) -> None:
        """Просмотреть входящие предложения."""
        self.console.clear()
        self.console.print_header("📥 Входящие предложения")

        bids = self.transfer_data.get("incoming_bids", [])
        if not bids:
            self.console.print("\n  [dim]Нет входящих предложений.[/]")
        else:
            for i, bid in enumerate(bids, 1):
                player = bid.get("player", {})
                from_team = bid.get("from_team", "")
                amount = bid.get("amount", 0)
                self.console.print(f"  {i}. {player.get('name', '?')} ← {from_team}: £{amount:,.0f}")

        self.console.wait_for_key()

    def view_outgoing_bids(self) -> None:
        """Просмотреть исходящие предложения."""
        self.console.clear()
        self.console.print_header("📤 Исходящие предложения")

        bids = self.transfer_data.get("outgoing_bids", [])
        if not bids:
            self.console.print("\n  [dim]Нет исходящих предложений.[/]")
        else:
            for i, bid in enumerate(bids, 1):
                player = bid.get("player", {})
                to_team = bid.get("to_team", "")
                amount = bid.get("amount", 0)
                status = bid.get("status", "в ожидании")
                self.console.print(
                    f"  {i}. {player.get('name', '?')} → {to_team}: £{amount:,.0f} [{status}]"
                )

        self.console.wait_for_key()

    def view_history(self) -> None:
        """Просмотреть историю трансферов."""
        self.console.clear()
        self.console.print_header("📜 История трансферов")

        history = self.transfer_data.get("transfer_history", [])
        if not history:
            self.console.print("\n  [dim]История трансферов пуста.[/]")
        else:
            for i, transfer in enumerate(history, 1):
                player = transfer.get("player", {})
                direction = transfer.get("direction", "")
                club = transfer.get("club", "")
                amount = transfer.get("amount", 0)
                date = transfer.get("date", "")
                icon = "📥" if direction == "in" else "📤"
                self.console.print(
                    f"  {icon} {date} | {player.get('name', '?')} | {club} | £{amount:,.0f}"
                )

        self.console.wait_for_key()

    def make_bid(self, player: Optional[Dict] = None) -> None:
        """Сделать предложение за игрока."""
        self.console.clear()
        self.console.print_header("💰 Предложение за игрока")

        if player:
            self.console.print(f"\n  Игрок: [bold]{player.get('name', '?')}[/]")
            self.console.print(f"  Текущая цена: £{player.get('value', 0):,.0f}")
            self.console.print(f"  Клуб: {player.get('club', '?')}")

            amount_str = self.console.input("\n[bold cyan]Введите сумму предложения (£): [/]")
            try:
                amount = float(amount_str.replace(",", "").replace("£", ""))
                if amount <= 0:
                    self.console.print_warning("Сумма должна быть положительной.")
                elif amount > self.transfer_data.get("transfer_budget", 0):
                    self.console.print_warning("Недостаточно бюджета.")
                else:
                    if self.console.confirm(f"Сделать предложение £{amount:,.0f} за {player.get('name', '?')}?"):
                        self.console.print_success("Предложение отправлено!")
            except ValueError:
                self.console.print_warning("Некорректная сумма.")

        self.console.wait_for_key()

    def add_to_shortlist(self, player: Optional[Dict] = None) -> None:
        """Добавить игрока в шортлист."""
        if player:
            shortlist = self.transfer_data.setdefault("shortlist", [])
            if player not in shortlist:
                shortlist.append(player)
                self.console.print_success(f"{player.get('name', '?')} добавлен в шортлист!")
            else:
                self.console.print_warning("Игрок уже в шортлисте.")
        self.console.wait_for_key()

    def offer_contract(self, player: Optional[Dict] = None) -> None:
        """Предложить контракт игроку."""
        self.console.clear()
        self.console.print_header("📝 Предложение контракта")

        if player:
            self.console.print(f"\n  Игрок: [bold]{player.get('name', '?')}[/]")
            self.console.print(f"  Возраст: {player.get('age', 0)}")
            self.console.print(f"  Позиция: {player.get('position', '?')}")
            self.console.print(f"  Рейтинг: {player.get('rating', 0)}")

            wage_str = self.console.input("\n[bold cyan]Предлагаемая зарплата (£/нед.): [/]")
            years_str = self.console.input("[bold cyan]Срок контракта (лет): [/]")

            try:
                wage = float(wage_str.replace(",", "").replace("£", ""))
                years = int(years_str)

                if wage <= 0 or years <= 0:
                    self.console.print_warning("Значения должны быть положительными.")
                elif wage > self.transfer_data.get("wage_budget", 0):
                    self.console.print_warning("Превышен зарплатный бюджет.")
                else:
                    self.console.print_success(
                        f"Предложение отправлено: £{wage:,.0f}/нед. на {years} лет"
                    )
            except ValueError:
                self.console.print_warning("Некорректный ввод.")

        self.console.wait_for_key()

    def offer_loan(self, player: Optional[Dict] = None) -> None:
        """Предложить аренду игрока."""
        self.console.clear()
        self.console.print_header("🤝 Предложение аренды")

        if player:
            self.console.print(f"\n  Игрок: [bold]{player.get('name', '?')}[/]")
            fee = player.get("loan_fee", 0)
            self.console.print(f"  Арендная плата: £{fee:,.0f}")

            if self.console.confirm(f"Предложить аренду {player.get('name', '?')}?"):
                self.console.print_success("Предложение аренды отправлено!")

        self.console.wait_for_key()
