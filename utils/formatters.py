"""Модуль форматирования данных для вывода в терминал."""

from typing import Any, Dict, List, Optional, Tuple

from rich.text import Text

from ..ui.colors import (
    FORM_COLORS,
    POSITION_COLORS,
    RATING_COLORS,
    TEAM_COLORS,
    get_color,
)


def format_currency(amount: float, short: bool = True) -> str:
    """
    Форматировать сумму денег.

    Args:
        amount: Сумма в фунтах
        short: Использовать сокращенный формат

    Returns:
        Отформатированная строка (например, "£1.5M", "£500K", "£50")

    Examples:
        >>> format_currency(1500000)
        '£1.5M'
        >>> format_currency(500000)
        '£500K'
        >>> format_currency(50)
        '£50'
    """
    if amount < 0:
        return f"-{format_currency(-amount, short)}"

    if not short:
        return f"£{amount:,.0f}"

    if amount >= 1_000_000:
        value = amount / 1_000_000
        if value == int(value):
            return f"£{int(value)}M"
        return f"£{value:.1f}M"
    elif amount >= 1_000:
        value = amount / 1_000
        if value == int(value):
            return f"£{int(value)}K"
        return f"£{value:.0f}K"
    else:
        return f"£{int(amount)}"


def format_rating(rating: int, colored: bool = True) -> str:
    """
    Форматировать рейтинг игрока с цветом.

    Args:
        rating: Рейтинг (1-99)
        colored: Применять ли цвет

    Returns:
        Отформатированная строка с цветом

    Examples:
        >>> format_rating(85)
        '[bold green]85[/]'
        >>> format_rating(65, colored=False)
        '65'
    """
    rating = max(1, min(99, rating))
    if not colored:
        return str(rating)

    # Определяем цвет по рейтингу
    if rating >= 85:
        color = "bold bright_green"
    elif rating >= 75:
        color = "green"
    elif rating >= 65:
        color = "yellow"
    elif rating >= 50:
        color = "orange3"
    else:
        color = "red"

    return f"[{color}]{rating}[/]"


def format_form(form: str, colored: bool = True) -> str:
    """
    Форматировать серию результатов (форму команды).

    Args:
        form: Строка результатов (W=победа, D=ничья, L=поражение)
        colored: Применять ли цвет

    Returns:
        Отформатированная строка с цветами

    Examples:
        >>> format_form("WWDLW")
        '[green]W[/][green]W[/][yellow]D[/][red]L[/][green]W[/]'
    """
    if not colored:
        return form

    result = []
    for char in form.upper():
        if char in FORM_COLORS:
            color = FORM_COLORS[char]
            result.append(f"[{color}]{char}[/]")
        else:
            result.append(char)
    return "".join(result)


def format_percent(value: float, decimals: int = 1) -> str:
    """
    Форматировать процент.

    Args:
        value: Значение (0.0 - 1.0 или 0 - 100)
        decimals: Количество знаков после запятой

    Returns:
        Отформатированная строка (например, "65.5%")
    """
    # Если значение больше 1, считаем что это уже проценты
    if value <= 1.0:
        percent = value * 100
    else:
        percent = value

    return f"{percent:.{decimals}f}%"


def format_date(day: int, month: int, year: int, short: bool = False) -> str:
    """
    Форматировать дату.

    Args:
        day: День
        month: Месяц (1-12)
        year: Год
        short: Краткий формат

    Returns:
        Отформатированная дата

    Examples:
        >>> format_date(15, 6, 2026)
        '15 июня 2026'
        >>> format_date(15, 6, 2026, short=True)
        '15/06/26'
    """
    months_ru = {
        1: "января",
        2: "февраля",
        3: "марта",
        4: "апреля",
        5: "мая",
        6: "июня",
        7: "июля",
        8: "августа",
        9: "сентября",
        10: "октября",
        11: "ноября",
        12: "декабря",
    }

    if short:
        return f"{day:02d}/{month:02d}/{year % 100:02d}"

    month_name = months_ru.get(month, str(month))
    return f"{day} {month_name} {year}"


def format_player_card(player: Dict[str, Any]) -> str:
    """
    Форматировать карточку игрока.

    Args:
        player: Словарь с данными игрока

    Returns:
        Rich Text объект с карточкой игрока
    """
    name = player.get("name", "Неизвестный")
    position = player.get("position", "?")
    rating = player.get("rating", 50)
    age = player.get("age", 0)
    nationality = player.get("nationality", "")
    value = player.get("value", 0)

    pos_color = POSITION_COLORS.get(position, "white")

    card = Text()
    card.append(f"  {name}", style="bold white")
    card.append(f" [{position}]", style=pos_color)
    card.append(f"  {format_rating(rating, colored=False)}", style="bold")
    card.append(f"  Возраст: {age}", style="dim")
    if nationality:
        card.append(f"  {nationality}", style="dim")
    card.append(f"  {format_currency(value)}", style="cyan")

    return card


