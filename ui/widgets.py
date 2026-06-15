"""Фабрика виджетов Rich для отображения данных."""

from typing import Any, Dict, List, Optional, Tuple

from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .colors import (
    FORM_COLORS,
    POSITION_COLORS,
    TEAM_COLORS,
    get_color,
    get_position_color,
)


def create_player_table(
    players: List[Dict[str, Any]],
    title: str = "Состав",
    show_position: bool = True,
    show_rating: bool = True,
    show_value: bool = True,
    compact: bool = False,
) -> Table:
    """
    Создать таблицу игроков.

    Args:
        players: Список игроков
        title: Заголовок таблицы
        show_position: Показывать позицию
        show_rating: Показывать рейтинг
        show_value: Показывать стоимость
        compact: Компактный режим

    Returns:
        Rich Table объект
    """
    table = Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        show_lines=not compact,
        expand=True,
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Игрок", style="bold", min_width=20)

    if show_position:
        table.add_column("Поз", justify="center", width=5)

    table.add_column("Возр", justify="center", width=4)
    table.add_column("Рейт", justify="center", width=5)

    if show_value:
        table.add_column("Стоимость", justify="right", width=10)

    for i, player in enumerate(players, 1):
        name = player.get("name", "Неизвестный")
        position = player.get("position", "")
        age = player.get("age", 0)
        rating = player.get("rating", 50)
        value = player.get("value", 0)

        row = [str(i), name]

        if show_position:
            pos_color = get_position_color(position)
            row.append(f"[{pos_color}]{position}[/]")

        row.append(str(age))

        rating_color = get_color(rating)
        row.append(f"[{rating_color}]{rating}[/]")

        if show_value:
            row.append(f"£{value:,.0f}")

        table.add_row(*row)

    return table


