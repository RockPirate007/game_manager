# -*- coding: utf-8 -*-
"""
ИИ клуба - обёртка над C++ ClubAI.
Выбор состава, трансферные решения, адаптация тактики.
"""

import random
import importlib
from typing import Dict, List, Any, Optional, Tuple

try:
    from ..models import (
        Player, Club, Transfer, Contract, Position, Formation
    )
except ImportError:
    from models import (
        Player, Club, Transfer, Contract, Position, Formation
    )


class ClubAIWrapper:
    """
    Обёртка над C++ ИИ для клуба.
    Если C++ модуль недоступен, использует Python логику.
    """

    CPP_AVAILABLE = False
    _cpp_ai = None

    def __init__(self):
        """Инициализация ИИ клуба"""
        try:
            module = importlib.import_module('game_engine')
            self._cpp_ai = module.ClubAI()
            ClubAIWrapper.CPP_AVAILABLE = True
        except (ImportError, AttributeError):
            ClubAIWrapper.CPP_AVAILABLE = False
            self._cpp_ai = None

        # Веса для оценки игроков
        self.POSITION_WEIGHTS = {
            'GK': {'reflexes': 3, 'diving': 2, 'kicking': 1.5, 'positioning': 2, 'composure': 1},
            'CB': {'defending': 3, 'heading': 2, 'physical': 2, 'tackling': 2.5, 'positioning': 1.5},
            'LB': {'pace': 2, 'crossing': 2, 'defending': 1.5, 'stamina': 2, 'tackling': 1.5},
            'RB': {'pace': 2, 'crossing': 2, 'defending': 1.5, 'stamina': 2, 'tackling': 1.5},
            'CDM': {'defending': 2.5, 'passing': 2, 'physical': 1.5, 'positioning': 2, 'tackling': 2},
            'CM': {'passing': 2.5, 'vision': 2, 'stamina': 1.5, 'dribbling': 1.5, 'composure': 1.5},
            'CAM': {'vision': 3, 'passing': 2.5, 'dribbling': 2, 'shooting': 1.5, 'flair': 2},
            'LW': {'pace': 3, 'dribbling': 2.5, 'crossing': 2, 'shooting': 1.5, 'flair': 2},
            'RW': {'pace': 3, 'dribbling': 2.5, 'crossing': 2, 'shooting': 1.5, 'flair': 2},
            'ST': {'shooting': 3, 'positioning': 2.5, 'heading': 2, 'physical': 1.5, 'composure': 2},
            'CF': {'shooting': 2.5, 'passing': 2, 'positioning': 2, 'dribbling': 1.5, 'vision': 1.5},
        }

    def select_lineup(
        self,
        team: Club,
        players: List[Player],
        formation: Optional[str] = None
    ) -> List[Player]:
        """
        Выбор оптимального состава.

        Args:
            team: Клуб
            players: Все игроки клуба
            formation: Желаемая формация (если None, используется текущая)

        Returns:
            Список из 11 лучших игроков на свои позиции
        """
        if self.CPP_AVAILABLE and self._cpp_ai is not None:
            try:
                team_data = self._club_to_dict(team)
                players_data = [self._player_to_dict(p) for p in players]
                result = self._cpp_ai.select_lineup(team_data, players_data)
                # Восстановление объектов Player из результата
                selected_ids = [p['id'] for p in result]
                return [p for p in players if p.id in selected_ids][:11]
            except Exception:
                pass

        return self._select_lineup_python(team, players, formation)

    def _select_lineup_python(
        self,
        team: Club,
        players: List[Player],
        formation: Optional[str] = None
    ) -> List[Player]:
        """Python логика выбора состава"""
        formation = formation or team.formation

        # Определяем Required позиции для формации
        required_positions = self._get_formation_positions(formation)

        # Доступные игроки (без травмированных)
        available = [p for p in players if p.injury is None or p.injury_weeks == 0]
        if len(available) < 11:
            available = players  # Если мало игроков, берём всех

        selected: List[Player] = []
        used_ids = set()

        for pos_name, count in required_positions.items():
            for _ in range(count):
                # Ищем лучшего игрока на позицию
                candidates = [
                    p for p in available
                    if p.id not in used_ids and self._can_play_position(p, pos_name)
                ]
                if not candidates:
                    # Если нет на позицию, берём лучшего из оставшихся
                    candidates = [p for p in available if p.id not in used_ids]
                if not candidates:
                    break

                # Сортируем по рейтингу на позиции
                candidates.sort(
                    key=lambda p: self._position_rating(p, pos_name),
                    reverse=True
                )
                best = candidates[0]
                selected.append(best)
                used_ids.add(best.id)

        return selected[:11]

    def _get_formation_positions(self, formation: str) -> Dict[str, int]:
        """Получение позиций для формации"""
        formations = {
            '4-4-2': {'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 'CM': 2, 'LW': 1, 'RW': 1, 'ST': 2},
            '4-3-3': {'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 'CM': 3, 'LW': 1, 'RW': 1, 'ST': 1},
            '4-2-3-1': {'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 'CDM': 2, 'CAM': 1, 'LW': 1, 'RW': 1, 'ST': 1},
            '3-5-2': {'GK': 1, 'CB': 3, 'CDM': 2, 'CM': 1, 'LW': 1, 'RW': 1, 'ST': 2},
            '3-4-3': {'GK': 1, 'CB': 3, 'CDM': 2, 'CM': 2, 'LW': 1, 'RW': 1, 'ST': 1},
            '5-3-2': {'GK': 1, 'CB': 3, 'LB': 1, 'RB': 1, 'CM': 3, 'ST': 2},
            '4-1-4-1': {'GK': 1, 'CB': 2, 'LB': 1, 'RB': 1, 'CDM': 1, 'CM': 2, 'LW': 1, 'RW': 1, 'ST': 1},
        }
        return formations.get(formation, formations['4-4-2'])

    def _can_play_position(self, player: Player, position: str) -> bool:
        """Может ли игрок играть на позиции"""
        if player.position == position:
            return True
        if position in player.secondary_positions:
            return True
        # Смежные позиции
        adjacent = {
            'CB': ['CDM', 'LB', 'RB'],
            'LB': ['CB', 'LW', 'CDM'],
            'RB': ['CB', 'RW', 'CDM'],
            'CDM': ['CB', 'CM'],
            'CM': ['CDM', 'CAM'],
            'CAM': ['CM', 'CF', 'LW', 'RW'],
            'LW': ['LB', 'CAM', 'ST', 'CF'],
            'RW': ['RB', 'CAM', 'ST', 'CF'],
            'ST': ['CF', 'LW', 'RW'],
            'CF': ['ST', 'CAM'],
        }
        return position in adjacent.get(player.position, [])

    def _position_rating(self, player: Player, position: str) -> float:
        """Рейтинг игрока на конкретной позиции"""
        weights = self.POSITION_WEIGHTS.get(position, {})
        attrs = player.attributes.to_dict()
        rating = 0
        total_weight = 0
        for attr, weight in weights.items():
            if attr in attrs:
                rating += attrs[attr] * weight
                total_weight += weight

        if total_weight == 0:
            return player.overall_rating

        base = rating / total_weight

        # Модификаторы
        form_mod = (player.form - 50) / 100
        age_mod = 0
        if player.age < 23:
            age_mod = (23 - player.age) * 0.5
        elif player.age > 30:
            age_mod = -(player.age - 30) * 1

        return base + form_mod * 5 + age_mod

    def make_transfer_decision(
        self,
        team: Club,
        players: List[Player],
        market_players: List[Player],
        budget: float
    ) -> Dict[str, Any]:
        """
        Принятие трансферных решений ИИ.

        Args:
            team: Клуб
            players: Текущий состав
            market_players: Игроки на трансферном рынке
            budget: Трансферный бюджет

        Returns:
            Словарь с решениями: покупки, продажи, приоритеты
        """
        if self.CPP_AVAILABLE and self._cpp_ai is not None:
            try:
                team_data = self._club_to_dict(team)
                players_data = [self._player_to_dict(p) for p in players]
                market_data = [self._player_to_dict(p) for p in market_players]
                result = self._cpp_ai.make_transfer_decision(
                    team_data, players_data, market_data, budget
                )
                return result
            except Exception:
                pass

        return self._make_transfer_decision_python(team, players, market_players, budget)

    def _make_transfer_decision_python(
        self,
        team: Club,
        players: List[Player],
        market_players: List[Player],
        budget: float
    ) -> Dict[str, Any]:
        """Python логика трансферных решений"""
        decisions = {
            'buy_targets': [],
            'sell_candidates': [],
            'priorities': [],
            'budget_allocation': budget,
        }

        # Анализ слабых мест
        position_counts = {}
        position_quality = {}
        for p in players:
            pos = p.position
            position_counts[pos] = position_counts.get(pos, 0) + 1
            if pos not in position_quality:
                position_quality[pos] = []
            position_quality[pos].append(p.overall_rating)

        # Определяем дефицитные позиции
        critical_positions = ['GK', 'CB', 'CM', 'ST']
        for pos in critical_positions:
            count = position_counts.get(pos, 0)
            if count < 2:
                decisions['priorities'].append(f"Нужен {pos}")
                # Ищем на рынке
                for mp in market_players:
                    if mp.position == pos and mp.value <= budget * 0.4:
                        decisions['buy_targets'].append({
                            'player_id': mp.id,
                            'name': mp.full_name,
                            'position': pos,
                            'estimated_fee': mp.value,
                            'priority': 'high',
                        })
                        break

        # Ищем молодых талантов (potential > 75, age < 23)
        for mp in market_players:
            if mp.potential > 75 and mp.age < 23 and mp.value <= budget * 0.3:
                decisions['buy_targets'].append({
                    'player_id': mp.id,
                    'name': mp.full_name,
                    'position': mp.position,
                    'estimated_fee': mp.value,
                    'priority': 'medium',
                    'reason': 'Молодой талант',
                })

        # Кандидаты на продажу (старше 30 или с низкой формой)
        for p in players:
            if p.age > 32 and p.overall_rating < 65:
                decisions['sell_candidates'].append({
                    'player_id': p.id,
                    'name': p.full_name,
                    'estimated_value': p.value,
                    'reason': 'Возраст и низкий рейтинг',
                })
            elif p.form < 35 and p.morale < 40:
                decisions['sell_candidates'].append({
                    'player_id': p.id,
                    'name': p.full_name,
                    'estimated_value': p.value,
                    'reason': 'Низкая форма и настроение',
                })

        return decisions

    def adapt_tactics(
        self,
        team: Club,
        players: List[Player],
        opponent: Optional[Club] = None,
        opponent_players: Optional[List[Player]] = None,
        match_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Адаптация тактики на основе соперника и контекста.

        Args:
            team: Наша команда
            players: Наши игроки
            opponent: Команда соперника
            opponent_players: Игроки соперника
            match_context: Контекст матча (счёт, время и т.д.)

        Returns:
            Рекомендации по тактике
        """
        if self.CPP_AVAILABLE and self._cpp_ai is not None:
            try:
                team_data = self._club_to_dict(team)
                players_data = [self._player_to_dict(p) for p in players]
                opp_data = self._club_to_dict(opponent) if opponent else None
                opp_players_data = (
                    [self._player_to_dict(p) for p in opponent_players]
                    if opponent_players else None
                )
                result = self._cpp_ai.adapt_tactics(
                    team_data, players_data, opp_data,
                    opp_players_data, match_context
                )
                return result
            except Exception:
                pass

        return self._adapt_tactics_python(
            team, players, opponent, opponent_players, match_context
        )

    def _adapt_tactics_python(
        self,
        team: Club,
        players: List[Player],
        opponent: Optional[Club] = None,
        opponent_players: Optional[List[Player]] = None,
        match_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Python логика адаптации тактики"""
        recommendations = {
            'formation': team.formation,
            'style': team.style,
            'pressing': 'medium',
            'tempo': 'normal',
            'width': 'normal',
            'instructions': [],
        }

        # Анализ соперника
        if opponent:
            # Если соперник силён,建议 оборонительную тактику
            if opponent.reputation > team.reputation + 15:
                recommendations['style'] = 'defensive'
                recommendations['pressing'] = 'low'
                recommendations['tempo'] = 'slow'
                recommendations['instructions'].append('Глубокая оборона')
                recommendations['instructions'].append('Быстрые контратаки')

            # Если соперник слаб建議 атакующую
            elif opponent.reputation < team.reputation - 15:
                recommendations['style'] = 'attacking'
                recommendations['pressing'] = 'high'
                recommendations['tempo'] = 'fast'
                recommendations['width'] = 'wide'
                recommendations['instructions'].append('Высокий прессинг')
                recommendations['instructions'].append('Широкая игра')

        # Контекст матча
        if match_context:
            score_diff = match_context.get('home_score', 0) - match_context.get('away_score', 0)
            is_home = match_context.get('is_home', True)
            minute = match_context.get('minute', 0)

            # Если проигрываем, нужно атаковать
            if (is_home and score_diff < 0) or (not is_home and score_diff > 0):
                recommendations['style'] = 'attacking'
                recommendations['tempo'] = 'fast'
                recommendations['instructions'].append('Нужно забивать!')

            # Если выигрываем в конце, можно закрыться
            if abs(score_diff) >= 1 and minute > 75:
                recommendations['style'] = 'defensive'
                recommendations['pressing'] = 'low'
                recommendations['instructions'].append('Удержать результат')

        # Проверка усталости игроков
        if players:
            avg_fatigue = sum(p.fatigue for p in players) / len(players)
            if avg_fatigue > 60:
                recommendations['tempo'] = 'slow'
                recommendations['pressing'] = 'low'
                recommendations['instructions'].append('Снизить нагрузку')

        return recommendations

    @staticmethod
    def _club_to_dict(club: Club) -> Dict[str, Any]:
        """Конвертация клуба в словарь для C++ модуля"""
        return {
            'id': club.id,
            'name': club.name,
            'reputation': club.reputation,
            'formation': club.formation,
            'style': club.style,
            'budget': club.budget,
            'balance': club.balance,
            'squad_size': club.squad_size,
        }

    @staticmethod
    def _player_to_dict(player: Player) -> Dict[str, Any]:
        """Конвертация игрока в словарь для C++ модуля"""
        return {
            'id': player.id,
            'name': player.full_name,
            'age': player.age,
            'position': player.position,
            'overall': player.overall_rating,
            'potential': player.potential,
            'value': player.value,
            'form': player.form,
            'fatigue': player.fatigue,
            'injury': player.injury,
            'attributes': player.attributes.to_dict(),
        }

    def simulate_ai_match(
        self,
        ai_team: Club,
        ai_players: List[Player],
        opponent_team: Club,
        opponent_players: List[Player]
    ) -> Dict[str, Any]:
        """
        Симуляция решений ИИ во время матча.

        Returns:
            Решения по заменам, тактике и т.д.
        """
        decisions = {
            'substitutions': [],
            'tactical_changes': [],
            'captain_instruction': None,
        }

        # Простая логика замен
        tired = [p for p in ai_players[:11] if p.fatigue > 70]
        bench = ai_players[11:] if len(ai_players) > 11 else []

        for tired_player in tired[:3]:  # Макс 3 замены
            if bench:
                replacement = bench.pop(0)
                decisions['substitutions'].append({
                    'out': tired_player.id,
                    'in': replacement.id,
                    'reason': 'Усталость',
                })

        # Тактические изменения по ходу матча
        if ai_team.reputation < opponent_team.reputation:
            decisions['tactical_changes'].append({
                'type': 'pressing',
                'value': 'low',
                'reason': 'Сильный соперник',
            })

        return decisions