def format_match_result(
    home_team: str,
    away_team: str,
    home_score: int,
    away_score: int,
    colored: bool = True,
) -> str:
    """
    Форматировать результат матча.

    Args:
        home_team: Название домашней команды
        away_team: Название гостевой команды
        home_score: Счет домашней команды
        away_score: Счет гостевой команды
        colored: Применять ли цвета команд

    Returns:
        Отформатированная строка с результатом

    Examples:
        >>> format_match_result("Манчестер Сити", "Ливерпуль", 2, 1)
        'Манчестер Сити [bold white]2[/] - [bold white]1[/] Ливерпуль'
    """
    if not colored:
        return f"{home_team} {home_score} - {away_score} {away_team}"

    home_color = TEAM_COLORS.get(home_team, "white")
    away_color = TEAM_COLORS.get(away_team, "white")

    return (
        f"[{home_color}]{home_team}[/] "
        f"[bold white]{home_score}[/] - "
        f"[bold white]{away_score}[/] "
        f"[{away_color}]{away_team}[/]"
    )


def format_league_table(teams: List[Dict[str, Any]], show_form: bool = True) -> Any:
    """
    Форматировать таблицу лиги.

    Args:
        teams: Список команд с данными
        show_form: Показывать ли форму команд

    Returns:
        Rich Table объект
    """
    from rich.table import Table

    table = Table(
        title="Таблица лиги",
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
        expand=True,
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Команда", style="bold", min_width=20)
    table.add_column("И", justify="center", width=4)
    table.add_column("В", justify="center", width=4)
    table.add_column("Н", justify="center", width=4)
    table.add_column("П", justify="center", width=4)
    table.add_column("Мячи", justify="center", width=7)
    table.add_column("Оч", justify="center", width=4, style="bold")

    if show_form:
        table.add_column("Форма", justify="center", width=8)

    for i, team in enumerate(teams, 1):
        name = team.get("name", "Неизвестно")
        played = team.get("played", 0)
        won = team.get("won", 0)
        drawn = team.get("drawn", 0)
        lost = team.get("lost", 0)
        goals_for = team.get("goals_for", 0)
        goals_against = team.get("goals_against", 0)
        points = team.get("points", 0)
        form = team.get("form", "")

        team_color = TEAM_COLORS.get(name, "white")

        row = [
            str(i),
            f"[{team_color}]{name}[/]",
            str(played),
            str(won),
            str(drawn),
            str(lost),
            f"{goals_for}:{goals_against}",
            str(points),
        ]

        if show_form:
            row.append(format_form(form[-5:] if form else ""))

        table.add_row(*row)

    return table


def format_stats_display(
    stats: Dict[str, Any], title: str = "Статистика матча"
) -> Any:
    """
    Форматировать статистику матча.

    Args:
        stats: Словарь со статистикой
        title: Заголовок панели

    Returns:
        Rich Table объект
    """
    from rich.table import Table

    table = Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
        expand=True,
    )

    table.add_column("Параметр", style="bold", min_width=20)
    table.add_column("Хозяева", justify="center", style="cyan", width=15)
    table.add_column("Гости", justify="center", style="magenta", width=15)

    stat_names = {
        "possession": "Владение мячом",
        "shots": "Удары",
        "shots_on_target": "Удары в створ",
        "corners": "Угловые",
        "fouls": "Нарушения",
        "yellow_cards": "Желтые карточки",
        "red_cards": "Красные карточки",
        "offsides": "Офсайды",
        "passes": "Передачи",
        "pass_accuracy": "Точность передач",
        "tackles": "Отборы",
        "interceptions": "Перехваты",
    }

    for key, display_name in stat_names.items():
        home_val = stats.get(f"home_{key}", stats.get(key, [0, 0])[0])
        away_val = stats.get(f"away_{key}", stats.get(key, [0, 0])[1])

        if isinstance(home_val, float):
            home_str = f"{home_val:.1f}%"
            away_str = f"{away_val:.1f}%"
        else:
            home_str = str(home_val)
            away_str = str(away_val)

        table.add_row(display_name, home_str, away_str)

    return table


