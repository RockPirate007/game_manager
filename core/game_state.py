"""
core/game_state.py — Глобальное состояние игры (синглтон).
Хранит все данные текущей карьеры: клубы, игроков, лиги,
турниры,fixtures и позволяет сохранять/загружать игру.
"""

import json
import os
import random
from typing import Any, Dict, List, Optional

from core.constants import (
    SEASON_MATCHDAYS,
    Position,
    PlayStyle,
    FORMATIONS,
)
from core.event_bus import EventBus, EventType
from models.player import Player
from models.team import Team
from models.league import League
from models.match import Match


class GameState:
    """
    Синглтон, хранящий состояние всей игры.
    Поддерживает инициализацию, обновление, сохранение и загрузку.
    """

    _instance: Optional["GameState"] = None

    def __new__(cls) -> "GameState":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        # Основные данные
        self.current_club_id: int = 0
        self.season: int = 2024
        self.matchday: int = 0
        self.week: int = 0

        # Коллекции
        self.clubs: Dict[int, Team] = {}
        self.players: Dict[int, Player] = {}
        self.leagues: Dict[int, League] = {}
        self.fixtures: Dict[int, List[Match]] = {}  # matchday -> matches
        self.tournaments: Dict[int, Any] = {}  # id -> Tournament

        # Новости и события
        self.news: List[Dict[str, Any]] = []
        self.transfer_offers: List[Dict[str, Any]] = []
        self.history: List[Dict[str, Any]] = []

        # Шина событий
        self.event_bus = EventBus()

        # Флаг инициализации
        self._is_initialized = False

    # ── Инициализация новой игры ────────────────────────────────────
    def initialize_new_game(
        self,
        club_name: str = "Аматорский клуб",
        manager_name: str = "Менеджер",
        difficulty: str = "NORMAL",
    ) -> None:
        """
        Инициализация новой карьеры.
        Создаёт начальные данные: клуб, игроков, лигу.
        """
        self._is_initialized = True

        # Создаём клуб игрока
        player_club = Team(
            team_id=1,
            name=club_name,
            reputation=40,
            budget=5_000_000,
            wage_budget=200_000,
            city="Москва",
            country="Россия",
        )

        # Генерируем состав клуба
        self._generate_squad(player_club)
        self.clubs[1] = player_club
        self.current_club_id = 1

        # Создаём соперников
        rival_names = [
            "Спартак", "ЦСКА", "Зенит", "Локомотив", "Динамо",
            "Краснодар", "Ростов", "Крылья Советов", "Рубин", "Ахмат",
            "Урал", "Оренбург", "Факел", "Химки", "Балтика",
        ]
        for i, name in enumerate(rival_names, 2):
            rival = Team(
                team_id=i,
                name=name,
                reputation=random.randint(30, 80),
                budget=random.randint(2_000_000, 20_000_000),
                wage_budget=random.randint(100_000, 800_000),
                city="Город",
                country="Россия",
            )
            self._generate_squad(rival)
            self.clubs[i] = rival

        # Создаём лигу
        team_ids = list(self.clubs.keys())
        team_names = {tid: self.clubs[tid].name for tid in team_ids}
        league = League(
            league_id=1,
            name="Премьер-лига",
            country="Россия",
            tier=1,
            team_ids=team_ids,
            team_names=team_names,
        )
        self.leagues[1] = league

        # Генерируем расписание
        self._generate_fixtures()

        self.matchday = 0
        self.week = 0
        self.season = 2024

        self.event_bus.emit(
            EventType.SEASON_START,
            {"season": self.season, "club": club_name},
        )

    def _generate_squad(self, team: Team) -> None:
        """Генерация состава команды из случайных игроков."""
        # Определяем состав по формации
        formation = team.formation
        position_counts = self._parse_formation(formation)

        # Генерируем вратаря
        for _ in range(position_counts.get("GK", 1)):
            player = self._create_random_player(team.id, Position.GK)
            team.add_player(player)
            self.players[player.id] = player

        # Генерируем полевых игроков
        for pos_str, count in position_counts.items():
            if pos_str == "GK":
                continue
            position = Position(pos_str)
            for _ in range(count):
                player = self._create_random_player(team.id, position)
                team.add_player(player)
                self.players[player.id] = player

        # Добавляем запасных
        backup_positions = [Position.CB, Position.CM, Position.ST, Position.LW, Position.RW]
        for pos in backup_positions:
            for _ in range(2):
                player = self._create_random_player(team.id, pos)
                team.add_player(player)
                self.players[player.id] = player

    def _parse_formation(self, formation: str) -> Dict[str, int]:
        """Парсинг формации (например, '4-4-2') в словарь позиций."""
        parts = formation.split("-")
        if len(parts) < 2:
            return {"GK": 1, "CB": 4, "CM": 4, "ST": 2}

        defenders = int(parts[0])
        midfielders = int(parts[1])
        forwards = int(parts[2]) if len(parts) > 2 else 1

        result = {"GK": 1}

        # Защитники
        if defenders == 3:
            result["CB"] = 3
        elif defenders == 4:
            result["LB"] = 1
            result["CB"] = 2
            result["RB"] = 1
        elif defenders == 5:
            result["LB"] = 1
            result["CB"] = 3
            result["RB"] = 1

        # Полузащитники
        if midfielders == 3:
            result["CM"] = 3
        elif midfielders == 4:
            result["CM"] = 4
        elif midfielders == 5:
            result["DM"] = 1
            result["CM"] = 3
            result["AM"] = 1

        # Нападающие
        if forwards == 1:
            result["ST"] = 1
        elif forwards == 2:
            result["ST"] = 2
        elif forwards == 3:
            result["LW"] = 1
            result["RW"] = 1
            result["ST"] = 1

        return result

    def _create_random_player(self, team_id: int, position: Position) -> Player:
        """Создание случайного игрока."""
        # Базовые значения в зависимости от позиции
        base_names_gk = ["Иванов", "Петров", "Сидоров"]
        base_names_out = ["Смирнов", "Козлов", "Попов", "Волков", "Новиков",
                          "Морозов", "Соколов", "Лебедев", "Орлов", "Зайцев"]
        base_names_att = ["Соколов", "Лебедев", "Орлов", "Зайцев", "Белов",
                          "Комаров", "Баранов", "Кузнецов", "Макаров", "Андреев"]

        if position == Position.GK:
            name = random.choice(base_names_gk)
        elif position.is_attacker:
            name = random.choice(base_names_att)
        else:
            name = random.choice(base_names_out)

        first_names = ["Алексей", "Дмитрий", "Сергей", "Андрей", "Михаил",
                        "Иван", "Артём", "Никита", "Максим", "Евгений"]
        name = f"{random.choice(first_names)} {name}"

        # Рейтинг зависит от репутации клуба
        team = self.clubs.get(team_id)
        base_rating = 45 + (team.reputation if team else 50) // 3
        rating = random.randint(max(30, base_rating - 15), min(90, base_rating + 15))
        potential = random.randint(rating, min(99, rating + random.randint(0, 20)))

        player_id = random.randint(1000, 999999)
        while player_id in self.players:
            player_id = random.randint(1000, 999999)

        return Player(
            player_id=player_id,
            name=name,
            age=random.randint(17, 35),
            nationality="Россия",
            position=position,
            rating=rating,
            potential=potential,
            morale=random.randint(60, 85),
            form=random.randint(50, 80),
            wage=random.randint(10000, 500000),
            contract_years=random.randint(1, 5),
            team_id=team_id,
        )

    def _generate_fixtures(self) -> None:
        """Генерация календаря матчей по системе каждый с каждым."""
        league = self.leagues.get(1)
        if not league:
            return

        team_ids = league.teams
        n = len(team_ids)
        matchday_num = 0

        # Круговой турнир (каждый с каждым дома и на выезде)
        for _ in range(2):  # Два круга
            for i in range(n):
                for j in range(i + 1, n):
                    matchday_num += 1
                    if matchday_num not in self.fixtures:
                        self.fixtures[matchday_num] = []

                    home_id = team_ids[i]
                    away_id = team_ids[j]

                    match = Match(
                        match_id=matchday_num * 100 + i * n + j,
                        home_team_id=home_id,
                        away_team_id=away_id,
                        home_team_name=self.clubs[home_id].name,
                        away_team_name=self.clubs[away_id].name,
                        competition="Премьер-лига",
                    )
                    self.fixtures[matchday_num].append(match)

                    # Чередуем дома/выезд во втором круге
                    if _ == 1:
                        match2 = Match(
                            match_id=matchday_num * 1000 + i * n + j,
                            home_team_id=away_id,
                            away_team_id=home_id,
                            home_team_name=self.clubs[away_id].name,
                            away_team_name=self.clubs[home_id].name,
                            competition="Премьер-лига",
                        )
                        if matchday_num + n not in self.fixtures:
                            self.fixtures[matchday_num + n] = []
                        self.fixtures[matchday_num + n].append(match2)

    # ── Обновление состояния ────────────────────────────────────────
    def advance_week(self) -> List[Dict[str, Any]]:
        """
        Продвижение времени на одну неделю.
        Возвращает список событий, произошедших за неделю.
        """
        self.week += 1
        events = []

        # Обновляем игроков
        for player in self.players.values():
            old_form = player.form
            # Стихийное изменение формы
            form_change = random.randint(-5, 5)
            player._form = max(0, min(100, player._form + form_change))

            # Лечение травм
            if player.is_injured():
                player.heal(1)
                if not player.is_injured():
                    events.append({
                        "type": "recovery",
                        "player_id": player.id,
                        "player_name": player.name,
                        "message": f"{player.name} вернулся после травмы",
                    })

            # Усталость восстанавливается за неделю отдыха
            player.rest(15)

            # Проверка травм (случайные)
            if random.random() < 0.01:
                weeks = random.randint(1, 8)
                player.injure(weeks)
                events.append({
                    "type": "injury",
                    "player_id": player.id,
                    "player_name": player.name,
                    "weeks": weeks,
                    "message": f"{player.name} травмирован на {weeks} нед.",
                })

        # Проверяем, пора ли проводить матч
        if self.week % 1 == 0:  # Каждую неделю
            self.matchday += 1
            matchday_events = self._simulate_matchday()
            events.extend(matchday_events)

        return events

    def _simulate_matchday(self) -> List[Dict[str, Any]]:
        """Симуляция всех матчей текущего тура."""
        events = []
        matches = self.fixtures.get(self.matchday, [])

        for match in matches:
            if match.played:
                continue

            home_team = self.clubs.get(match.home_team_id)
            away_team = self.clubs.get(match.away_team_id)

            if not home_team or not away_team:
                continue

            # Собираем данные игроков
            home_players = [
                {"id": p.id, "name": p.name, "position": p.position.value}
                for p in home_team.get_starting_xi()
            ]
            away_players = [
                {"id": p.id, "name": p.name, "position": p.position.value}
                for p in away_team.get_starting_xi()
            ]

            result = match.simulate(
                home_strength=home_team.get_avg_rating(),
                away_strength=away_team.get_avg_rating(),
                home_morale=70,
                away_morale=65,
                home_form=60,
                away_form=55,
                home_players=home_players,
                away_players=away_players,
            )

            # Обновляем статистику команд
            if match.get_winner() == match.home_team_id:
                home_team.update_season_record(
                    win=True, goals_for=match.home_goals,
                    goals_against=match.away_goals
                )
                away_team.update_season_record(
                    loss=True, goals_for=match.away_goals,
                    goals_against=match.home_goals
                )
            elif match.get_winner() == match.away_team_id:
                away_team.update_season_record(
                    win=True, goals_for=match.away_goals,
                    goals_against=match.home_goals
                )
                home_team.update_season_record(
                    loss=True, goals_for=match.home_goals,
                    goals_against=match.away_goals
                )
            else:
                home_team.update_season_record(
                    draw=True, goals_for=match.home_goals,
                    goals_against=match.away_goals
                )
                away_team.update_season_record(
                    draw=True, goals_for=match.away_goals,
                    goals_against=match.home_goals
                )

            # Обновляем таблицу лиги
            self._update_league_table(match)

            events.append({
                "type": "match_result",
                "match_id": match.id,
                "home": match.home_team_name,
                "away": match.away_team_name,
                "score": match.get_result(),
            })

            self.event_bus.emit(
                EventType.MATCH_END,
                {"match": match.get_summary()},
            )

        return events

    def _update_league_table(self, match: Match) -> None:
        """Обновление таблицы лиги после матча."""
        for league in self.leagues.values():
            if match.home_team_id in league.teams and match.away_team_id in league.teams:
                league.record_match(
                    home_team_id=match.home_team_id,
                    away_team_id=match.away_team_id,
                    home_goals=match.home_goals,
                    away_goals=match.away_goals,
                )
                break

    # ── Доступ к данным ─────────────────────────────────────────────
    def get_club_by_id(self, club_id: int) -> Optional[Team]:
        """Получение клуба по ID."""
        return self.clubs.get(club_id)

    def get_club_players(self, club_id: int) -> List[Player]:
        """Получение всех игроков клуба."""
        return [p for p in self.players.values() if p.team_id == club_id]

    def get_current_matchday_fixtures(self) -> List[Match]:
        """Получение матчей текущего тура."""
        return self.fixtures.get(self.matchday, [])

    def get_player(self, player_id: int) -> Optional[Player]:
        """Получение игрока по ID."""
        return self.players.get(player_id)

    def add_news(self, title: str, content: str, category: str = "general") -> None:
        """Добавление новости."""
        self.news.append({
            "title": title,
            "content": content,
            "category": category,
            "week": self.week,
            "matchday": self.matchday,
        })

    # ── Сохранение и загрузка ───────────────────────────────────────
    def save(self, filepath: str = "saves/game_state.json") -> bool:
        """
        Сохранение состояния игры в JSON-файл.
        Возвращает True при успешном сохранении.
        """
        try:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
            data = {
                "current_club_id": self.current_club_id,
                "season": self.season,
                "matchday": self.matchday,
                "week": self.week,
                "clubs": {str(k): v.to_dict() for k, v in self.clubs.items()},
                "players": {str(k): v.to_dict() for k, v in self.players.items()},
                "leagues": {str(k): v.to_dict() for k, v in self.leagues.items()},
                "fixtures": {
                    str(k): [m.to_dict() for m in v]
                    for k, v in self.fixtures.items()
                },
                "news": self.news[-100:],  # Сохраняем последние 100 новостей
                "transfer_offers": self.transfer_offers,
                "history": self.history[-50:],
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[GameState] Ошибка сохранения: {e}")
            return False

    def load(self, filepath: str = "saves/game_state.json") -> bool:
        """
        Загрузка состояния игры из JSON-файла.
        Возвращает True при успешной загрузке.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.current_club_id = data["current_club_id"]
            self.season = data["season"]
            self.matchday = data["matchday"]
            self.week = data["week"]

            self.clubs = {
                int(k): Team.from_dict(v) for k, v in data.get("clubs", {}).items()
            }
            self.players = {
                int(k): Player.from_dict(v) for k, v in data.get("players", {}).items()
            }
            self.leagues = {
                int(k): League.from_dict(v) for k, v in data.get("leagues", {}).items()
            }
            self.fixtures = {
                int(k): [Match.from_dict(m) for m in v]
                for k, v in data.get("fixtures", {}).items()
            }
            self.news = data.get("news", [])
            self.transfer_offers = data.get("transfer_offers", [])
            self.history = data.get("history", [])
            self._is_initialized = True

            return True
        except Exception as e:
            print(f"[GameState] Ошибка загрузки: {e}")
            return False

    def reset(self) -> None:
        """Сброс состояния игры."""
        self.clubs.clear()
        self.players.clear()
        self.leagues.clear()
        self.fixtures.clear()
        self.tournaments.clear()
        self.news.clear()
        self.transfer_offers.clear()
        self.history.clear()
        self.current_club_id = 0
        self.season = 2024
        self.matchday = 0
        self.week = 0
        self._is_initialized = False
