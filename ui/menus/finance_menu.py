"""Меню финансов клуба."""

from typing import Any, Dict, Optional

from ..console import ConsoleUI
from ..widgets import create_financial_display


class FinanceMenu:
    """Меню финансов клуба."""

    def __init__(self, console: ConsoleUI, finance_data: Optional[Dict[str, Any]] = None):
        """
        Инициализация меню финансов.

        Args:
            console: Объект консоли
            finance_data: Финансовые данные
        """
        self.console = console
        self.finance_data = finance_data or self._default_finance_data()

    def _default_finance_data(self) -> Dict[str, Any]:
        """Финансовые данные по умолчанию."""
        return {
            "balance": 50_000_000,
            "transfer_budget": 20_000_000,
            "wage_budget": 2_000_000,
            "wage_bill": 1_500_000,
            "season_start_balance": 45_000_000,
            "income": {
                "Телевидение": 30_000_000,
                "Билеты": 8_000_000,
                "Спонсорство": 15_000_000,
                "Продажа merchandise": 3_000_000,
                "Трансферы (продажа)": 0,
            },
            "expenses": {
                "Зарплаты игроков": 78_000_000,
                "Зарплаты персонала": 5_000_000,
                "Трансферы (покупка)": 15_000_000,
                "Инфраструктура": 8_000_000,
                "Академия": 3_000_000,
                "Путешествия": 2_000_000,
                "Медицинское обслуживание": 1_500_000,
                "Прочее": 1_000_000,
            },
            "stadium_income": {
                "Билеты": 8_000_000,
                "VIP-ложи": 3_000_000,
                "Концессы": 2_000_000,
            },
            "projected_income": {
                "Телевидение": 35_000_000,
                "Билеты": 10_000_000,
                "Спонсорство": 18_000_000,
            },
        }

    def display(self) -> Optional[str]:
        """
        Отобразить меню финансов.

        Returns:
            Команда
        """
        self.console.clear()
        self.console.print_header("💎 Финансы клуба")

        balance = self.finance_data.get("balance", 0)
        transfer = self.finance_data.get("transfer_budget", 0)
        wage_bill = self.finance_data.get("wage_bill", 0)
        wage_budget = self.finance_data.get("wage_budget", 0)

        # Краткая сводка
        self.console.print()
        balance_color = "green" if balance > 0 else "red"
        self.console.print(f"  [bold]Баланс:[/] [{balance_color}]£{balance:,.0f}[/]")
        self.console.print(f"  [bold]Трансферный бюджет:[/] £{transfer:,.0f}")
        self.console.print(
            f"  [bold]ФОТ:[/] £{wage_bill:,.0f} / £{wage_budget:,.0f} "
            f"({wage_bill / wage_budget * 100:.1f}%)" if wage_budget > 0 else ""
        )

        # Опции
        self.console.print()
        self.console.print("[bold cyan]Разделы:[/]")
        self.console.print("  [bold cyan]1.[/] 📊 Сводка")
        self.console.print("  [bold cyan]2.[/] 📈 Доходы")
        self.console.print("  [bold cyan]3.[/] 📉 Расходы")
        self.console.print("  [bold cyan]4.[/] 💰 Бюджет")
        self.console.print("  [bold cyan]5.[/] 🏥 Финансовое здоровье")
        self.console.print("  [bold cyan]6.[/] 📅 Прогноз на сезон")
        self.console.print("  [bold cyan]7.[/] 💼 Зарплатная ведомость")
        self.console.print("  [bold cyan]8.[/] ◀️ Назад")

        choice = self.console.input("\n[bold cyan]Ваш выбор: [/]")

        if choice == "1":
            return "summary"
        elif choice == "2":
            return "income"
        elif choice == "3":
            return "expenses"
        elif choice == "4":
            return "budget"
        elif choice == "5":
            return "health"
        elif choice == "6":
            return "projection"
        elif choice == "7":
            return "wages"
        return "back"

    def show_summary(self) -> None:
        """Показать финансовую сводку."""
        self.console.clear()
        self.console.print_header("📊 Финансовая сводка")

        panel = create_financial_display(self.finance_data)
        self.console.print(panel)
        self.console.wait_for_key()

    def show_income(self) -> None:
        """Показать подробные доходы."""
        self.console.clear()
        self.console.print_header("📈 Доходы")

        from rich.table import Table

        table = Table(
            title="Источники дохода",
            show_header=True,
            header_style="bold green",
            show_lines=True,
            expand=True,
        )
        table.add_column("Источник", style="bold", min_width=25)
        table.add_column("Сумма", justify="right", min_width=15)
        table.add_column("%", justify="right", width=8)

        income = self.finance_data.get("income", {})
        total = sum(income.values())

        for source, amount in income.items():
            if amount > 0:
                pct = (amount / total * 100) if total > 0 else 0
                table.add_row(source, f"£{amount:,.0f}", f"{pct:.1f}%")

        table.add_row(
            "[bold]ИТОГО[/]",
            f"[bold green]£{total:,.0f}[/]",
            "[bold]100%[/]",
        )

        self.console.print(table)

        # Дополнительные доходы от стадиона
        stadium = self.finance_data.get("stadium_income", {})
        if stadium:
            self.console.print()
            self.console.print("[bold cyan]Доходы от стадиона:[/]")
            for source, amount in stadium.items():
                self.console.print(f"  • {source}: £{amount:,.0f}")

        self.console.wait_for_key()

    def show_expenses(self) -> None:
        """Показать подробные расходы."""
        self.console.clear()
        self.console.print_header("📉 Расходы")

        from rich.table import Table

        table = Table(
            title="Статьи расходов",
            show_header=True,
            header_style="bold red",
            show_lines=True,
            expand=True,
        )
        table.add_column("Статья", style="bold", min_width=25)
        table.add_column("Сумма", justify="right", min_width=15)
        table.add_column("%", justify="right", width=8)

        expenses = self.finance_data.get("expenses", {})
        total = sum(expenses.values())

        for source, amount in expenses.items():
            if amount > 0:
                pct = (amount / total * 100) if total > 0 else 0
                table.add_row(source, f"[red]£{amount:,.0f}[/]", f"{pct:.1f}%")

        table.add_row(
            "[bold]ИТОГО[/]",
            f"[bold red]£{total:,.0f}[/]",
            "[bold]100%[/]",
        )

        self.console.print(table)
        self.console.wait_for_key()

    def show_budget(self) -> None:
        """Показать бюджет."""
        self.console.clear()
        self.console.print_header("💰 Бюджет")

        transfer = self.finance_data.get("transfer_budget", 0)
        wage_budget = self.finance_data.get("wage_budget", 0)

        self.console.print(f"\n  [bold cyan]Трансферный бюджет:[/] £{transfer:,.0f}")
        self.console.print(f"  [bold cyan]Зарплатный бюджет (неделя):[/] £{wage_budget:,.0f}")

        # Распределение
        self.console.print("\n[bold]Распределение бюджета:[/]")

        # Примерное распределение
        allocations = [
            ("Основная команда", 60),
            ("Молодёжная академия", 15),
            ("Инфраструктура", 10),
            ("Скаутинг", 10),
            ("Резерв", 5),
        ]

        from rich.progress import Progress, BarColumn, TextColumn

        with Progress(
            TextColumn("[bold]{task.description}"),
            BarColumn(bar_width=40),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console.console,
        ) as progress:
            for label, pct in allocations:
                progress.add_task(label, total=100, completed=pct)

        self.console.wait_for_key()

    def show_health(self) -> None:
        """Показать финансовое здоровье."""
        self.console.clear()
        self.console.print_header("🏥 Финансовое здоровье")

        balance = self.finance_data.get("balance", 0)
        income = self.finance_data.get("income", {})
        expenses = self.finance_data.get("expenses", {})

        total_income = sum(income.values())
        total_expenses = sum(expenses.values())
        profit = total_income - total_expenses

        # Оценка здоровья
        if profit > 0 and balance > 0:
            health = "Отличное"
            color = "bold green"
            emoji = "💚"
        elif profit > 0:
            health = "Хорошее"
            color = "green"
            emoji = "💛"
        elif balance > 0:
            health = "Удовлетворительное"
            color = "yellow"
            emoji = "🧡"
        else:
            health = "Плохое"
            color = "bold red"
            emoji = "❤️"

        self.console.print(f"\n  {emoji} Финансовое здоровье: [{color}]{health}[/]")
        self.console.print(f"\n  [bold]Прибыль/убыток за сезон:[/]")
        profit_color = "green" if profit > 0 else "red"
        self.console.print(f"  [{profit_color}]£{profit:+,.0f}[/]")

        self.console.print(f"\n  [bold]Прогноз остатка на конец сезона:[/]")
        projected = balance + profit
        proj_color = "green" if projected > 0 else "red"
        self.console.print(f"  [{proj_color}]£{projected:,.0f}[/]")

        # Рекомендации
        self.console.print("\n[bold cyan]Рекомендации:[/]")
        if total_expenses > total_income:
            self.console.print("  ⚠️ Расходы превышают доходы. Рассмотрите продажу игроков.")
        if balance < 5_000_000:
            self.console.print("  ⚠️ Низкий баланс. Избегайте крупных трансферов.")

        self.console.wait_for_key()

    def show_projection(self) -> None:
        """Показать прогноз на сезон."""
        self.console.clear()
        self.console.print_header("📅 Прогноз на сезон")

        projected = self.finance_data.get("projected_income", {})

        self.console.print("\n[bold cyan]Прогнозируемые доходы на следующий сезон:[/]")
        total = 0
        for source, amount in projected.items():
            self.console.print(f"  • {source}: £{amount:,.0f}")
            total += amount

        self.console.print(f"\n  [bold]ИТОГО:[/] [green]£{total:,.0f}[/]")

        # Текущий сезон
        current_income = self.finance_data.get("income", {})
        current_total = sum(current_income.values())

        change = total - current_total
        change_color = "green" if change > 0 else "red"
        self.console.print(f"\n  [bold]Изменение:[/] [{change_color}]£{change:+,.0f}[/]")

        self.console.wait_for_key()

    def show_wages(self) -> None:
        """Показать зарплатную ведомость."""
        self.console.clear()
        self.console.print_header("💼 Зарплатная ведомость")

        wage_bill = self.finance_data.get("wage_bill", 0)
        wage_budget = self.finance_data.get("wage_budget", 0)

        self.console.print(f"\n  [bold]Общий ФОТ:[/] £{wage_bill:,.0f} / £{wage_budget:,.0f} (неделя)")
        self.console.print(f"  [bold]Годовой ФОТ:[/] £{wage_bill * 52:,.0f}")

        # Примерная разбивка
        self.console.print("\n[bold cyan]Структура зарплат:[/]")

        from rich.table import Table

        table = Table(show_header=True, header_style="bold cyan", show_lines=True)
        table.add_column("Категория", style="bold", min_width=25)
        table.add_column("Неделя", justify="right", min_width=12)
        table.add_column("Год", justify="right", min_width=12)

        wage_breakdown = [
            ("Основная команда", wage_bill * 0.85),
            ("Молодёжь", wage_bill * 0.08),
            ("Персонал", wage_bill * 0.07),
        ]

        for category, weekly in wage_breakdown:
            table.add_row(category, f"£{weekly:,.0f}", f"£{weekly * 52:,.0f}")

        table.add_row(
            "[bold]ИТОГО[/]",
            f"[bold]£{wage_bill:,.0f}[/]",
            f"[bold]£{wage_bill * 52:,.0f}[/]",
        )

        self.console.print(table)

        # Загрузка ФОТ
        usage = (wage_bill / wage_budget * 100) if wage_budget > 0 else 0
        usage_color = "green" if usage < 80 else ("yellow" if usage < 100 else "red")
        self.console.print(f"\n  [bold]Загрузка ФОТ:[/] [{usage_color}]{usage:.1f}%[/]")

        self.console.wait_for_key()