def create_team_table(
    teams: List[Dict[str, Any]],
    title: str = "Таблица лиги",
    show_form: bool = True,
    highlight_team: Optional[str] = None,
) -> Table:
    """
    Создать таблицу команд (лиги).

    Args:
        teams: Список команд
        title: Заголовок таблицы
        show_form: Показывать форму
        highlight_team: Выделить конкретную команду

    Returns:
        Rich Table объект
    """
    table = Table(
        title=title,
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
    table.add_column("Разн", justify="center", width=5)
    table.add_column("Оч", justify="center", width=4, style="bold")

    if show_form:
        table.add_column("Форма", justify="center", width=10)

    for i, team in enumerate(teams, 1):
        name = team.get("name", "Неизвестно")
        played = team.get("played", 0)
        won = team.get("won", 0)
        drawn = team.get("drawn", 0)
        lost = team.get("lost", 0)
        goals_for = team.get("goals_for", 0)
        goals_against = team.get("goals_against", 0)
        goal_diff = goals_for - goals_against
        points = team.get("points", 0)
        form = team.get("form", "")

        # Цвет команды
        team_color = TEAM_COLORS.get(name, "white")

        # Выделение выбранной команды
        name_style = f"bold {team_color}" if name == highlight_team else team_color
        row_style = "on grey15" if name == highlight_team else None

        diff_str = f"+{goal_diff}" if goal_diff > 0 else str(goal_diff)
        diff_color = "green" if goal_diff > 0 else ("red" if goal_diff < 0 else "yellow")

        row = [
            str(i),
            f"[{name_style}]{name}[/]",
            str(played),
            str(won),
            str(drawn),
            str(lost),
            f"{goals_for}:{goals_against}",
            f"[{diff_color}]{diff_str}[/]",
            str(points),
        ]

        if show_form:
            form_display = format_form(form[-5:]) if form else ""
            row.append(form_display)

        table.add_row(*row)

    return table


def create_match_fixture(
    home_team: str,
    away_team: str,
    home_score: Optional[int] = None,
    away_score: Optional[int] = None,
    matchday: Optional[int] = None,
    date: Optional[str] = None,
    venue: Optional[str] = None,
) -> Panel:
    """
    Создать панель матча.

    Args:
        home_team: Домашняя команда
        away_team: Гостевая команда
        home_score: Счет домашней (None для предматчевого)
        away_score: Счет гостевой
        matchday: Тур
        date: Дата матча
        venue: Стадион

    Returns:
        Rich Panel объект
    """
    home_color = TEAM_COLORS.get(home_team, "white")
    away_color = TEAM_COLORS.get(away_team, "white")

    content = Text()

    # Дата и тур
    if date or matchday:
        header = Text()
        if matchday:
            header.append(f"Тур {matchday}", style="bold cyan")
        if date:
            if matchday:
                header.append("  |  ", style="dim")
            header.append(date, style="dim")
        content.append_text(header)
        content.append("\n")

    # Команды и счет
    content.append(f"\n  {home_team}", style=f"bold {home_color}")
    content.append("  ")

    if home_score is not None and away_score is not None:
        content.append(f"{home_score} : {away_score}", style="bold bright_white")
    else:
        content.append("vs", style="bold yellow")

    content.append("  ")
    content.append(f"{away_team}\n", style=f"bold {away_color}")

    # Стадион
    if venue:
        content.append(f"\n  {venue}", style="dim italic")

    # Стиль рамки
    border_style = home_color if home_score is None else "cyan"

    return Panel(
        content,
        title=f"[bold]{'Матч' if home_score is None else 'Результат'}[/]",
        border_style=border_style,
        expand=True,
        padding=(1, 2),
    )


def create_formation_display(
    formation: str,
    players: Dict[str, List[Dict[str, Any]]],
    team_color: str = "cyan",
) -> Table:
    """
    Создать отображение формации команды.

    Args:
        formation: Строка формации (например, "4-3-3")
        players: Словарь {позиция: [игроки]}
        team_color: Цвет команды

    Returns:
        Rich Table объект с визуализацией формации
    """
    # Парсим формацию
    lines = [int(x) for x in formation.split("-")]

    # Создаем таблицу-поле
    table = Table(
        title=f"Формация: {formation}",
        show_header=False,
        show_lines=False,
        expand=True,
        padding=(0, 1),
    )

    table.add_column("Поле", justify="center", ratio=1)

    # Вратарь
    gk = players.get("GK", [{}])[0] if players.get("GK") else {}
    gk_name = gk.get("name", "???")
    gk_rating = gk.get("rating", 50)
    gk_color = get_color(gk_rating)

    table.add_row(f"[{team_color}]╔═══════════════════════════╗[/]")
    table.add_row(f"[{team_color}]║[/]  [bold yellow]🟨 {gk_name}[/] [{gk_color}]({gk_rating})[/]  [{team_color}]║[/]")
    table.add_row(f"[{team_color}]║[/]{'':^25}[{team_color}]║[/]")
    table.add_row(f"[{team_color}]║[/]{'':^25}[{team_color}]║[/]")

    # Защита
    defenders = []
    for pos in ["CB", "LB", "RB", "LWB", "RWB"]:
        defenders.extend(players.get(pos, []))

    if defenders and len(lines) >= 1:
        def_count = lines[0]
        def_names = []
        for p in defenders[:def_count]:
            name = p.get("name", "???")
            rating = p.get("rating", 50)
            color = get_color(rating)
            pos = p.get("position", "?")
            pos_color = get_position_color(pos)
            def_names.append(f"[{pos_color}]{pos}[/] [{color}]{name}({rating})[/]")

        # Разбиваем на строки
        for i in range(0, len(def_names), 3):
            row_names = def_names[i : i + 3]
            row_str = "  ".join(row_names)
            table.add_row(f"[{team_color}]║[/] {row_str:<25} [{team_color}]║[/]")

    table.add_row(f"[{team_color}]║[/]{'':^25}[{team_color}]║[/]")

    # Полузащита
    midfielders = []
    for pos in ["CDM", "CM", "CAM", "LM", "RM"]:
        midfielders.extend(players.get(pos, []))

    if midfielders and len(lines) >= 2:
        mid_count = lines[1]
        mid_names = []
        for p in midfielders[:mid_count]:
            name = p.get("name", "???")
            rating = p.get("rating", 50)
            color = get_color(rating)
            pos = p.get("position", "?")
            pos_color = get_position_color(pos)
            mid_names.append(f"[{pos_color}]{pos}[/] [{color}]{name}({rating})[/]")

        for i in range(0, len(mid_names), 3):
            row_names = mid_names[i : i + 3]
            row_str = "  ".join(row_names)
            table.add_row(f"[{team_color}]║[/] {row_str:<25} [{team_color}]║[/]")

    table.add_row(f"[{team_color}]║[/]{'':^25}[{team_color}]║[/]")

    # Нападение
    forwards = []
    for pos in ["LW", "RW", "CF", "ST", "SS"]:
        forwards.extend(players.get(pos, []))

    if forwards and len(lines) >= 3:
        fwd_count = lines[2]
        fwd_names = []
        for p in forwards[:fwd_count]:
            name = p.get("name", "???")
            rating = p.get("rating", 50)
            color = get_color(rating)
            pos = p.get("position", "?")
            pos_color = get_position_color(pos)
            fwd_names.append(f"[{pos_color}]{pos}[/] [{color}]{name}({rating})[/]")

        for i in range(0, len(fwd_names), 3):
            row_names = fwd_names[i : i + 3]
            row_str = "  ".join(row_names)
            table.add_row(f"[{team_color}]║[/] {row_str:<25} [{team_color}]║[/]")

    table.add_row(f"[{team_color}]║[/]{'':^25}[{team_color}]║[/]")
    table.add_row(f"[{team_color}]╚═══════════════════════════╝[/]")

    return table


def create_stats_display(
    stats: Dict[str, Any],
    title: str = "Статистика матча",
    home_name: str = "Хозяева",
    away_name: str = "Гости",
) -> Table:
    """
    Создать таблицу статистики матча.

    Args:
        stats: Словарь со статистикой
        title: Заголовок
        home_name: Имя домашней команды
        away_name: Имя гостевой команды

    Returns:
        Rich Table объект
    """
    table = Table(
        title=title,
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
        expand=True,
    )

    table.add_column("Параметр", style="bold", min_width=20)
    table.add_column(home_name, justify="center", style="cyan", width=15)
    table.add_column("", justify="center", width=15)
    table.add_column(away_name, justify="center", style="magenta", width=15)

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
        "saves": "Сейвы",
        "aerial_duels": "Воздушные единоборства",
    }

    for key, display_name in stat_names.items():
        home_val = stats.get(f"home_{key}", stats.get(key, [0, 0])[0])
        away_val = stats.get(f"away_{key}", stats.get(key, [0, 0])[1])

        # Форматируем значения
        if isinstance(home_val, float):
            home_str = f"{home_val:.1f}%"
            away_str = f"{away_val:.1f}%"
        else:
            home_str = str(home_val)
            away_str = str(away_val)

        # Визуальная полоска сравнения
        try:
            total = float(home_val) + float(away_val)
            if total > 0:
                home_pct = float(home_val) / total
                bar_width = 10
                home_bar = "█" * int(home_pct * bar_width)
                away_bar = "█" * int((1 - home_pct) * bar_width)
                comparison = f"[cyan]{home_bar}[/][dim]{'░' * (bar_width - len(home_bar))}[/]|[dim]{'░' * (bar_width - len(away_bar))}[/][magenta]{away_bar}[/]"
            else:
                comparison = ""
        except (ValueError, TypeError):
            comparison = ""

        table.add_row(display_name, home_str, comparison, away_str)

    return table