def format_financial_display(data: Dict[str, Any]) -> Any:
    """
    Форматировать финансовую информацию.

    Args:
        data: Словарь с финансовыми данными

    Returns:
        Rich Panel объект
    """
    from rich.panel import Panel
    from rich.table import Table

    table = Table(show_header=True, header_style="bold cyan", show_lines=True)
    table.add_column("Показатель", style="bold", min_width=25)
    table.add_column("Значение", justify="right", min_width=15)

    # Бюджет
    balance = data.get("balance", 0)
    transfer_budget = data.get("transfer_budget", 0)
    wage_budget = data.get("wage_budget", 0)
    wage_bill = data.get("wage_bill", 0)

    balance_style = "green" if balance > 0 else "red"
    table.add_row("Текущий баланс", f"[{balance_style}]{format_currency(balance)}[/]")
    table.add_row("Трансферный бюджет", format_currency(transfer_budget))
    table.add_row("Бюджет на зарплаты", format_currency(wage_budget))
    table.add_row("ФОТ", format_currency(wage_bill))

    # Доходы
    table.add_row("", "")
    table.add_row("[bold]ДОХОДЫ[/]", "", style="bold")

    income = data.get("income", {})
    total_income = income.get("total", 0)
    for source, amount in income.items():
        if source != "total" and amount > 0:
            table.add_row(f"  {source}", format_currency(amount))
    table.add_row("  ИТОГО ДОХОДЫ", f"[green]{format_currency(total_income)}[/]")

    # Расходы
    table.add_row("", "")
    table.add_row("[bold]РАСХОДЫ[/]", "", style="bold")

    expenses = data.get("expenses", {})
    total_expenses = expenses.get("total", 0)
    for source, amount in expenses.items():
        if source != "total" and amount > 0:
            table.add_row(f"  {source}", f"[red]{format_currency(amount)}[/]")
    table.add_row(
        "  ИТОГО РАСХОДЫ", f"[red]{format_currency(total_expenses)}[/]"
    )

    return Panel(
        table,
        title="[bold]Финансы клуба[/]",
        border_style="cyan",
        expand=True,
    )


def format_news_card(article: Dict[str, Any]) -> Any:
    """
    Форматировать карточку новости.

    Args:
        article: Словарь с данными новости

    Returns:
        Rich Panel объект
    """
    from rich.panel import Panel
    from rich.text import Text

    title = article.get("title", "Без заголовка")
    content = article.get("content", "")
    category = article.get("category", "general")
    date = article.get("date", "")
    source = article.get("source", "Пресса")

    # Цвет категории
    cat_colors = {
        "transfer": "cyan",
        "match": "green",
        "injury": "red",
        "award": "yellow",
        "general": "white",
        "press_conf": "magenta",
    }
    cat_color = cat_colors.get(category, "white")

    header = Text()
    header.append(f"[{category.upper()}]", style=f"bold {cat_color}")
    header.append(f"  {title}", style="bold white")
    if date:
        header.append(f"\n{date}", style="dim")

    content_text = Text(content, style="white")

    body = Text()
    body.append_text(header)
    body.append("\n\n")
    body.append_text(content_text)
    body.append(f"\n\nИсточник: {source}", style="dim italic")

    return Panel(
        body,
        title=f"[bold {cat_color}]Новость[/]",
        border_style=cat_color,
        expand=True,
        padding=(1, 2),
    )


def format_bar(value: int, max_val: int, width: int = 20) -> str:
    """
    Создать текстовую полосу прогресса.

    Args:
        value: Текущее значение
        max_val: Максимальное значение
        width: Ширина полосы в символах

    Returns:
        Строка с полосой прогресса

    Examples:
        >>> format_bar(75, 100, 20)
        '███████████████░░░░░░'
    """
    if max_val <= 0:
        return "░" * width

    ratio = min(1.0, max(0.0, value / max_val))
    filled = int(ratio * width)
    empty = width - filled

    # Выбираем цвет по заполненности
    if ratio >= 0.7:
        color = "green"
    elif ratio >= 0.4:
        color = "yellow"
    else:
        color = "red"

    return f"[{color}]{'█' * filled}{'░' * empty}[/] {value}/{max_val}"


def format_position(position: str) -> str:
    """
    Форматировать позицию игрока с цветом.

    Args:
        position: Код позиции (GK, CB, LB, etc.)

    Returns:
        Строка с цветом позиции
    """
    color = POSITION_COLORS.get(position, "white")
    return f"[{color}]{position}[/]"


def format_goals_scorer(scorer: str, minute: int, assist: str = "") -> str:
    """
    Форматировать информацию о голе.

    Args:
        scorer: Имя забившего
        minute: Минута гола
        assist: Имя ассистента

    Returns:
        Отформатированная строка
    """
    result = f"[bold yellow]⚽ {minute}'[/] {scorer}"
    if assist:
        result += f" (асистент: {assist})"
    return result


def format_card_event(player: str, minute: int, card_type: str) -> str:
    """
    Форматировать информацию о карточке.

    Args:
        player: Имя игрока
        minute: Минута
        card_type: Тип карточки ('yellow' или 'red')

    Returns:
        Отформатированная строка
    """
    if card_type == "red":
        return f"[bold red]🟥 {minute}'[/] {player}"
    else:
        return f"[yellow]🟨 {minute}'[/] {player}"
