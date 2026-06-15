# -*- coding: utf-8 -*-
"""
Сервис контрактов.
Управление контрактами игроков, переговоры, расторжение.
"""

import random
from typing import Dict, List, Any, Optional

try:
    from ..models import Player, Club, Contract, ContractStatus
except ImportError:
    from models import Player, Club, Contract, ContractStatus


class ContractService:
    """
    Сервис контрактов.
    Управление контрактами игроков.
    """

    # Константы
    MIN_WAGE = 500           # Минимальная зарплата
    MAX_WAGE = 500000        # Максимальная зарплата
    MIN_CONTRACT_YEARS = 1
    MAX_CONTRACT_YEARS = 7
    RELEASE_CLAUSE_MIN = 1000000

    # Факторы влияния на зарплатные требования
    AGE_WAGE_FACTORS = {
        (15, 18): 0.3,   # Молодые - дешевле
        (19, 21): 0.6,
        (22, 25): 1.0,   # Пик
        (26, 28): 1.1,
        (29, 31): 1.0,
        (32, 34): 0.8,
        (35, 50): 0.5,   # Старшие - дешевле
    }

    def __init__(self, game_state):
        """
        Инициализация сервиса контрактов.

        Args:
            game_state: Объект GameState
        """
        self.game_state = game_state

    def offer_contract(
        self,
        player_id: str,
        club_id: str,
        wage: float,
        years: int,
        release_clause: Optional[float] = None,
        signing_fee: float = 0,
        bonus_goals: float = 0,
        bonus_assists: float = 0,
    ) -> Dict[str, Any]:
        """
        Предложение контракта игроку.

        Args:
            player_id: ID игрока
            club_id: ID клуба
            wage: Еженедельная зарплата
            years: Срок контракта (лет)
            release_clause: Откупная сумма
            signing_fee: Подписной бонус
            bonus_goals: Бонус за голы
            bonus_assists: Бонус за голевые передачи

        Returns:
            Результат переговоров
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        # Валидация параметров
        if wage < self.MIN_WAGE:
            return {'success': False, 'message': f'Минимальная зарплата: {self.MIN_WAGE}'}
        if wage > self.MAX_WAGE:
            return {'success': False, 'message': f'Максимальная зарплата: {self.MAX_WAGE}'}
        if years < self.MIN_CONTRACT_YEARS or years > self.MAX_CONTRACT_YEARS:
            return {
                'success': False,
                'message': f'Срок контракта: {self.MIN_CONTRACT_YEARS}-{self.MAX_CONTRACT_YEARS} лет',
            }

        # Проверка бюджета
        annual_wage_cost = wage * 52
        if annual_wage_cost > club.wage_budget * 0.15:
            return {
                'success': False,
                'message': 'Зарплата превышает допустимую долю бюджета',
            }

        # Расчет требований игрока
        demands = self._calculate_player_demands(player, club)

        # Оценка предложения
        evaluation = self._evaluate_offer(
            wage, years, release_clause, signing_fee,
            bonus_goals, bonus_assists, demands
        )

        if evaluation['accepted']:
            # Создание контракта
            contract = Contract(
                player_id=player_id,
                club_id=club_id,
                wage=wage,
                duration_years=years,
                release_clause=release_clause,
                bonus_goals=bonus_goals,
                bonus_assists=bonus_assists,
                signing_fee=signing_fee,
                status=ContractStatus.ACTIVE,
            )
            self.game_state.contracts[contract.id] = contract

            # Обновление данных игрока
            old_club_id = player.club_id
            player.club_id = club_id
            player.wage = wage
            player.contract_id = contract.id

            # Обновление составов
            if old_club_id and old_club_id in self.game_state.clubs:
                old_club = self.game_state.clubs[old_club_id]
                if player.id in old_club.squad:
                    old_club.squad.remove(player.id)
                old_club.wage_bill = max(0, old_club.wage_bill - player.wage)

            if player.id not in club.squad:
                club.squad.append(player.id)
            club.wage_bill += wage

            # Подписной бонус
            if signing_fee > 0:
                club.balance -= signing_fee

            return {
                'success': True,
                'message': f'{player.full_name} подписал контракт на {years} лет!',
                'contract': contract.to_dict(),
                'signing_fee': signing_fee,
            }
        else:
            return {
                'success': False,
                'message': f'{player.full_name} отклонил предложение',
                'reasons': evaluation['reasons'],
                'demands': demands,
            }

    def _calculate_player_demands(
        self,
        player: Player,
        club: Club
    ) -> Dict[str, Any]:
        """Расчет требований игрока"""
        # Базовая зарплата на основе рейтинга
        rating = player.overall_rating
        base_wage = (rating ** 2.5) * 5

        # Модификатор возраста
        age_factor = 1.0
        for (min_age, max_age), factor in self.AGE_WAGE_FACTORS.items():
            if min_age <= player.age <= max_age:
                age_factor = factor
                break

        # Модификатор репутации клуба
        reputation_factor = club.reputation / 80.0

        # Модификатор формы
        form_factor = 0.8 + (player.form / 100) * 0.4

        # Требуемая зарплата
        demanded_wage = base_wage * age_factor * reputation_factor * form_factor

        # Свободные агенты требуют больше
        if not player.club_id:
            demanded_wage *= 1.3

        # Требования к контракту
        desired_years = 4 if player.age < 25 else 3 if player.age < 30 else 2

        # Требование откупной
        release_clause = None
        if player.value > 10000000:
            release_clause = player.value * 1.5

        return {
            'wage': round(max(self.MIN_WAGE, demanded_wage), -2),
            'years': desired_years,
            'release_clause': release_clause,
            'signing_fee': round(demanded_wage * 26, -2),  # Полгода зарплаты
        }

    def _evaluate_offer(
        self,
        wage: float,
        years: int,
        release_clause: Optional[float],
        signing_fee: float,
        bonus_goals: float,
        bonus_assists: float,
        demands: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Оценка предложения игроком"""
        reasons = []
        score = 0

        # Оценка зарплаты
        demanded_wage = demands['wage']
        wage_ratio = wage / demanded_wage if demanded_wage > 0 else 0

        if wage_ratio >= 1.2:
            score += 30
            reasons.append('Отличная зарплата')
        elif wage_ratio >= 1.0:
            score += 20
            reasons.append('Хорошая зарплата')
        elif wage_ratio >= 0.8:
            score += 10
            reasons.append('Зарплата ниже ожиданий')
        else:
            score -= 10
            reasons.append('Зарплата слишком низкая')

        # Оценка срока
        desired_years = demands['years']
        if years >= desired_years:
            score += 15
            reasons.append('Хороший срок контракта')
        elif years >= desired_years - 1:
            score += 5
        else:
            score -= 5
            reasons.append('Слишком короткий контракт')

        # Оценка подписного бонуса
        if signing_fee >= demands['signing_fee']:
            score += 15
            reasons.append('Щедрый подписной бонус')
        elif signing_fee > 0:
            score += 5

        # Оценка бонусов
        if bonus_goals > 0:
            score += 5
        if bonus_assists > 0:
            score += 5

        # Откупная сумма
        if release_clause and demands.get('release_clause'):
            if release_clause <= demands['release_clause']:
                score += 10
                reasons.append('Приемлемая откупная')
            else:
                score -= 5

        # Случайный фактор (игрок может быть непредсказуем)
        random_factor = random.uniform(-10, 10)
        score += random_factor

        accepted = score >= 30

        return {
            'accepted': accepted,
            'score': score,
            'reasons': reasons,
        }

    def renew_contract(
        self,
        player_id: str,
        new_wage: Optional[float] = None,
        new_years: Optional[int] = None,
        new_release_clause: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Продление контракта.

        Args:
            player_id: ID игрока
            new_wage: Новая зарплата
            new_years: Новый срок
            new_release_clause: Новая откупная

        Returns:
            Результат продления
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        # Поиск текущего контракта
        current_contract = None
        for contract in self.game_state.contracts.values():
            if contract.player_id == player_id:
                current_contract = contract
                break

        if not current_contract:
            return {'success': False, 'message': 'Контракт не найден'}

        if current_contract.club_id != player.club_id:
            return {'success': False, 'message': 'Контракт принадлежит другому клубу'}

        club = self.game_state.clubs.get(player.club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        # Обновление параметров
        if new_wage is not None:
            current_contract.wage = new_wage
            player.wage = new_wage
            # Пересчет зарплатной ведомости
            club.wage_bill = sum(
                self.game_state.players[pid].wage
                for pid in club.squad
                if pid in self.game_state.players
            )

        if new_years is not None:
            current_contract.duration_years = new_years

        if new_release_clause is not None:
            current_contract.release_clause = new_release_clause

        current_contract.status = ContractStatus.ACTIVE

        return {
            'success': True,
            'message': f'Контракт {player.full_name} продлён',
            'contract': current_contract.to_dict(),
        }

    def terminate_contract(
        self,
        player_id: str,
        mutual: bool = False
    ) -> Dict[str, Any]:
        """
        Расторжение контракта.

        Args:
            player_id: ID игрока
            mutual: По обоюдному согласию

        Returns:
            Результат расторжения
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        # Поиск контракта
        contract_toTerminate = None
        contract_id = None
        for cid, contract in self.game_state.contracts.items():
            if contract.player_id == player_id:
                contract_toTerminate = contract
                contract_id = cid
                break

        if not contract_toTerminate:
            return {'success': False, 'message': 'Контракт не найден'}

        club = self.game_state.clubs.get(contract_toTerminate.club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        # Компенсация
        compensation = 0
        if not mutual:
            # Компенсация за оставшийся срок
            remaining_weeks = contract_toTerminate.duration_years * 52
            compensation = contract_toTerminate.wage * remaining_weeks * 0.5

            if compensation > club.balance:
                return {
                    'success': False,
                    'message': f'Недостаточно средств для компенсации ({compensation:,.0f})',
                }

            club.balance -= compensation

        # Обновление контракта
        contract_toTerminate.status = ContractStatus.TERMINATED

        # Обновление игрока
        player.club_id = None
        player.contract_id = None
        player.wage = 0

        # Обновление состава
        if player.id in club.squad:
            club.squad.remove(player.id)
        club.wage_bill = max(0, club.wage_bill - contract_toTerminate.wage)

        return {
            'success': True,
            'message': f'Контракт {player.full_name} расторгнут',
            'compensation': compensation,
            'mutual': mutual,
        }

    def get_contract_info(self, player_id: str) -> Dict[str, Any]:
        """
        Получение информации о контракте.

        Returns:
            Детали контракта
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'error': 'Игрок не найден'}

        contract = None
        for c in self.game_state.contracts.values():
            if c.player_id == player_id:
                contract = c
                break

        if not contract:
            return {
                'player_id': player_id,
                'player_name': player.full_name,
                'status': 'free_agent',
                'club': None,
            }

        club = self.game_state.clubs.get(contract.club_id)

        return {
            'player_id': player_id,
            'player_name': player.full_name,
            'contract_id': contract.id,
            'club_id': contract.club_id,
            'club_name': club.name if club else None,
            'wage': contract.wage,
            'wage_annual': contract.wage * 52,
            'duration_years': contract.duration_years,
            'release_clause': contract.release_clause,
            'bonus_goals': contract.bonus_goals,
            'bonus_assists': contract.bonus_assists,
            'signing_fee': contract.signing_fee,
            'status': contract.status,
            'is_expiring_soon': contract.status == ContractStatus.EXPIRING,
        }

    def check_expiring_contracts(
        self,
        club_id: Optional[str] = None,
        weeks_threshold: int = 26
    ) -> List[Dict[str, Any]]:
        """
        Проверка контрактов, истекающих в ближайшее время.

        Args:
            club_id: Фильтр по клубу
            weeks_threshold: Порог в неделях

        Returns:
            Список истекающих контрактов
        """
        expiring = []

        for contract in self.game_state.contracts.values():
            if contract.status == ContractStatus.TERMINATED:
                continue

            if club_id and contract.club_id != club_id:
                continue

            player = self.game_state.players.get(contract.player_id)
            if not player:
                continue

            # Проверка, истекает ли контракт
            # (В упрощенной модели считаем, что контракт истекает если осталось < порога)
            remaining_weeks = contract.duration_years * 52 - self.game_state.current_week
            if remaining_weeks <= weeks_threshold and remaining_weeks > 0:
                expiring.append({
                    'player_id': player.id,
                    'player_name': player.full_name,
                    'club_id': contract.club_id,
                    'club_name': self.game_state.clubs[contract.club_id].name
                    if contract.club_id in self.game_state.clubs else None,
                    'wage': contract.wage,
                    'remaining_weeks': remaining_weeks,
                    'value': player.value,
                    'status': 'expiring',
                })
                contract.status = ContractStatus.EXPIRING

        return expiring

    def get_club_wage_bill(self, club_id: str) -> Dict[str, Any]:
        """
        Получение зарплатной ведомости клуба.

        Returns:
            Детали зарплатной ведомости
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'error': 'Клуб не найден'}

        wages = []
        total_weekly = 0

        for player_id in club.squad:
            player = self.game_state.players.get(player_id)
            if not player:
                continue

            wages.append({
                'player_id': player.id,
                'name': player.full_name,
                'wage_weekly': player.wage,
                'wage_annual': player.wage * 52,
                'position': player.position,
                'age': player.age,
            })
            total_weekly += player.wage

        wages.sort(key=lambda x: x['wage_weekly'], reverse=True)

        return {
            'club_id': club_id,
            'club_name': club.name,
            'total_weekly': round(total_weekly, 2),
            'total_annual': round(total_weekly * 52, 2),
            'wage_budget': club.wage_budget,
            'budget_usage': round(total_weekly / club.wage_budget * 100, 1)
            if club.wage_budget > 0 else 0,
            'players': wages,
            'count': len(wages),
        }
