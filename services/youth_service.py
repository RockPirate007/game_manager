# -*- coding: utf-8 -*-
"""
Сервис молодёжной академии.
Генерация молодых игроков, развитие, продвижение в основу.
"""

import random
from typing import Dict, List, Any, Optional

try:
    from ..models import Player, Club, YouthPlayer, PlayerAttributes
except ImportError:
    from models import Player, Club, YouthPlayer, PlayerAttributes


class YouthService:
    """
    Сервис молодёжной академии.
    Управление молодыми игроками и их развитием.
    """

    # Константы для генерации молодых игроков
    MIN_AGE = 15
    MAX_AGE = 18
    PROMOTION_AGE = 18
    YOUTH_INTAKE_SIZE = 10  # Количество игроков в наборе

    # Шкала потенциала
    POTENTIAL_RANGES = {
        'world_class': (85, 99),    # 5%
        'top': (75, 84),            # 15%
        'good': (65, 74),           # 30%
        'average': (50, 64),        # 35%
        'low': (30, 49),            # 15%
    }

    def __init__(self, game_state):
        """
        Инициализация сервиса молодёжной академии.

        Args:
            game_state: Объект GameState
        """
        self.game_state = game_state

    def generate_youth_intake(
        self,
        club_id: str,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Генерация нового набора молодых игроков.

        Args:
            club_id: ID клуба
            year: Год набора (если None, текущий год)

        Returns:
            Список новых молодых игроков
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найдён'}

        if year is None:
            year = self.game_state.current_season

        # Качество набора зависит от репутации академии
        academy_quality = self._get_academy_quality(club)

        new_players = []
        for i in range(self.YOUTH_INTAKE_SIZE):
            player = self._generate_youth_player(club, academy_quality, year)
            new_players.append(player)

            # Сохранение в gameState
            self.game_state.players[player.id] = player

            # Создание молодёжной записи
            youth = YouthPlayer(
                player_id=player.id,
                name=player.full_name,
                age=player.age,
                potential=player.potential,
                scout_rating=self._calculate_scout_rating(player),
                development_speed=random.uniform(0.8, 1.2),
            )
            self.game_state.youth_players.append(youth)

            # Добавление в молодёжный состав клуба
            if player.id not in club.youth_squad:
                club.youth_squad.append(player.id)

        return {
            'success': True,
            'message': f'Набор {len(new_players)} молодых игроков',
            'players': [p.to_dict() for p in new_players],
            'academy_quality': academy_quality,
        }

    def _get_academy_quality(self, club: Club) -> float:
        """Определение качества академии"""
        # Зависит от репутации и размера клуба
        base = club.reputation / 100.0

        # Бонус за размер стадиона (крупные клубы)
        if club.stadium_capacity > 50000:
            base += 0.15
        elif club.stadium_capacity > 30000:
            base += 0.1

        # Случайный фактор
        noise = random.uniform(0.85, 1.15)

        return min(1.0, base * noise)

    def _generate_youth_player(
        self,
        club: Club,
        academy_quality: float,
        year: int
    ) -> Player:
        """Генерация одного молодого игрока"""
        age = random.randint(self.MIN_AGE, self.MAX_AGE)

        # Определение потенциала
        potential = self._generate_potential(academy_quality)

        # Определение позиции
        position = random.choice([
            'GK', 'CB', 'LB', 'RB', 'CDM', 'CM', 'CAM',
            'LW', 'RW', 'ST', 'CF'
        ])

        # Генерация атрибутов на основе потенциала и возраста
        attributes = self._generate_attributes(position, age, potential)

        # Имя (генерируется случайно)
        first_name = self._generate_first_name()
        last_name = self._generate_last_name()

        # Рассчитываем стоимость (молодые игроки дешевле)
        base_value = (potential ** 2) * 500
        value = base_value * (1.0 + academy_quality * 0.3)

        player = Player(
            first_name=first_name,
            last_name=last_name,
            age=age,
            nationality=club.country,
            position=position,
            attributes=attributes,
            potential=potential,
            value=round(value, -3),
            wage=round(random.uniform(500, 5000), -2),
            form=random.uniform(50, 70),
            morale=random.uniform(60, 80),
            is_youth=True,
            club_id=club.id,
        )

        return player

    def _generate_potential(self, academy_quality: float) -> int:
        """Генерация потенциала"""
        # Распределение по категориям
        roll = random.random()
        adjusted_roll = roll / max(0.1, academy_quality)  # Лучшая академия = выше шанс

        if adjusted_roll < 0.05:
            return random.randint(*self.POTENTIAL_RANGES['world_class'])
        elif adjusted_roll < 0.20:
            return random.randint(*self.POTENTIAL_RANGES['top'])
        elif adjusted_roll < 0.50:
            return random.randint(*self.POTENTIAL_RANGES['good'])
        elif adjusted_roll < 0.85:
            return random.randint(*self.POTENTIAL_RANGES['average'])
        else:
            return random.randint(*self.POTENTIAL_RANGES['low'])

    def _generate_attributes(
        self,
        position: str,
        age: int,
        potential: int
    ) -> PlayerAttributes:
        """Генерация атрибутов молодого игрока"""
        # Базовые значения на основе позиции
        base_attrs = self._get_position_base(position)

        # Модификатор потенциала (более высокий потенциал = лучшие стартовые атрибуты)
        potential_factor = potential / 100.0

        # Модификатор возраста (младше = хуже стартовые, но больше рост)
        age_factor = 1.0 - (self.MAX_AGE - age) * 0.05

        attrs = {}
        for attr, base_val in base_attrs.items():
            # Генерация значения
            noise = random.uniform(-5, 5)
            val = base_val * potential_factor * age_factor + noise
            attrs[attr] = max(10, min(99, int(val)))

        return PlayerAttributes(**attrs)

    def _get_position_base(self, position: str) -> Dict[str, int]:
        """Базовые атрибуты по позиции"""
        bases = {
            'GK': {
                'reflexes': 50, 'diving': 45, 'kicking': 40,
                'positioning': 45, 'composure': 40,
            },
            'CB': {
                'defending': 50, 'heading': 45, 'physical': 45,
                'tackling': 45, 'positioning': 40,
            },
            'LB': {
                'pace': 50, 'stamina': 50, 'crossing': 40,
                'tackling': 40, 'defending': 40,
            },
            'RB': {
                'pace': 50, 'stamina': 50, 'crossing': 40,
                'tackling': 40, 'defending': 40,
            },
            'CDM': {
                'defending': 50, 'passing': 45, 'tackling': 45,
                'positioning': 45, 'physical': 40,
            },
            'CM': {
                'passing': 50, 'vision': 45, 'stamina': 45,
                'dribbling': 40, 'composure': 40,
            },
            'CAM': {
                'vision': 50, 'passing': 48, 'dribbling': 45,
                'shooting': 40, 'flair': 45,
            },
            'LW': {
                'pace': 50, 'dribbling': 48, 'crossing': 42,
                'shooting': 38, 'flair': 45,
            },
            'RW': {
                'pace': 50, 'dribbling': 48, 'crossing': 42,
                'shooting': 38, 'flair': 45,
            },
            'ST': {
                'shooting': 50, 'positioning': 48, 'heading': 42,
                'physical': 40, 'composure': 42,
            },
            'CF': {
                'shooting': 48, 'passing': 42, 'positioning': 45,
                'dribbling': 40, 'vision': 42,
            },
        }
        return bases.get(position, {
            'pace': 40, 'shooting': 40, 'passing': 40,
            'dribbling': 40, 'defending': 40, 'physical': 40,
        })

    def _generate_first_name(self) -> str:
        """Генерация имени"""
        names = [
            'Александр', 'Дмитрий', 'Максим', 'Сергей', 'Андрей',
            'Алексей', 'Артём', 'Илья', 'Кирилл', 'Михаил',
            'Никита', 'Матвей', 'Роман', 'Егор', 'Арсений',
            'Иван', 'Денис', 'Евгений', 'Тимофей', 'Владислав',
        ]
        return random.choice(names)

    def _generate_last_name(self) -> str:
        """Генерация фамилии"""
        names = [
            'Иванов', 'Петров', 'Сидоров', 'Смирнов', 'Кузнецов',
            'Попов', 'Васильев', 'Соколов', 'Михайлов', 'Новиков',
            'Морозов', 'Волков', 'Алексеев', 'Лебедев', 'Семенов',
            'Егоров', 'Павлов', 'Козлов', 'Степанов', 'Николаев',
        ]
        return random.choice(names)

    def _calculate_scout_rating(self, player: Player) -> float:
        """Рейтинг игрока по оценке скаута"""
        # Комбинация потенциала и текущих атрибутов
        current = player.attributes.overall()
        potential_bonus = (player.potential - current) / 100 * 30

        return min(100, max(0, round(current + potential_bonus, 1)))

    def promote_player(
        self,
        player_id: str,
        club_id: str
    ) -> Dict[str, Any]:
        """
        Продвижение молодого игрока в основной состав.

        Args:
            player_id: ID игрока
            club_id: ID клуба

        Returns:
            Результат продвижения
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        # Проверка возраста
        if player.age < self.PROMOTION_AGE:
            return {
                'success': False,
                'message': f'Игрок слишком молод ({player.age} лет). Нужно {self.PROMOTION_AGE}',
            }

        # Проверка, что уже в основе
        if player.id in club.squad:
            return {'success': False, 'message': 'Игрок уже в основном составе'}

        # Продвижение
        club.squad.append(player.id)
        if player.id in club.youth_squad:
            club.youth_squad.remove(player.id)

        # Обновление данных игрока
        player.is_youth = False
        player.morale = min(100, player.morale + 20)  # Радость от продвижения

        # Обновление молодёжной записи
        for youth in self.game_state.youth_players:
            if youth.player_id == player_id:
                youth.promoted = True
                youth.promotion_date = f"Week {self.game_state.current_week}"
                break

        # Повышение зарплаты
        new_wage = max(player.wage, club.wage_budget * 0.01)
        player.wage = round(new_wage, -2)

        return {
            'success': True,
            'message': f'{player.full_name} продвинут в основной состав!',
            'player': player.to_dict(),
            'new_wage': player.wage,
        }

    def scout_recommendations(
        self,
        club_id: str
    ) -> List[Dict[str, Any]]:
        """
        Рекомендации скаутов по молодым игрокам.

        Returns:
            Список рекомендаций
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return []

        recommendations = []
        for youth in self.game_state.youth_players:
            player = self.game_state.players.get(youth.player_id)
            if not player:
                continue

            # Интересные для рекомендации
            if (youth.potential > 65 and
                    youth.scout_rating > 60 and
                    not youth.promoted and
                    player.club_id == club_id):

                recommendations.append({
                    'player_id': player.id,
                    'name': player.full_name,
                    'age': player.age,
                    'position': player.position,
                    'potential': youth.potential,
                    'scout_rating': round(youth.scout_rating, 1),
                    'notes': youth.notes,
                    'recommendation': self._get_recommendation_text(player, youth),
                })

        # Сортировка по рейтингу скаута
        recommendations.sort(key=lambda x: x['scout_rating'], reverse=True)

        return recommendations[:10]  # Топ-10

    def _get_recommendation_text(
        self,
        player: Player,
        youth: YouthPlayer
    ) -> str:
        """Текст рекомендации"""
        if youth.potential > 80:
            return "Выдающийся талант! Рекомендуется к скорейшему продвижению."
        elif youth.potential > 70:
            return "Очень перспективный игрок. Стоит дать шанс."
        elif youth.potential > 60:
            return "Хороший потенциал. Продолжать развитие."
        else:
            return "Средний потенциал. Нужен дополнительный рост."

    def get_academy_prospects(
        self,
        club_id: str
    ) -> Dict[str, Any]:
        """
        Получение информации о prospects академии.

        Returns:
            Информация о prospects
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'error': 'Клуб не найден'}

        prospects = []
        for youth in self.game_state.youth_players:
            player = self.game_state.players.get(youth.player_id)
            if not player or player.club_id != club_id:
                continue

            prospects.append({
                'player_id': player.id,
                'name': player.full_name,
                'age': player.age,
                'position': player.position,
                'potential': youth.potential,
                'scout_rating': round(youth.scout_rating, 1),
                'development_speed': round(youth.development_speed, 2),
                'promoted': youth.promoted,
                'years_to_promotion': max(0, self.PROMOTION_AGE - player.age),
            })

        # Сортировка по потенциалу
        prospects.sort(key=lambda x: x['potential'], reverse=True)

        # Статистика
        total = len(prospects)
        promoted = sum(1 for p in prospects if p['promoted'])
        avg_potential = (
            sum(p['potential'] for p in prospects) / total if total > 0 else 0
        )

        return {
            'club_id': club_id,
            'club_name': club.name,
            'total_prospects': total,
            'promoted': promoted,
            'avg_potential': round(avg_potential, 1),
            'prospects': prospects,
            'academy_level': self._get_academy_level(club),
        }

    def _get_academy_level(self, club: Club) -> str:
        """Уровень академии"""
        if club.reputation >= 80:
            return 'Элитная'
        elif club.reputation >= 60:
            return 'Хорошая'
        elif club.reputation >= 40:
            return 'Средняя'
        else:
            return 'Базовая'

    def train_young_player(
        self,
        player_id: str,
        focus: str = 'balanced',
        intensity: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Индивидуальная тренировка молодого игрока.

        Args:
            player_id: ID игрока
            focus: Фокус тренировки
            intensity: Интенсивность

        Returns:
            Результаты тренировки
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        if not player.is_youth:
            return {'success': False, 'message': 'Игрок не является молодым'}

        # Множители по интенсивности
        intensity_mult = {
            'low': 0.5,
            'medium': 1.0,
            'high': 1.5,
            'very_high': 2.0,
        }.get(intensity, 1.0)

        # Множитель по возрасту (молодые растут быстрее)
        age_mult = max(0.5, 1.0 - (player.age - 16) * 0.1)

        improvements = {}

        # Определяем целевые атрибуты
        target_attrs = self._get_youth_target_attributes(player, focus)

        for attr in target_attrs:
            current_val = getattr(player.attributes, attr, 50)

            # Шанс улучшения
            chance = 0.2 * intensity_mult * age_mult * (player.potential / 100)

            if random.random() < chance:
                amount = 1
                if random.random() < 0.15:  # 15% шанс на большое улучшение
                    amount = 2

                new_val = min(99, current_val + amount)
                setattr(player.attributes, attr, new_val)
                improvements[attr] = amount

        # Влияние на усталость
        fatigue_add = {'low': 5, 'medium': 10, 'high': 15, 'very_high': 20}.get(intensity, 10)
        player.fatigue = min(100, player.fatigue + fatigue_add)

        # Влияние на настроение
        if improvements:
            player.morale = min(100, player.morale + 2)

        return {
            'success': True,
            'message': f'Тренировка {player.full_name} завершена',
            'improvements': improvements,
            'fatigue': round(player.fatigue, 1),
        }

    def _get_youth_target_attributes(
        self,
        player: Player,
        focus: str
    ) -> List[str]:
        """Целевые атрибуты для молодого игрока"""
        focus_attrs = {
            'attack': ['shooting', 'dribbling', 'vision', 'composure'],
            'defense': ['defending', 'tackling', 'positioning', 'heading'],
            'fitness': ['stamina', 'pace', 'strength', 'jumping'],
            'balanced': ['pace', 'shooting', 'passing', 'dribbling', 'defending'],
            'youth_development': ['pace', 'shooting', 'passing', 'dribbling'],
        }
        return focus_attrs.get(focus, ['pace', 'shooting', 'passing', 'dribbling'])
