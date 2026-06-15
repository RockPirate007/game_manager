"""Меню новостей и прессы."""

from typing import Any, Dict, List, Optional

from ..console import ConsoleUI
from ..widgets import create_news_card


class NewsMenu:
    """Меню новостей и прессы."""

    def __init__(self, console: ConsoleUI, news_data: Optional[Dict[str, Any]] = None):
        """
        Инициализация меню новостей.

        Args:
            console: Объект консоли
            news_data: Данные новостей
        """
        self.console = console
        self.news_data = news_data or self._default_news_data()

    def _default_news_data(self) -> Dict[str, Any]:
        """Данные новостей по умолчанию."""
        return {
            "articles": [
                {
                    "id": 1,
                    "title": "Трансферное окно: главные слухи",
                    "content": (
                        "Множество клубов ищут усиление перед новым сезоном. "
                        "Наши скауты отследили несколько интересных вариантов."
                    ),
                    "category": "transfer",
                    "date": "15 июня 2026",
                    "source": "Спортивные новости",
                    "importance": "high",
                    "read": False,
                },
                {
                    "id": 2,
                    "title": "Травма ключевого игрока",
                    "content": (
                        "Наш основной нападающий получил травму на тренировке. "
                        "Ожидаемый срок восстановления - 3 недели."
                    ),
                    "category": "injury",
                    "date": "14 июня 2026",
                    "source": "Пресс-служба клуба",
                    "importance": "high",
                    "read": False,
                },
                {
                    "id": 3,
                    "title": "Победа в товарищеском матче",
                    "content": (
                        "Команда одержала уверенную победу 3:0 в последнем "
                        "товарищеском матче перед началом сезона."
                    ),
                    "category": "match",
                    "date": "13 июня 2026",
                    "source": "Спортивные новости",
                    "importance": "normal",
                    "read": True,
                },
                {
                    "id": 4,
                    "title": "Новый спонсор клуба",
                    "content": (
                        "Клуб заключил спонсорское соглашение с крупной "
                        "компанией. Детали контракта не раскрываются."
                    ),
                    "category": "finance",
                    "date": "12 июня 2026",
                    "source": "Пресс-служба клуба",
                    "importance": "normal",
                    "read": True,
                },
                {
                    "id": 5,
                    "title": "Пресс-конференция тренера",
                    "content": (
                        "Главный тренер провёл пресс-конференцию, "
                        "в которой рассказал о планах на новый сезон."
                    ),
                    "category": "press_conf",
                    "date": "11 июня 2026",
                    "source": "Пресс-служба клуба",
                    "importance": "normal",
                    "read": False,
                },
            ],
            "categories": {
                "all": "Все новости",
                "transfer": "Трансферы",
                "match": "Матчи",
                "injury": "Травмы",
                "finance": "Финансы",
                "press_conf": "Пресс-конференции",
                "award": "Награды",
                "general": "Общее",
            },
            "awards": [
                {"name": "Игрок месяца", "winner": "Попов Даниил", "month": "Май 2026"},
                {"name": "Гол месяца", "winner": "Соколов Никита", "month": "Май 2026"},
                {"name": "Тренер месяца", "winner": "Главный тренер", "month": "Май 2026"},
            ],
        }

    def display(self) -> Optional[str]:
        """
        Отобразить меню новостей.

        Returns:
            Команда
        """
        self.console.clear()
        self.console.print_header("📰 Новости и пресса")

        articles = self.news_data.get("articles", [])
        unread = sum(1 for a in articles if not a.get("read", False))

        self.console.print(f"\n  [bold]Всего новостей:[/] {len(articles)}")
        self.console.print(f"  [bold]Непрочитанных:[/] [cyan]{unread}[/]")

        # Опции
        self.console.print()
        self.console.print("[bold cyan]Разделы:[/]")
        self.console.print("  [bold cyan]1.[/] 📰 Лента новостей")
        self.console.print("  [bold cyan]2.[/] 📁 По категориям")
        self.console.print("  [bold cyan]3.[/] 🎤 Пресс-конференции")
        self.console.print("  [bold cyan]4.[/] 🏆 Награды")
        self.console.print("  [bold cyan]5.[/] 🔍 Поиск")
        self.console.print("  [bold cyan]6.[/] ◀️ Назад")

        choice = self.console.input("\n[bold cyan]Ваш выбор: [/]")

        if choice == "1":
            return "feed"
        elif choice == "2":
            return "categories"
        elif choice == "3":
            return "press_conf"
        elif choice == "4":
            return "awards"
        elif choice == "5":
            return "search"
        return "back"

    def show_feed(self, category: Optional[str] = None) -> None:
        """Показать ленту новостей."""
        self.console.clear()
        title = "📰 Лента новостей"
        if category and category != "all":
            title += f" [{category}]"
        self.console.print_header(title)

        articles = self.news_data.get("articles", [])

        if category and category != "all":
            articles = [a for a in articles if a.get("category") == category]

        if not articles:
            self.console.print("\n  [dim]Нет новостей в этой категории.[/]")
            self.console.wait_for_key()
            return

        for i, article in enumerate(articles, 1):
            read_marker = "" if article.get("read", False) else " [bold yellow]●[/]"
            panel = create_news_card(article)
            self.console.print(panel)

            # Отметить как прочитанную
            article["read"] = True

        self.console.wait_for_key()

    def show_categories(self) -> None:
        """Показать новости по категориям."""
        self.console.clear()
        self.console.print_header("📁 Категории новостей")

        categories = self.news_data.get("categories", {})
        articles = self.news_data.get("articles", [])

        for key, name in categories.items():
            count = len([a for a in articles if a.get("category") == key]) if key != "all" else len(articles)
            self.console.print(f"  [bold cyan]{name}[/] ({count})")

        self.console.print()
        choice = self.console.input("[bold cyan]Выберите категорию: [/]")

        # Находим ключ по названию
        for key, name in categories.items():
            if name.lower() == choice.lower() or key.lower() == choice.lower():
                self.show_feed(category=key)
                return

        if choice.lower() == "все" or choice == "0":
            self.show_feed(category="all")
        else:
            self.console.print_warning("Категория не найдена.")
            self.console.wait_for_key()

    def show_press_conferences(self) -> None:
        """Показать пресс-конференции."""
        self.console.clear()
        self.console.print_header("🎤 Пресс-конференции")

        articles = self.news_data.get("articles", [])
        press_articles = [a for a in articles if a.get("category") == "press_conf"]

        if not press_articles:
            self.console.print("\n  [dim]Нет пресс-конференций.[/]")
        else:
            for article in press_articles:
                panel = create_news_card(article)
                self.console.print(panel)

        # Провести пресс-конференцию
        self.console.print()
        self.console.print("[bold cyan]Провести пресс-конференцию:[/]")
        self.console.print("  1. О трансферах")
        self.console.print("  2. О составе на матч")
        self.console.print("  3. О травмах")
        self.console.print("  4. О планах на сезон")
        self.console.print("  5. Свободная тема")
        self.console.print("  0. Назад")

        choice = self.console.input("\n[bold cyan]Выберите тему: [/]")

        if choice != "0":
            topics = {
                "1": "трансферы",
                "2": "состав",
                "3": "травмы",
                "4": "планы",
                "5": "свободная тема",
            }
            topic = topics.get(choice, "общая")
            self.console.print_success(f"Пресс-конференция на тему '{topic}' проведена!")

        self.console.wait_for_key()

    def show_awards(self) -> None:
        """Показать награды клуба."""
        self.console.clear()
        self.console.print_header("🏆 Награды клуба")

        awards = self.news_data.get("awards", [])

        if not awards:
            self.console.print("\n  [dim]Нет наград.[/]")
        else:
            from rich.table import Table

            table = Table(
                title="Награды",
                show_header=True,
                header_style="bold yellow",
                show_lines=True,
                expand=True,
            )
            table.add_column("Награда", style="bold", min_width=25)
            table.add_column("Победитель", style="cyan", min_width=20)
            table.add_column("Период", style="dim", min_width=15)

            for award in awards:
                table.add_row(
                    award.get("name", "?"),
                    award.get("winner", "?"),
                    award.get("month", "?"),
                )

            self.console.print(table)

        self.console.wait_for_key()

    def search_news(self) -> None:
        """Поиск по новостям."""
        self.console.clear()
        self.console.print_header("🔍 Поиск новостей")

        query = self.console.input("[bold cyan]Введите поисковый запрос: [/]")

        if not query:
            self.console.print_warning("Запрос не может быть пустым.")
            self.console.wait_for_key()
            return

        articles = self.news_data.get("articles", [])
        results = [
            a
            for a in articles
            if query.lower() in a.get("title", "").lower()
            or query.lower() in a.get("content", "").lower()
        ]

        if not results:
            self.console.print(f"\n  [dim]Ничего не найдено по запросу '{query}'.[/]")
        else:
            self.console.print(f"\n[bold]Найдено {len(results)} результатов:[/]")
            for article in results:
                panel = create_news_card(article)
                self.console.print(panel)

        self.console.wait_for_key()
