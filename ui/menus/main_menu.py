"""Главное меню игры Football Manager."""

import sys
from typing import Optional

from ..console import ConsoleUI


# ASCII-арт заголовок игры
TITLE_ART = r"""
   ███████╗██╗   ██╗ ██████╗██╗  ██╗    ██╗   ██╗██╗
   ██╔════╝██║   ██║██╔════╝██║ ██╔╝    ██║   ██║██║
   █████╗  ██║   ██║██║     █████╔╝     ██║   ██║██║
   ██╔══╝  ╚██╗ ██╔╝██║     ██╔═██╗     ╚██╗ ██╔╝██║
   ███████╗ ╚████╔╝ ╚██████╗██║  ██╗     ╚████╔╝ ██║
   ╚══════╝  ╚═══╝   ╚═════╝╚═╝  ╚═╝      ╚═══╝  ╚═╝
   ██████╗  ██████╗ ███╗   ███╗██████╗  ██████╗ ███╗   ██╗
  ██╔════╝ ██╔═══██╗████╗ ████║██╔══██╗██╔═══██╗████╗  ██║
  ██║      ██║   ██║██╔████╔██║██║  ██║██║   ██║██╔██╗ ██║
  ██║      ██║   ██║██║╚██╔╝██║██║  ██║██║   ██║██║╚██╗██║
  ╚██████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝╚██████╔╝██║ ╚████║
   ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═══╝
"""


class MainMenu:
    """Главное меню игры."""

    def __init__(self, console: ConsoleUI):
        """
        Инициализация главного меню.

        Args:
            console: Объект консоли для вывода
        """
        self.console = console
        self.options = [
            "Новая игра",
            "Загрузить игру",
            "Настройки",
            "Об игре",
            "Выход",
        ]

    def display(self) -> None:
        """Отобразить главное меню."""
        self.console.clear()
        self.console.print_centered("[bold bright_cyan]⚽ FOOTBALL MANAGER 2026 ⚽[/]")
        self.console.print()

        # ASCII-арт заголовок
        self.console.print(f"[bold bright_cyan]{TITLE_ART}[/]")
        self.console.print()

        # Опции меню
        for i, option in enumerate(self.options, 1):
            self.console.print_centered(f"[bold cyan]{i}.[/] [white]{option}[/]")

        self.console.print()
        self.console.print_centered("[dim]Выберите опцию (1-5):[/]")

    def run(self) -> Optional[str]:
        """
        Запустить главное меню.

        Returns:
            Название выбранной опции или None для выхода
        """
        while True:
            try:
                self.display()
                choice = self.console.input()

                if choice == "1":
                    return "new_game"
                elif choice == "2":
                    return "load_game"
                elif choice == "3":
                    return "settings"
                elif choice == "4":
                    self._show_about()
                elif choice == "5":
                    if self.console.confirm("Вы уверены, что хотите выйти?"):
                        return "exit"
                else:
                    self.console.print_warning("Неверный выбор. Попробуйте снова.")
                    self.console.wait_for_key()

            except KeyboardInterrupt:
                self.console.print("\n[dim]Выход из игры...[/]")
                return "exit"

    def _show_about(self) -> None:
        """Показать информацию об игре."""
        self.console.clear()
        self.console.print_header("О игре", "Football Manager 2026")

        about_text = """
[bold]Football Manager 2026[/bold]

Симулятор менеджера футбольного клуба.
Управляйте командой, выигрывайте трофеи и станьте легендой!

[bold cyan]Возможности:[/]
• Управление составом и тактикой
• Трансферы и скаутинг
• Финансы и инфраструктура
• Обучение молодёжи
• Проведение матчей в реальном времени
• Новости и пресс-конференции
• Соревнования в лигах и кубках

[bold cyan]Управление:[/]
• Ввод цифр для выбора опций
• 'назад' - вернуться в предыдущее меню
• 'выход' - выйти из игры
• Ctrl+C - экстренный выход

[dim]Версия 1.0.0 | 2026[/]
"""
        self.console.print(about_text)
        self.console.wait_for_key()

    def _show_settings(self) -> None:
        """Показать настройки."""
        self.console.clear()
        self.console.print_header("Настройки")

        settings = [
            "Громкость звуков",
            "Скорость анимаций",
            "Авто-сохранение",
            "Язык интерфейса",
            "Тема оформления",
            "Уведомления",
            "Назад",
        ]

        for i, setting in enumerate(settings, 1):
            self.console.print(f"  [bold cyan]{i}.[/] {setting}")

        self.console.print()
        choice = self.console.input("[bold cyan]Выберите настройку: [/]")

        if choice == "7":
            return

        self.console.print_warning("Настройки ещё не реализованы.")
        self.console.wait_for_key()
