# -*- coding: utf-8 -*-
"""
Симулятор матчей.
Обёртка над C++ MatchEngine с fallback на чистый Python.
Генерация комментариев на русском языке.
"""

import random
import importlib
from typing import Dict, List, Any, Optional, Tuple

try:
    from ..models import (
        Player, Club, Match, MatchEvent, MatchStatus,
        Position, Formation
    )
except (ImportError, ValueError):
    from models import (
        Player, Club, Match, MatchEvent, MatchStatus,
        Position, Formation
    )
from models import Player as _BasePlayer, Club as _BaseClub


class MatchSimulator:
    """
    Симулятор матчей. Обёртка над C++ движком.
    Если C++ модуль недоступен, использует чистый Python.
    """

    # Попытка загрузить C++ модуль
    CPP_AVAILABLE = False
    _cpp_engine = None

    def __init__(self):
        """Инициализация симулятора"""
        try:
            # Попытка импорта C++ модуля (если скомпилирован)
            module = importlib.import_module('game_engine')
            self._cpp_engine = module.MatchEngine()
            MatchSimulator.CPP_AVAILABLE = True
        except (ImportError, AttributeError):
            MatchSimulator.CPP_AVAILABLE = False
            self._cpp_engine = None

        # Константы для симуляции
        self.MATCH_MINUTES = 90
        self.BASE_GOAL_PROBABILITY = 0.025  # Базовая вероятность гола за минуту
        self.HOME_ADVANTAGE = 1.15          # Преимущество дома
        self.MAX_EVENTS_PER_MATCH = 25      # Максimum событий за матч

    def simulate(
        self,
        home_team: Club,
        away_team: Club,
        home_players: List[Player],
        away_players: List[Player],
        tactics: Optional[Dict[str, str]] = None
    ) -> Match:
        """
        Симуляция матча.

        Args:
            home_team: Домашняя команда
            away_team: Гостевая команда
            home_players: Игроки домашней команды
            away_players: Игроки гостевой команды
            tactics: Тактика {"home": formation, "away": formation}

        Returns:
            Объект Match с результатом и событиями
        """
        if tactics is None:
            tactics = {
                'home': home_team.formation,
                'away': away_team.formation
            }

        # Использование C++ движка если доступен
        if self.CPP_AVAILABLE and self._cpp_engine is not None:
            try:
                return self._simulate_cpp(
                    home_team, away_team,
                    home_players, away_players,
                    tactics
                )
            except Exception:
                # Fallback на Python при ошибке C++
                pass

        # Python симуляция
        return self._simulate_python(
            home_team, away_team,
            home_players, away_players,
            tactics
        )

    def _simulate_cpp(
        self,
        home_team: Club,
        away_team: Club,
        home_players: List[Player],
        away_players: List[Player],
        tactics: Dict[str, str]
    ) -> Match:
        """Симуляция через C++ движок"""
        # Подготовка данных для C++
        home_data = {
            'id': home_team.id,
            'name': home_team.name,
            'reputation': home_team.reputation,
            'formation': tactics.get('home', home_team.formation),
            'players': [self._player_to_dict(p) for p in home_players[:11]]
        }
        away_data = {
            'id': away_team.id,
            'name': away_team.name,
            'reputation': away_team.reputation,
            'formation': tactics.get('away', away_team.formation),
            'players': [self._player_to_dict(p) for p in away_players[:11]]
        }

        # Вызов C++ движка
        raw_result = self._cpp_engine.simulate(home_data, away_data)

        # Парсинг результата
        return self._parse_result(raw_result, home_team, away_team)

    def _simulate_python(
        self,
        home_team: Club,
        away_team: Club,
        home_players: List[Player],
        away_players: List[Player],
        tactics: Dict[str, str]
    ) -> Match:
        """
        Симуляция матча на чистом Python.
        Моделирует события по ходу матча.
        """
        match = Match(
            home_team_id=home_team.id,
            home_team_name=home_team.name,
            away_team_id=away_team.id,
            away_team_name=away_team.name,
            status=MatchStatus.IN_PROGRESS,
            venue=f"Стадион {home_team.name}",
        )

        # Расчет сил команд
        home_strength = self._calculate_team_strength(home_players, home_team)
        away_strength = self._calculate_team_strength(away_players, away_team)

        # Преимущество дома
        home_strength *= self.HOME_ADVANTAGE

        # Соотношение сил для распределения вероятностей
        total_strength = home_strength + away_strength
        if total_strength == 0:
            total_strength = 1

        home_attack_ratio = home_strength / total_strength
        away_attack_ratio = away_strength / total_strength

        # Симуляция по минутам
        events: List[MatchEvent] = []
        home_goals = 0
        away_goals = 0
        home_stats = {'shots': 0, 'shots_on_target': 0, 'possession': 50, 'fouls': 0}
        away_stats = {'shots': 0, 'shots_on_target': 0, 'possession': 50, 'fouls': 0}

        for minute in range(1, self.MATCH_MINUTES + 1):
            # Вероятность события в каждой минуте
            if random.random() < self.BASE_GOAL_PROBABILITY:
                # Кто забивает
                if random.random() < home_attack_ratio:
                    # Гол домашней команды
                    scorer = self._select_goal_scorer(home_players)
                    assister = self._select_assist(home_players, scorer)
                    home_goals += 1
                    event = MatchEvent(
                        minute=minute,
                        event_type='goal',
                        player_id=scorer.id,
                        player_name=scorer.full_name,
                        team_id=home_team.id,
                        team_name=home_team.name,
                        description=f"ГОЛ! {scorer.full_name} забивает за {home_team.name}!"
                    )
                    if assister:
                        event.details['assist'] = {
                            'id': assister.id,
                            'name': assister.full_name
                        }
                        event.description += f" (Пас: {assister.full_name})"
                    events.append(event)
                    home_stats['shots_on_target'] += 1
                else:
                    # Гол гостевой команды
                    scorer = self._select_goal_scorer(away_players)
                    assister = self._select_assist(away_players, scorer)
                    away_goals += 1
                    event = MatchEvent(
                        minute=minute,
                        event_type='goal',
                        player_id=scorer.id,
                        player_name=scorer.full_name,
                        team_id=away_team.id,
                        team_name=away_team.name,
                        description=f"ГОЛ! {scorer.full_name} забивает за {away_team.name}!"
                    )
                    if assister:
                        event.details['assist'] = {
                            'id': assister.id,
                            'name': assister.full_name
                        }
                        event.description += f" (Пас: {assister.full_name})"
                    events.append(event)
                    away_stats['shots_on_target'] += 1

            # Удары (без гола)
            if random.random() < 0.08:
                if random.random() < home_attack_ratio:
                    home_stats['shots'] += 1
                else:
                    away_stats['shots'] += 1

            # Карточки
            if random.random() < 0.015:
                player = random.choice(home_players + away_players)
                card_type = 'yellow_card' if random.random() < 0.85 else 'red_card'
                card_name = 'Жёлтая' if card_type == 'yellow_card' else 'Красная'
                team = home_team if player.club_id == home_team.id else away_team
                events.append(MatchEvent(
                    minute=minute,
                    event_type=card_type,
                    player_id=player.id,
                    player_name=player.full_name,
                    team_id=team.id,
                    team_name=team.name,
                    description=f"{card_name} карточка - {player.full_name} ({team.name})"
                ))

            # Замены (60-80 минута)
            if 60 <= minute <= 80 and random.random() < 0.04:
                team = home_team if random.random() < 0.5 else away_team
                players = home_players if team.id == home_team.id else away_players
                if len(players) > 11:
                    out_player = random.choice(players[:11])
                    in_player = random.choice(players[11:])
                    events.append(MatchEvent(
                        minute=minute,
                        event_type='substitution',
                        player_id=in_player.id,
                        player_name=in_player.full_name,
                        team_id=team.id,
                        team_name=team.name,
                        description=f"Замена ({team.name}): {out_player.full_name} → {in_player.full_name}",
                        details={'out': out_player.full_name, 'in': in_player.full_name}
                    ))

            # Травмы (очень редко)
            if random.random() < 0.003:
                player = random.choice(home_players + away_players)
                team = home_team if player.club_id == home_team.id else away_team
                injury_type = random.choice([
                    'Растяжение связок', 'Ушиб', 'Мышечный спазм',
                    'Вывих', 'Трещина'
                ])
                events.append(MatchEvent(
                    minute=minute,
                    event_type='injury',
                    player_id=player.id,
                    player_name=player.full_name,
                    team_id=team.id,
                    team_name=team.name,
                    description=f"Травма! {player.full_name} покидает поле ({injury_type})"
                ))

        # Статистика владения мячом
        possession_base = 50 + (home_strength - away_strength) / total_strength * 15
        home_stats['possession'] = max(30, min(70, int(possession_base)))
        away_stats['possession'] = 100 - home_stats['possession']
        home_stats['shots'] = max(home_stats['shots'], home_goals)
        away_stats['shots'] = max(away_stats['shots'], away_goals)

        # Финализация матча
        match.home_score = home_goals
        match.away_score = away_goals
        match.events = events
        match.home_stats = home_stats
        match.away_stats = away_stats
        match.status = MatchStatus.FINISHED
        match.attendance = self._generate_attendance(home_team, away_team)

        # Генерация комментариев
        match.commentary = self._generate_commentary(events, match)

        return match

    def _calculate_team_strength(self, players: List[Player], team: Club) -> float:
        """Расчет силы команды на основе игроков и атрибутов клуба"""
        if not players:
            return team.reputation / 100.0

        # Средний рейтинг основы (первые 11)
        starters = players[:11] if len(players) >= 11 else players
        avg_rating = sum(p.overall_rating for p in starters) / len(starters)

        # Факторы
        form_factor = sum(p.form for p in starters) / (len(starters) * 100)
        morale_factor = sum(p.morale for p in starters) / (len(starters) * 100)
        fatigue_factor = 1.0 - (sum(p.fatigue for p in starters) / (len(starters) * 100)) * 0.3
        reputation_factor = team.reputation / 100.0

        strength = (
            avg_rating * 0.4 +
            form_factor * 20 +
            morale_factor * 15 +
            fatigue_factor * 15 +
            reputation_factor * 10
        )
        return max(10, strength)

    def _select_goal_scorer(self, players: List[Player]) -> Player:
        """Выбор забившего игрока (на основе позиции и атрибутов)"""
        # Вероятность забить по позициям
        position_weights = {
            'ST': 3.0, 'CF': 2.8, 'CAM': 1.8,
            'LW': 1.5, 'RW': 1.5,
            'CM': 1.0, 'CDM': 0.5,
            'LB': 0.4, 'RB': 0.4, 'CB': 0.6,
            'GK': 0.05
        }

        eligible = [p for p in players[:11]]
        if not eligible:
            eligible = players

        weights = []
        for p in eligible:
            pos_weight = position_weights.get(p.position, 0.5)
            shooting_weight = p.attributes.shooting / 50.0
            overall_weight = p.overall_rating / 50.0
            weights.append(pos_weight * shooting_weight * overall_weight)

        total = sum(weights)
        if total == 0:
            return random.choice(eligible)

        weights = [w / total for w in weights]
        return random.choices(eligible, weights=weights, k=1)[0]

    def _select_assist(self, players: List[Player], scorer: Player) -> Optional[Player]:
        """Выбор игрока, отдавшего пас"""
        eligible = [p for p in players[:11] if p.id != scorer.id]
        if not eligible:
            return None

        # Пасовики имеют больший шанс
        weights = []
        for p in eligible:
            passing_weight = p.attributes.passing / 50.0
            vision_weight = p.attributes.vision / 50.0
            weights.append(passing_weight * vision_weight)

        if random.random() < 0.6:  # 60% шанс что будет пас
            total = sum(weights)
            if total > 0:
                weights = [w / total for w in weights]
                return random.choices(eligible, weights=weights, k=1)[0]
        return None

    def _generate_attendance(self, home_team: Club, away_team: Club) -> int:
        """Генерация посещаемости"""
        base = home_team.attendance_avg
        # Престижные матчи привлекают больше зрителей
        reputation_boost = (home_team.reputation + away_team.reputation) / 200
        noise = random.uniform(0.85, 1.15)
        return int(base * (0.7 + reputation_boost * 0.3) * noise)

    def _generate_commentary(self, events: List[MatchEvent], match: Match) -> List[str]:
        """
        Генерация комментариев к матчу на русском языке.
        """
        commentary = []

        # Начало матча
        commentary.append(
            f"Матч {match.home_team_name} vs {match.away_team_name} начинается!"
        )

        # События по ходу матча
        goal_home = 0
        goal_away = 0

        for event in sorted(events, key=lambda e: e.minute):
            if event.event_type == 'goal':
                if event.team_id == match.home_team_id:
                    goal_home += 1
                else:
                    goal_away += 1

                # Разнообразные комментарии к голам
                goal_commentaries = [
                    f"{event.minute}' - ГОООЛ! {event.player_name} порывает ворота! ({event.team_name})",
                    f"{event.minute}' - МЯЧ! {event.player_name} отличается! ({event.team_name})",
                    f"{event.minute}' - ГОЛ! {event.player_name} отправляет мяч в сетку! ({event.team_name})",
                    f"{event.minute}' - СУПЕРГОЛ! {event.player_name} бьёт без шансов! ({event.team_name})",
                    f"{event.minute}' - ВОТ ЭТО УДАР! {event.player_name} забивает! ({event.team_name})",
                ]
                commentary.append(random.choice(goal_commentaries))

                if 'assist' in event.details:
                    commentary.append(
                        f"        Отличный пас от {event.details['assist']['name']}!"
                    )

                # Обновление счета
                commentary.append(f"        Счёт: {goal_home} - {goal_away}")

            elif event.event_type == 'yellow_card':
                commentary.append(
                    f"{event.minute}' - Жёлтая карточка! {event.player_name} ({event.team_name})"
                )
            elif event.event_type == 'red_card':
                commentary.append(
                    f"{event.minute}' - КРАСНАЯ КАРТОЧКА! {event.player_name} удалён! ({event.team_name})"
                )
                commentary.append(f"        {event.team_name} остаётся в меньшинстве!")
            elif event.event_type == 'substitution':
                if 'out' in event.details and 'in' in event.details:
                    commentary.append(
                        f"{event.minute}' - Замена ({event.team_name}): "
                        f"{event.details['out']} → {event.details['in']}"
                    )
            elif event.event_type == 'injury':
                commentary.append(
                    f"{event.minute}' - ТРАВМА! {event.player_name} не может продолжать! ({event.team_name})"
                )

        # Конец матча
        if match.winner:
            winner_name = match.home_team_name if match.winner == match.home_team_id else match.away_team_name
            commentary.append(
                f"Матч завершён! {match.result}. Победа {winner_name}!"
            )
        else:
            commentary.append(
                f"Матч завершён! Ничья {match.result}."
            )

        # Статистика
        commentary.append("--- Статистика матча ---")
        commentary.append(
            f"Владение мячом: {match.home_stats.get('possession', 50)}% - "
            f"{match.away_stats.get('possession', 50)}%"
        )
        commentary.append(
            f"Удары: {match.home_stats.get('shots', 0)} - "
            f"{match.away_stats.get('shots', 0)}"
        )
        commentary.append(f"Посещаемость: {match.attendance:,}")

        return commentary

    def _parse_result(
        self,
        raw_result: Dict[str, Any],
        home_team: Club,
        away_team: Club
    ) -> Match:
        """
        Парсинг результата от C++ движка.
        """
        match = Match(
            home_team_id=home_team.id,
            home_team_name=home_team.name,
            away_team_id=away_team.id,
            away_team_name=away_team.name,
            home_score=raw_result.get('home_score', 0),
            away_score=raw_result.get('away_score', 0),
            status=MatchStatus.FINISHED,
            home_stats=raw_result.get('home_stats', {}),
            away_stats=raw_result.get('away_stats', {}),
        )

        # Парсинг событий
        for evt_data in raw_result.get('events', []):
            event = MatchEvent(
                minute=evt_data.get('minute', 0),
                event_type=evt_data.get('type', ''),
                player_id=evt_data.get('player_id', ''),
                player_name=evt_data.get('player_name', ''),
                team_id=evt_data.get('team_id', ''),
                team_name=evt_data.get('team_name', ''),
                description=evt_data.get('description', ''),
                details=evt_data.get('details', {}),
            )
            match.events.append(event)

        # Генерация комментариев
        match.commentary = self._generate_commentary(match.events, match)

        return match

    @staticmethod
    def _player_to_dict(player: Player) -> Dict[str, Any]:
        """Конвертация игрока в словарь для C++ модуля"""
        return {
            'id': player.id,
            'name': player.full_name,
            'age': player.age,
            'position': player.position,
            'attributes': player.attributes.to_dict(),
            'overall': player.overall_rating,
            'form': player.form,
            'fatigue': player.fatigue,
            'morale': player.morale,
        }


    def simulate_batch(
        self,
        fixtures: List[Tuple[Club, Club, List[Player], List[Player]]],
        tactics: Optional[Dict[str, Dict[str, str]]] = None
    ) -> List[Match]:
        """
        Пакетная симуляция нескольких матчей (тур).

        Args:
            fixtures: Список кортежей (home_team, away_team, home_players, away_players)
            tactics: Тактика для каждой пары команд

        Returns:
            Список результатов матчей
        """
        results = []
        for i, (home, away, h_players, a_players) in enumerate(fixtures):
            team_tactics = tactics.get(str(i), {}) if tactics else {}
            match = self.simulate(home, away, h_players, a_players, team_tactics)
            results.append(match)
        return results