def create_financial_display(data: Dict[str, Any]) -> Panel:
    """
    Создать панель финансов клуба.

    Args:
        data: Словарь с финансовыми данными

    Returns:
        Rich Panel объект
    """
    table = Table(show_header=True, header_style="bold cyan", show_lines=True)
    table.add_column("Показатель", style="bold", min_width=25)
    table.add_column("Значение", justify="right", min_width=15)

    # Баланс
    balance = data.get("balance", 0)
    balance_color = "green" if balance > 0 else "red"
    table.add_row("Текущий баланс", f"[{balance_color}]£{balance:,.0f}[/]")

    # Трансферный бюджет
    transfer = data.get("transfer_budget", 0)
    table.add_row("Трансферный бюджет", f"£{transfer:,.0f}")

    # Зарплаты
    wage_bill = data.get("wage_bill", 0)
    wage_budget = data.get("wage_budget", 0)
    wage_pct = (wage_bill / wage_budget * 100) if wage_budget > 0 else 0
    wage_color = "green" if wage_pct < 80 else ("yellow" if wage_pct < 100 else "red")

    table.add_row("ФОТ (неделя)", f"£{wage_bill:,.0f}")
    table.add_row("Бюджет ФОТ", f"£{wage_budget:,.0f}")
    table.add_row(
        "Загрузка ФОТ",
        f"[{wage_color}]{wage_pct:.1f}%[/]",
    )

    table.add_row("", "")

    # Доходы
    table.add_row("[bold green]ДОХОДЫ[/]", "", style="bold")
    income = data.get("income", {})
    total_income = 0
    for source, amount in income.items():
        if amount > 0:
            table.add_row(f"  {source}", f"[green]£{amount:,.0f}[/]")
            total_income += amount
    table.add_row(
        "  ИТОГО ДОХОДЫ", f"[bold green]£{total_income:,.0f}[/]"
    )

    table.add_row("", "")

    # Расходы
    table.add_row("[bold red]РАСХОДЫ[/]", "", style="bold")
    expenses = data.get("expenses", {})
    total_expenses = 0
    for source, amount in expenses.items():
        if amount > 0:
            table.add_row(f"  {source}", f"[red]£{amount:,.0f}[/]")
            total_expenses += amount
    table.add_row(
        "  ИТОГО РАСХОДЫ", f"[bold red]£{total_expenses:,.0f}[/]"
    )

    # Прибыль
    table.add_row("", "")
    profit = total_income - total_expenses
    profit_color = "green" if profit > 0 else "red"
    table.add_row(
        "ПРИБЫЛЬ/УБЫТОК",
        f"[bold {profit_color}]£{profit:+,.0f}[/]",
    )

    return Panel(
        table,
        title="[bold]💰 Финансы клуба[/]",
        border_style="cyan",
        expand=True,
    )


