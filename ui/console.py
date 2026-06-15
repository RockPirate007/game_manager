"""Класс консоли для вывода информации в терминал."""

import os
import sys
from typing import Any, Dict, List, Optional, Union

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .colors import DEFAULT_THEME


class ConsoleUI:
    """
    Обертка над rich.console.Console для统一ного интерфейса.

    Предоставляет методы для вывода:
    - Обычного текста
    - Таблиц
    - Панелей
    - Уведомлений
    - Ошибок и успешных сообщений
    - Заголовков
    """

    def __init__(self, theme: Optional[Dict[str, str]] = None):
        """
        Инициализация консоли.

        Args:
            theme: Пользовательская тема (по умолчанию DEFAULT_THEME)
        """
        self.theme_dict = theme or DEFAULT_THEME

        # Создаем Rich тему
        rich_theme = Theme(
            {
                "primary": self.theme_dict.get("primary", "cyan"),
                "secondary": self.theme_dict.get("secondary", "magenta"),
                "success": self.theme_dict.get("success", "green"),
                "warning": self.theme_dict.get("warning", "yellow"),
                "error": self.theme_dict.get("error", "red"),
                "info": self.theme_dict.get("info", "blue"),
                "muted": self.theme_dict.get("muted", "dim"),
                "accent": self.theme_dict.get("accent", "bright_yellow"),
            }
        )

        self.console = Console(theme=rich_theme)

    def print(
        self,
        *objects: Any,
        style: Optional[str] = None,
        end: str = "\n",
        highlight: bool = False,
        **kwargs,
    ) -> None:
        """
        Вывести текст в консоль.

        Args:
            *objects: Объекты для вывода
            style: Стиль текста
            end: Символ окончания строки
            highlight: Подсвечивать синтаксис
        """
        self.console.print(*objects, style=style, end=end, highlight=highlight, **kwargs)

    def input(self, prompt: str = "", **kwargs) -> str:
        """
        Запросить ввод у пользователя.

        Args:
            prompt: Приглашение для ввода

        Returns:
            Введённая строка
        """
        if prompt:
            self.print(prompt, end="", style="bold cyan")
        try:
            return input(**kwargs)
        except (EOFError, KeyboardInterrupt):
            self.print("\n", end="")
            return ""

    def clear(self) -> None:
        """Очистить консоль."""
        self.console.clear()

    def print_header(
        self,
        title: str,
        subtitle: str = "",
        style: str = "bold bright_cyan",
    ) -> None:
        """
        Вывести заголовок с рамкой.

        Args:
            title: Заголовок
            subtitle: Подзаголовок
            style: Стиль заголовка
        """
        width = self.console.width
        border = "═" * (width - 2)

        self.print(f"[dim]╔{border}╗[/]")
        if subtitle:
            self.print(f"[dim]║[/] [{style}]{title:^{width-4}}[/] [dim]║[/]")
            self.print(f"[dim]║[/] [dim]{subtitle:^{width-4}}[/] [dim]║[/]")
        else:
            self.print(f"[dim]║[/] [{style}]{title:^{width-4}}[/] [dim]║[/]")
        self.print(f"[dim]╚{border}╝[/]")

    def print_table(
        self,
        title: Optional[str] = None,
        columns: Optional[List[Dict[str, Any]]] = None,
        rows: Optional[List[List[str]]] = None,
        show_header: bool = True,
        header_style: str = "bold cyan",
        show_lines: bool = True,
        expand: bool = True,
        **kwargs,
    ) -> Table:
        """
        Вывести таблицу.

        Args:
            title: Заголовок таблицы
            columns: Список колонок [{"name": str, "style": str, ...}]
            rows: Список строк
            show_header: Показывать заголовки
            header_style: Стиль заголовков
            show_lines: Показывать разделители строк
            expand: Растягивать на всю ширину

        Returns:
            Объект Table для дальнейшей модификации
        """
        table = Table(
            title=title,
            show_header=show_header,
            header_style=header_style,
            show_lines=show_lines,
            expand=expand,
            **kwargs,
        )

        if columns:
            for col in columns:
                table.add_column(
                    col.get("name", ""),
                    style=col.get("style"),
                    width=col.get("width"),
                    justify=col.get("justify", "left"),
                    no_wrap=col.get("no_wrap", False),
                )

        if rows:
            for row in rows:
                table.add_row(*row)

        self.console.print(table)
        return table

    def print_panel(
        self,
        content: Any,
        title: str = "",
        subtitle: str = "",
        border_style: str = "cyan",
        expand: bool = True,
        padding: tuple = (0, 1),
        **kwargs,
    ) -> Panel:
        """
        Вывести панель с содержимым.

        Args:
            content: Содержимое панели
            title: Заголовок панели
            subtitle: Подзаголовок
            border_style: Стиль рамки
            expand: Растягивать на всю ширину
            padding: Отступы (вертикальный, горизонтальный)

        Returns:
            Объект Panel
        """
        panel = Panel(
            content,
            title=title,
            subtitle=subtitle,
            border_style=border_style,
            expand=expand,
            padding=padding,
            **kwargs,
        )
        self.console.print(panel)
        return panel

    def print_notification(
        self,
        message: str,
        level: str = "info",
        title: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Вывести уведомление.

        Args:
            message: Текст уведомления
            level: Уровень (info, success, warning, error)
            title: Заголовок уведомления
        """
        icons = {
            "info": "ℹ️ ",
            "success": "✅ ",
            "warning": "⚠️ ",
            "error": "❌ ",
        }

        styles = {
            "info": "info",
            "success": "success",
            "warning": "warning",
            "error": "error",
        }

        icon = icons.get(level, "")
        style = styles.get(level, "white")
        title = title or {
            "info": "Информация",
            "success": "Успешно",
            "warning": "Внимание",
            "error": "Ошибка",
        }.get(level, "Уведомление")

        self.print_panel(
            f"{icon}{message}",
            title=f"[bold {style}]{title}[/]",
            border_style=style,
            **kwargs,
        )

    def print_error(self, message: str, title: str = "Ошибка") -> None:
        """
        Вывести сообщение об ошибке.

        Args:
            message: Текст ошибки
            title: Заголовок
        """
        self.print_notification(message, level="error", title=title)

    def print_success(self, message: str, title: str = "Успешно") -> None:
        """
        Вывести успешное сообщение.

        Args:
            message: Текст сообщения
            title: Заголовок
        """
        self.print_notification(message, level="success", title=title)

    def print_warning(self, message: str, title: str = "Внимание") -> None:
        """
        Вывести предупреждение.

        Args:
            message: Текст предупреждения
            title: Заголовок
        """
        self.print_notification(message, level="warning", title=title)

    def print_divider(self, style: str = "dim", char: str = "─") -> None:
        """
        Вывести разделитель.

        Args:
            style: Стиль разделителя
            char: Символ разделителя
        """
        width = self.console.width
        self.print(f"[{style}]{char * width}[/]")

    def print_spacer(self, lines: int = 1) -> None:
        """
        Вывести пустые строки.

        Args:
            lines: Количество пустых строк
        """
        self.print("\n" * (lines - 1))

    def print_centered(
        self, text: str, style: str = "", width: Optional[int] = None
    ) -> None:
        """
        Вывести текст по центру.

        Args:
            text: Текст для центрирования
            style: Стиль текста
        """
        w = width or self.console.width
        if style:
            text = f"[{style}]{text}[/]"
        self.print(text, justify="center", width=w)

    def get_width(self) -> int:
        """Получить ширину консоли."""
        return self.console.width

    def get_height(self) -> int:
        """Получить высоту консоли."""
        return self.console.height

    def wait_for_key(self, message: str = "Нажмите Enter для продолжения...") -> None:
        """
        Ожидать нажатия клавиши.

        Args:
            message: Сообщение для пользователя
        """
        self.print(f"\n[bold cyan]{message}[/]", end="")
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            self.print("\n")

    def confirm(self, message: str, default: bool = True) -> bool:
        """
        Запросить подтверждение.

        Args:
            message: Вопрос
            default: Значение по умолчанию

        Returns:
            True если подтверждено
        """
        suffix = " [Д/н]: " if default else " [д/Н]: "
        self.print(f"[bold]{message}[/]{suffix}", end="")
        try:
            response = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            return default

        if not response:
            return default

        return response in ("да", "д", "y", "yes", "1", "true")

    def select_option(
        self,
        options: List[str],
        prompt: str = "Выберите опцию",
        allow_cancel: bool = True,
    ) -> Optional[int]:
        """
        Показать список опций и выбрать одну.

        Args:
            options: Список опций
            prompt: Приглашение
            allow_cancel: Разрешить отмену (0)

        Returns:
            Номер выбранной опции или None при отмене
        """
        table = Table(show_header=False, show_lines=False, expand=True)
        table.add_column("№", style="bold cyan", width=4)
        table.add_column("Опция", style="white")

        for i, option in enumerate(options, 1):
            table.add_row(str(i), option)

        if allow_cancel:
            table.add_row("0", "[dim]Выход / Отмена[/]")

        self.print_panel(table, title=f"[bold]{prompt}[/]")

        while True:
            try:
                self.print("[bold cyan]Ваш выбор: [/]", end="")
                response = input().strip()

                if response == "0" and allow_cancel:
                    return None

                try:
                    choice = int(response)
                    if 1 <= choice <= len(options):
                        return choice - 1
                    self.print_warning(
                        f"Введите число от 1 до {len(options)}"
                    )
                except ValueError:
                    self.print_warning("Введите номер опции")
            except (EOFError, KeyboardInterrupt):
                return None

    def __repr__(self) -> str:
        return f"ConsoleUI(width={self.get_width()}, height={self.get_height()})"
