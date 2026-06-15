"""
game/news.py — Генератор новостей.
Создаёт новости о матчах, трансферах, травмах и общих событиях.
"""

import random
from typing import Any, Dict, List, Optional


class NewsGenerator:
    """
    Генератор игровых новостей.
    Создаёт разнообразные новости для игровой вселенной.
    """

    def __init__(self) -> None:
        self._generated_news: List[Dict[str, Any]] = []
        self._news_id_counter = 0

    # ── Новости матчей ──────────────────────────────────────────────
    def generate_match_news(
        self,
        home_team: str,
        away_team: str,
        home_goals: int,
        away_goals: int,
        events: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Генерация новости о матче.
        """
        self._news_id_counter += 1

        # Определяем результат
        if home_goals > away_goals:
            winner = home_team
            loser = away_team
            result_type = "home_win"
        elif away_goals > home_goals:
            winner = away_team
            loser = home_team
            result_type = "away_win"
        else:
            winner = None
            result_type = "draw"

        # Генерируем заголовок
        if result_type == "draw":
            title_templates = [
                f"{home_team} и {away_team} сыграли вничью",
                f"Ничья в матче {home_team} — {away_team}",
                f"Ничья {home_goals}:{away_goals} в матче {home_team} — {away_team}",
            ]
        else:
            title_templates = [
                f"{winner} одержал победу над {loser}",
                f"{winner} обыграл {loser} со счётом {home_goals}:{away_goals}",
                f"Три очка {winner} в матче с {loser}",
            ]
        title = random.choice(title_templates)

        # Генерируем текст
        content_templates = [
            f"Матч завершился со счётом {home_goals}:{away_goals}. "
            f"{'Ничья' if result_type == 'draw' else f'{winner} одержал уверенную победу'}.",

            f"В матче {home_team} — {away_team} мячи забили: " +
            (", ".join([e.get("player_name", "Игрок") for e in (events or []) if e.get("event_type") == "goal"]) or "голов не было") +
            f". Итоговый счёт {home_goals}:{away_goals}.",

            f"Зрители стали свидетелями интересного матча между {home_team} и {away_team}. "
            f"Счёт {home_goals}:{away_goals} говорит о равной борьбе." if result_type == "draw"
            else f"{winner} контролировал ход матча и заслуженно победил {loser} {home_goals}:{away_goals}.",
        ]
        content = random.choice(content_templates)

        news = {
            "id": self._news_id_counter,
            "title": title,
            "content": content,
            "category": "match",
            "priority": "high" if abs(home_goals - away_goals) <= 1 else "normal",
            "teams": [home_team, away_team],
            "score": f"{home_goals}:{away_goals}",
        }
        self._generated_news.append(news)
        return news

    # ── Трансферные новости ─────────────────────────────────────────
    def generate_transfer_news(
        self,
        player_name: str,
        from_team: Optional[str],
        to_team: str,
        fee: Optional[int] = None,
        transfer_type: str = "transfer",
    ) -> Dict[str, Any]:
        """
        Генерация новости о трансфере.
        """
        self._news_id_counter += 1

        if transfer_type == "loan":
            title_templates = [
                f"{player_name} отправляется в аренду в {to_team}",
                f"{to_team} арендовал {player_name}",
            ]
            action = "отправляется в аренду"
        else:
            fee_str = f"за {fee:,} €" if fee else "в результате трансфера"
            title_templates = [
                f"{player_name} перешёл в {to_team} {fee_str}",
                f"{to_team} подписал {player_name} {fee_str}",
                f"Трансфер дня: {player_name} — {to_team}",
            ]
            action = "перешёл"

        title = random.choice(title_templates)

        if from_team:
            content = (
                f"Полузащитник/нападающий {player_name} {action} из {from_team} в {to_team}. "
                f"{'Сумма трансфера не разглашается.' if not fee else f'Сумма трансфера составила {fee:,} €.'}"
            )
        else:
            content = (
                f"{player_name} теперь игрок {to_team}. "
                f"Клуб укрепил свой состав перед началом сезона."
            )

        news = {
            "id": self._news_id_counter,
            "title": title,
            "content": content,
            "category": "transfer",
            "priority": "high",
            "player": player_name,
            "from_team": from_team,
            "to_team": to_team,
            "fee": fee,
            "transfer_type": transfer_type,
        }
        self._generated_news.append(news)
        return news

    # ── Новости о травмах ───────────────────────────────────────────
    def generate_injury_news(
        self,
        player_name: str,
        team: str,
        injury_type: str = "травма",
        weeks_out: int = 2,
    ) -> Dict[str, Any]:
        """
        Генерация новости о травме игрока.
        """
        self._news_id_counter += 1

        injury_types = [
            "растяжение связок", "перелом стопы", "травма колена",
            "травма голеностопа", "смещение плеча", "рваная рана",
            "сотрясение мозга", "травма спины", "воспаление сухожилий",
        ]
        if injury_type == "травма":
            injury_type = random.choice(injury_types)

        title_templates = [
            f"{player_name} пропустит {weeks_out} {'неделю' if weeks_out == 1 else 'недель'} из-за травмы",
            f"Потеря для {team}: {player_name} травмирован",
            f"{team} потерял {player_name} на {weeks_out} недель",
        ]
        title = random.choice(title_templates)

        content = (
            f"Полузащитник/нападающий {player_name} ({team}) получил {injury_type} "
            f"и не сможет помогать команде в течение {weeks_out} "
            f"{'недели' if weeks_out == 1 else 'недель'}. "
            f"Это серьёзная потеря для клуба."
        )

        news = {
            "id": self._news_id_counter,
            "title": title,
            "content": content,
            "category": "injury",
            "priority": "high",
            "player": player_name,
            "team": team,
            "injury_type": injury_type,
            "weeks_out": weeks_out,
        }
        self._generated_news.append(news)
        return news

    # ── Общие новости ───────────────────────────────────────────────
    def generate_general_news(
        self,
        headline: str,
        body: str,
        category: str = "general",
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """
        Генерация общей новости.
        """
        self._news_id_counter += 1

        news = {
            "id": self._news_id_counter,
            "title": headline,
            "content": body,
            "category": category,
            "priority": priority,
        }
        self._generated_news.append(news)
        return news

    def generate_manager_news(self, manager_name: str, club: str, event: str) -> Dict[str, Any]:
        """Новость о менеджере."""
        self._news_id_counter += 1

        if event == "hired":
            title = f"{manager_name} назначен главным тренером {club}"
            content = (
                f"{club} объявил о назначении {manager_name} на пост главного тренера. "
                f"Новый наставник подписал контракт на 2 года."
            )
        elif event == "fired":
            title = f"{manager_name} уволен из {club}"
            content = (
                f"{club} расторг контракт с {manager_name}. "
                f"Причины увольнения — неудовлетворительные результаты."
            )
        else:
            title = f"{manager_name} и {club}: {event}"
            content = f"Произошло событие: {manager_name} — {club}: {event}"

        news = {
            "id": self._news_id_counter,
            "title": title,
            "content": content,
            "category": "manager",
            "priority": "high",
            "manager": manager_name,
            "team": club,
            "event": event,
        }
        self._generated_news.append(news)
        return news

    def generate_award_news(self, award_name: str, winner_name: str, team: str) -> Dict[str, Any]:
        """Новость об награде."""
        self._news_id_counter += 1

        title = f"{winner_name} ({team}) победил в номинации «{award_name}»"
        content = (
            f"Полузащитник/нападающий {winner_name} из {team} "
            f"победил в голосовании за звание «{award_name}». "
            f"Фанаты и эксперты отметили его выдающиеся результаты."
        )

        news = {
            "id": self._news_id_counter,
            "title": title,
            "content": content,
            "category": "award",
            "priority": "normal",
            "award": award_name,
            "player": winner_name,
            "team": team,
        }
        self._generated_news.append(news)
        return news

    # ── Получение новостей ──────────────────────────────────────────
    def get_latest_news(self, count: int = 10) -> List[Dict[str, Any]]:
        """Получение последних N новостей."""
        return self._generated_news[-count:]

    def get_news_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Получение новостей по категории."""
        return [n for n in self._generated_news if n.get("category") == category]

    def clear_news(self) -> None:
        """Очистка списка новостей."""
        self._generated_news.clear()

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь."""
        return {
            "news_id_counter": self._news_id_counter,
            "generated_news": self._generated_news[-50:],  # Последние 50 новостей
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NewsGenerator":
        """Десериализация из словаря."""
        ng = cls()
        ng._news_id_counter = data.get("news_id_counter", 0)
        ng._generated_news = data.get("generated_news", [])
        return ng

    def __repr__(self) -> str:
        return f"NewsGenerator(news_count={len(self._generated_news)})"