def create_news_card(article: Dict[str, Any]) -> Panel:
    """
    Создать карточку новости.

    Args:
        article: Словарь с данными новости

    Returns:
        Rich Panel объект
    """
    title = article.get("title", "Без заголовка")
    content = article.get("content", "")
    category = article.get("category", "general")
    date = article.get("date", "")
    source = article.get("source", "Пресса")
    importance = article.get("importance", "normal")

    # Цвет категории
    cat_colors = {
        "transfer": "cyan",
        "match": "green",
        "injury": "red",
        "award": "yellow",
        "general": "white",
        "press_conf": "magenta",
        "training": "bright_green",
        "finance": "bright_yellow",
    }
    cat_color = cat_colors.get(category, "white")

    # Важность
    border_style = cat_color
    if importance == "high":
        border_style = f"bold {cat_color}"

    body = Text()
    body.append(f"[{category.upper()}]", style=f"bold {cat_color}")
    body.append(f"  {title}", style="bold white")
    if date:
        body.append(f"\n{date}", style="dim")
    body.append(f"\n\n{content}", style="white")
    body.append(f"\n\nИсточник: {source}", style="dim italic")

    return Panel(
        body,
        title=f"[bold {cat_color}]📰 Новость[/]",
        border_style=border_style,
        expand=True,
        padding=(1, 2),
    )


