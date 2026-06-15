# -*- coding: utf-8 -*-
"""
Сервис тренировок.
Управление тренировочным процессом, развитием игроков.
"""

import random
from typing import Dict, List, Any, Optional

try:
    from ..models import (
        Player, Club, TrainingSession, TrainingFocus, TrainingIntensity
    )
    from ..engine.stats import StatCalculatorWrapper
except ImportError:
    from models import (
        Player, Club, TrainingSession, TrainingFocus, TrainingIntensity
    )
    from engine.stats import StatCalculatorWrapper


class TrainingService:
    """
    Сервис тренировок.
    Управление тренировочным процессом и развитием игроков.
    """

    # Максимальные атрибуты для улучшения
    MAX_ATTRIBUTE = 99
    MIN_ATTRIBUTE = 1

    # Базовые шансы улучшения атрибутов
    BASE_IMPROVEMENT_CHANCE = 0.15
    BASE_IMPROVEMENT_AMOUNT = 1

    # Факторы по возрасту
    AGE_GROWTH_FACTORS = {
        (15, 18): 1.5,   # Очень высокий потенциал роста
        (19, 21): 1.2,   # Высокий рост
        (22, 25): 1.0,   # Нормальный рост
        (26, 28): 0.7,   # Замедление
        (29, 31): 0.4,   # Медленный рост
        (32, 35): 0.2,   # Минимальный рост
        (36, 50): 0.05,  # Практически нет роста
    }

    # Связи атрибутов (какие атрибуты влияют на другие)
    ATTRIBUTE_SYNERGIES = {
        'shooting': ['heading', 'composure'],
        'passing': ['vision', 'dribbling'],
        'defending': ['tackling', 'positioning'],
        'pace': ['stamina', 'dribbling'],
        'physical': ['strength', 'jumping'],
        'dribbling': ['pace', 'flair'],
        'crossing': ['passing', 'vision'],
        'heading': ['jumping', 'physical'],
        'tackling': ['defending', 'positioning'],
        'positioning': ['vision', 'composure'],
        'reflexes': ['diving', 'kicking'],
        'stamina': ['pace', 'work_rate'],
        'composure': ['vision', 'flair'],
        'vision': ['passing', 'composure'],
    }

    def __init__(self, game_state):
        """
        Инициализация сервиса тренировок.

        Args:
            game_state: Объект GameState
        """
        self.game_state = game_state
        self.stats_calculator = StatCalculatorWrapper()

    def set_team_focus(self, club_id: str, focus: str) -> Dict[str, Any]:
        """
        Установка фокуса тренировок для команды.

        Args:
            club_id: ID клуба
            focus: Фокус тренировки

        Returns:
            Результат установки
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        valid_focuses = [getattr(TrainingFocus, f) for f in dir(TrainingFocus) if not f.startswith('_') and f.isupper()]
        if focus not in valid_focuses:
            return {
                'success': False,
                'message': f'Неверный фокус. Допустимые: {", ".join(valid_focuses)}',
            }

        # Сохранение фокуса (в будущем можно хранить в gameState)
        return {
            'success': True,
            'message': f'Фокус тренировок установлен: {focus}',
            'focus': focus,
        }

    def set_individual_focus(
        self,
        player_id: str,
        focus: str
    ) -> Dict[str, Any]:
        """
        Установка индивидуального фокуса для игрока.

        Args:
            player_id: ID игрока
            focus: Фокус тренировки

        Returns:
            Результат
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        valid_focuses = [getattr(TrainingFocus, f) for f in dir(TrainingFocus) if not f.startswith('_') and f.isupper()]
        if focus not in valid_focuses:
            return {
                'success': False,
                'message': f'Неверный фокус. Допустимые: {", ".join(valid_focuses)}',
            }

        player.training_focus = focus

        return {
            'success': True,
            'message': f'Индивидуальный фокус для {player.full_name}: {focus}',
            'player': player.full_name,
            'focus': focus,
        }

    def set_intensity(self, club_id: str, intensity: str) -> Dict[str, Any]:
        """
        Установка интенсивности тренировок.

        Args:
            club_id: ID клуба
            intensity: Интенсивность

        Returns:
            Результат
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        valid_intensities = [getattr(TrainingIntensity, i) for i in dir(TrainingIntensity) if not i.startswith('_') and i.isupper()]
        if intensity not in valid_intensities:
            return {
                'success': False,
                'message': f'Неверная интенсивность. Допустимые: {", ".join(valid_intensities)}',
            }

        return {
            'success': True,
            'message': f'Интенсивность тренировок: {intensity}',
            'intensity': intensity,
        }

    def simulate_week(
        self,
        club_id: str,
        intensity: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Симуляция недели тренировок.

        Args:
            club_id: ID клуба
            intensity: Интенсивность тренировок

        Returns:
            Результаты недели тренировок
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        # Получаем игроков клуба
        players = [
            self.game_state.players.get(pid)
            for pid in club.squad
            if pid in self.game_state.players
        ]
        players = [p for p in players if p is not None]

        if not players:
            return {'success': False, 'message': 'Нет игроков для тренировок'}

        # Интенсивность влияет на результаты
        intensity_factors = {
            'low': {'improvement_mult': 0.5, 'injury_mult': 0.3, 'fatigue_add': 5},
            'medium': {'improvement_mult': 1.0, 'injury_mult': 1.0, 'fatigue_add': 15},
            'high': {'improvement_mult': 1.5, 'injury_mult': 1.8, 'fatigue_add': 25},
            'very_high': {'improvement_mult': 2.0, 'injury_mult': 2.5, 'fatigue_add': 35},
        }
        factors = intensity_factors.get(intensity, intensity_factors['medium'])

        improvements = {}
        injuries = []
        total_fitness_change = 0
        total_morale_change = 0

        for player in players:
            player_improvements = self._train_player(player, factors)
            if player_improvements:
                improvements[player.id] = player_improvements

            # Увеличение усталости
            fatigue_increase = factors['fatigue_add'] * random.uniform(0.8, 1.2)
            player.fatigue = min(100, player.fatigue + fatigue_increase)

            # Риск травмы
            injury_risk = self.stats_calculator.calculate_injury_risk(
                player, intensity, match_load=1
            )
            if random.random() * 100 < injury_risk * 0.1:
                injury = self._apply_training_injury(player)
                if injury:
                    injuries.append(injury)

            # Влияние на настроение
            morale_change = random.uniform(-2, 3)
            if intensity == 'very_high':
                morale_change -= 1  # Слишком интенсивно снижает настроение
            player.morale = max(0, min(100, player.morale + morale_change))
            total_morale_change += morale_change

        # Восстановление fitness (если тренировки помогают)
        fitness_change = random.uniform(-5, 5)
        if intensity == 'low':
            fitness_change = abs(fitness_change)  # Лёгкие тренировки восстанавливают

        for player in players:
            player.fatigue = max(0, player.fatigue - abs(fitness_change))
            total_fitness_change += fitness_change

        # Создание записи о тренировке
        session = TrainingSession(
            week=self.game_state.current_week,
            focus='balanced',
            intensity=intensity,
            team_id=club_id,
            players_trained=[p.id for p in players],
            improvements=improvements,
            injuries_occurred=injuries,
            fitness_change=total_fitness_change / len(players) if players else 0,
            morale_change=total_morale_change / len(players) if players else 0,
        )
        self.game_state.training_sessions.append(session)

        return {
            'success': True,
            'message': f'Тренировочная неделя завершена',
            'players_trained': len(players),
            'improvements': improvements,
            'injuries': injuries,
            'avg_fitness_change': round(total_fitness_change / len(players), 1) if players else 0,
            'avg_morale_change': round(total_morale_change / len(players), 1) if players else 0,
        }

    def _train_player(
        self,
        player: Player,
        intensity_factors: Dict[str, float]
    ) -> Dict[str, int]:
        """
        Тренировка одного игрока.

        Returns:
            Улучшения атрибутов {attribute: change}
        """
        improvements = {}

        # Определяем атрибуты для улучшения на основе фокуса
        target_attrs = self._get_target_attributes(player)

        # Фактор возраста
        age_factor = self._get_age_factor(player.age)

        # Фактор потенциала
        potential_factor = player.potential / 100.0

        for attr in target_attrs:
            # Шанс улучшения
            chance = (
                self.BASE_IMPROVEMENT_CHANCE *
                age_factor *
                potential_factor *
                intensity_factors['improvement_mult']
            )

            # Бонус за перекрывающиеся атрибуты
            synergies = self.ATTRIBUTE_SYNERGIES.get(attr, [])
            synergy_bonus = 0
            for syn_attr in synergies:
                current_val = getattr(player.attributes, syn_attr, 50)
                synergy_bonus += (current_val - 50) / 200  # До +0.25
            chance *= (1 + synergy_bonus)

            if random.random() < chance:
                # Улучшение
                amount = self.BASE_IMPROVEMENT_AMOUNT
                if random.random() < 0.1:  # 10% шанс на большое улучшение
                    amount = 2

                current_val = getattr(player.attributes, attr, 50)
                new_val = min(self.MAX_ATTRIBUTE, current_val + amount)

                if new_val > current_val:
                    setattr(player.attributes, attr, new_val)
                    improvements[attr] = amount

                    # Синергетические улучшения
                    for syn_attr in synergies:
                        if random.random() < 0.3:  # 30% шанс
                            syn_val = getattr(player.attributes, syn_attr, 50)
                            if syn_val < self.MAX_ATTRIBUTE:
                                setattr(player.attributes, syn_attr, syn_val + 1)
                                improvements[f"{syn_attr}_synergy"] = 1

        return improvements

    def _get_target_attributes(self, player: Player) -> List[str]:
        """Определение целевых атрибутов для тренировки"""
        # Если есть индивидуальный фокус
        if player.training_focus:
            focus_map = {
                'attack': ['shooting', 'dribbling', 'vision', 'composure'],
                'defense': ['defending', 'tackling', 'positioning', 'heading'],
                'fitness': ['stamina', 'pace', 'strength', 'jumping'],
                'tactics': ['positioning', 'vision', 'composure', 'work_rate'],
                'shooting': ['shooting', 'composure', 'heading'],
                'passing': ['passing', 'vision', 'dribbling'],
                'heading': ['heading', 'jumping', 'physical'],
                'set_pieces': ['shooting', 'crossing', 'composure'],
                'youth_development': ['pace', 'shooting', 'passing', 'dribbling', 'defending'],
            }
            return focus_map.get(player.training_focus, ['stamina', 'work_rate'])

        # Автоматический выбор по позиции
        position_attrs = {
            'GK': ['reflexes', 'diving', 'kicking', 'positioning'],
            'CB': ['defending', 'heading', 'tackling', 'physical'],
            'LB': ['pace', 'stamina', 'crossing', 'tackling'],
            'RB': ['pace', 'stamina', 'crossing', 'tackling'],
            'CDM': ['defending', 'passing', 'tackling', 'positioning'],
            'CM': ['passing', 'vision', 'stamina', 'dribbling'],
            'CAM': ['vision', 'passing', 'dribbling', 'shooting'],
            'LW': ['pace', 'dribbling', 'crossing', 'shooting'],
            'RW': ['pace', 'dribbling', 'crossing', 'shooting'],
            'ST': ['shooting', 'heading', 'positioning', 'composure'],
            'CF': ['shooting', 'passing', 'vision', 'dribbling'],
        }
        return position_attrs.get(player.position, ['stamina', 'work_rate'])

    def _get_age_factor(self, age: int) -> float:
        """Получение фактора возраста для тренировок"""
        for (min_age, max_age), factor in self.AGE_GROWTH_FACTORS.items():
            if min_age <= age <= max_age:
                return factor
        return 0.05

    def _apply_training_injury(self, player: Player) -> Optional[Dict[str, Any]]:
        """Применение тренировочной травмы"""
        injury_types = [
            ('Растяжение', 1, 2),
            ('Мышечный спазм', 0, 1),
            ('Ушиб', 0, 1),
            ('Надрыв', 1, 3),
            ('Вывих', 2, 4),
        ]

        injury_name, min_weeks, max_weeks = random.choice(injury_types)

        # Снижение шанса серьёзных травм
        if random.random() < 0.7:
            weeks = random.randint(min_weeks, min_weeks, max_weeks)
        else:
            weeks = random.randint(min_weeks, max_weeks)

        player.injury = injury_name
        player.injury_weeks = weeks

        return {
            'player_id': player.id,
            'player_name': player.full_name,
            'injury': injury_name,
            'weeks_out': weeks,
        }

    def get_training_report(self, club_id: str) -> Dict[str, Any]:
        """
        Получение отчёта по тренировкам.

        Returns:
            Отчёт о тренировках
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'error': 'Клуб не найден'}

        # Получаем последнюю тренировочную сессию
        recent_sessions = [
            s for s in self.game_state.training_sessions
            if s.team_id == club_id
        ]
        recent_sessions.sort(key=lambda s: s.week, reverse=True)

        if not recent_sessions:
            return {'message': 'Нет данных о тренировках'}

        last_session = recent_sessions[0]

        # Статистика по игрокам
        players = [
            self.game_state.players.get(pid)
            for pid in club.squad
            if pid in self.game_state.players
        ]
        players = [p for p in players if p is not None]

        player_stats = []
        for p in players:
            fatigue_status = 'low' if p.fatigue < 30 else 'medium' if p.fatigue < 60 else 'high'
            player_stats.append({
                'id': p.id,
                'name': p.full_name,
                'form': round(p.form, 1),
                'fatigue': round(p.fatigue, 1),
                'fatigue_status': fatigue_status,
                'morale': round(p.morale, 1),
                'training_focus': p.training_focus or 'team',
            })

        return {
            'club_id': club_id,
            'club_name': club.name,
            'last_session_week': last_session.week,
            'intensity': last_session.intensity,
            'players_trained': len(last_session.players_trained),
            'total_improvements': sum(
                sum(imp.values()) for imp in last_session.improvements.values()
            ),
            'injuries': last_session.injuries_occurred,
            'player_stats': player_stats,
            'fitness_trend': round(last_session.fitness_change, 1),
            'morale_trend': round(last_session.morale_change, 1),
        }

    def get_player_development(self, player_id: str) -> Dict[str, Any]:
        """
        Получение информации о развитии игрока.

        Returns:
            Данные о развитии
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'error': 'Игрок не найден'}

        # Текущий рейтинг
        current_rating = self.stats_calculator.calculate_rating(player)

        # Потенциал
        potential = self.stats_calculator.calculate_potential(player)

        # История улучшений (из последних сессий)
        recent_improvements = []
        for session in self.game_state.training_sessions[-10:]:
            if player_id in session.improvements:
                recent_improvements.append({
                    'week': session.week,
                    'improvements': session.improvements[player_id],
                })

        # Прогноз развития
        age_factor = self._get_age_factor(player.age)
        development_speed = age_factor * (player.potential / 100)

        return {
            'player_id': player_id,
            'player_name': player.full_name,
            'current_rating': round(current_rating, 1),
            'potential': potential,
            'age': player.age,
            'development_speed': round(development_speed, 2),
            'training_focus': player.training_focus,
            'recent_improvements': recent_improvements,
            'attributes': player.attributes.to_dict(),
            'recommendations': self._get_development_recommendations(player),
        }

    def _get_development_recommendations(self, player: Player) -> List[str]:
        """Рекомендации по развитию игрока"""
        recommendations = []

        if player.age < 21:
            recommendations.append('Молодой игрок - максимальный фокус на развитии')
            if player.training_focus != 'youth_development':
                recommendations.append('Рассмотрите индивидуальную программу')

        if player.age > 30:
            recommendations.append('Снижение физической нагрузки')
            recommendations.append('Фокус на тактические атрибуты')

        attrs = player.attributes.to_dict()
        low_attrs = [k for k, v in attrs.items() if v < 50]
        if low_attrs:
            recommendations.append(f'Слабые атрибуты: {", ".join(low_attrs[:3])}')

        if player.form < 40:
            recommendations.append('Низкая форма - возможно, нужен отдых')

        if player.fatigue > 70:
            recommendations.append('Высокая усталость - снизить нагрузку')

        return recommendations

    def check_injury_risks(self, club_id: str) -> List[Dict[str, Any]]:
        """
        Проверка рисков травм для игроков клуба.

        Returns:
            Список игроков с высоким риском
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return []

        high_risk_players = []
        for pid in club.squad:
            player = self.game_state.players.get(pid)
            if not player:
                continue

            risk = self.stats_calculator.calculate_injury_risk(player)
            if risk > 50:  # Высокий риск
                high_risk_players.append({
                    'player_id': player.id,
                    'name': player.full_name,
                    'injury_risk': round(risk, 1),
                    'fatigue': round(player.fatigue, 1),
                    'age': player.age,
                    'reasons': self._get_injury_risk_reasons(player),
                })

        # Сортировка по риску
        high_risk_players.sort(key=lambda x: x['injury_risk'], reverse=True)

        return high_risk_players

    def _get_injury_risk_reasons(self, player: Player) -> List[str]:
        """Причины высокого риска травмы"""
        reasons = []

        if player.fatigue > 60:
            reasons.append('Высокая усталость')
        if player.age > 30:
            reasons.append('Возраст')
        if player.attributes.physical < 50:
            reasons.append('Низкая физическая подготовка')
        if player.injury:
            reasons.append('Предыдущая травма')

        return reasons