def create_bar(value: int, max_val: int, width: int = 20) -> str:
    """
    Создать текстовую полосу прогресса.

    Args:
        value: Текущее значение
        max_val: Максимальное значение
        width: Ширина в символах

    Returns:
        Строка с полосой

    Examples:
        >>> create_bar(75, 100, 20)
        '████████████████░░░░ 75%'
    """
    if max_val <= 0:
        return "░" * width

    ratio = min(1.0, max(0.0, value / max_val))
    filled = int(ratio * width)
    empty = width - filled

    if ratio >= 0.7:
        color = "green"
    elif ratio >= 0.4:
        color = "yellow"
    else:
        color = "red"

    bar = f"[{color}]{'█' * filled}{'░' * empty}[/] {value}/{max_val}"
    return bar


def create_substitution_display(
    player_out: Dict[str, Any],
    player_in: Dict[str, Any],
    minute: int,
    reason: str = "тактическая замена",
) -> Panel:
    """
    Создать отображение замены.

    Args:
        player_out: Выходящий игрок
        player_in: Входящий игрок
        minute: Минута замены
        reason: Причина

    Returns:
        Rich Panel объект
    """
    out_name = player_out.get("name", "???")
    out_pos = player_out.get("position", "?")
    in_name = player_in.get("name", "???")
    in_pos = player_in.get("position", "?")

    content = Text()
    content.append(f"🔄 Замена на {minute}'\n", style="bold yellow")
    content.append(f"  Выходит: ", style="dim")
    content.append(f"{out_name}", style="bold red")
    content.append(f" ({out_pos})\n", style="dim")
    content.append(f"  На поле: ", style="dim")
    content.append(f"{in_name}", style="bold green")
    content.append(f" ({in_pos})\n", style="dim")
    content.append(f"\n  Причина: {reason}", style="italic dim")

    return Panel(
        content,
        title="[bold]Замена[/]",
        border_style="yellow",
        expand=True,
    )


def create_event_card(
    event_type: str,
    minute: int,
    description: str,
    team: str = "",
) -> Panel:
    """
    Создать карточку события матча.

    Args:
        event_type: Тип события (goal, card, substitution, etc.)
        minute: Минута
        description: Описание
        team: Название команды

    Returns:
        Rich Panel объект
    """
    icons = {
        "goal": "⚽",
        "yellow_card": "🟨",
        "red_card": "🟥",
        "substitution": "🔄",
        "injury": "🏥",
        "penalty": "🎯",
        "free_kick": "FK",
        "corner": "🚩",
        "offside": "🏴",
    }

    colors = {
        "goal": "bold yellow",
        "yellow_card": "yellow",
        "red_card": "bold red",
        "substitution": "cyan",
        "injury": "red",
        "penalty": "bold cyan",
        "free_kick": "bright_cyan",
        "corner": "bright_green",
        "offside": "dim",
    }

    icon = icons.get(event_type, "•")
    color = colors.get(event_type, "white")

    body = Text()
    body.append(f"{icon} {minute}'", style=f"bold {color}")
    if team:
        team_color = TEAM_COLORS.get(team, "white")
        body.append(f" [{team_color}]{team}[/]", style=team_color)
    body.append(f"\n  {description}", style="white")

    return Panel(
        body,
        border_style=color,
        expand=True,
        padding=(0, 1),
    )


def create_comparison_bar(
    home_val: int,
    away_val: int,
    label: str,
    width: int = 20,
) -> Text:
    """
    Создать полосу сравнения двух значений.

    Args:
        home_val: Значение домашней команды
        away_val: Значение гостевой команды
        label: Название параметра
        width: Ширина полосы

    Returns:
        Rich Text объект
    """
    total = home_val + away_val
    if total == 0:
        home_ratio = 0.5
    else:
        home_ratio = home_val / total

    home_width = int(home_ratio * width)
    away_width = width - home_width

    text = Text()
    text.append(f"{home_val}", style="cyan")
    text.append(" ")
    text.append("█" * home_width, style="cyan")
    text.append(" ", style="dim")
    text.append(f"{label}", style="bold")
    text.append(" ", style="dim")
    text.append("█" * away_width, style="magenta")
    text.append(" ")
    text.append(f"{away_val}", style="magenta")

    return text
