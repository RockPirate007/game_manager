# -*- coding: utf-8 -*-
"""
Сервис финансов.
Управление доходами, расходами, FFP соблюдением.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from ..models import Club, Player
except ImportError:
    from models import Club, Player


class FinanceService:
    """
    Сервис финансов клуба.
    Управление доходами, расходами и финансовым здоровьем.
    """

    # Константы
    FFP_LOSS_LIMIT = -30000000  # Лимит убытка по FFP (30 млн)
    WAGE_TO_REVENUE_RATIO = 0.7  # Максимальная доля зарплат в доходах
    TRANSFER_INSTALLMENT_YEARS = 3  # Рассрочка на трансферы

    def __init__(self, game_state):
        """
        Инициализация сервиса финансов.

        Args:
            game_state: Объект GameState
        """
        self.game_state = game_state

    def get_balance(self, club_id: str) -> Dict[str, Any]:
        """
        Получение баланса клуба.

        Returns:
            Детали баланса
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'error': 'Клуб не найден'}

        return {
            'club_id': club_id,
            'club_name': club.name,
            'balance': club.balance,
            'budget': club.budget,
            'wage_budget': club.wage_budget,
            'wage_bill': club.wage_bill,
            'available_for_transfers': club.balance,
            'available_for_wages': club.wage_budget - club.wage_bill,
            'financial_status': self._get_financial_status(club),
        }

    def _get_financial_status(self, club: Club) -> str:
        """Определение финансового статуса"""
        if club.balance > club.budget * 1.5:
            return 'excellent'
        elif club.balance > club.budget:
            return 'good'
        elif club.balance > club.budget * 0.5:
            return 'stable'
        elif club.balance > 0:
            return 'warning'
        else:
            return 'critical'

    def get_income_breakdown(self, club_id: str) -> Dict[str, float]:
        """
        Разбивка доходов клуба.

        Returns:
            Словарь с источниками дохода
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {}

        # Расчет доходов
        ticket_income = self._calculate_ticket_income(club)
        sponsor_income = club.sponsor_deal / 52  # Еженедельный доход от спонсора
        merchandise = self._calculate_merchandise_income(club)
        tv_money = self._calculate_tv_revenue(club)
        prize_money = self._calculate_prize_money(club)

        return {
            'tickets': round(ticket_income, 2),
            'sponsors': round(sponsor_income, 2),
            'merchandise': round(merchandise, 2),
            'tv_rights': round(tv_money, 2),
            'prize_money': round(prize_money, 2),
            'total': round(
                ticket_income + sponsor_income + merchandise + tv_money + prize_money,
                2
            ),
        }

    def _calculate_ticket_income(self, club: Club) -> float:
        """Расчет дохода от билетов"""
        attendance = club.attendance_avg
        price = club.ticket_price
        matches_per_week = 1  # В среднем 1 домашний матч в неделю
        return attendance * price * matches_per_week

    def _calculate_merchandise_income(self, club: Club) -> float:
        """Расчет дохода от мерча"""
        # Зависит от репутации и размера стадиона
        base = club.stadium_capacity * 0.1  # 10% от.capacity
        reputation_factor = club.reputation / 100
        return base * reputation_factor

    def _calculate_tv_revenue(self, club: Club) -> float:
        """Расчет дохода от телевидения"""
        # Базовый пакет + бонусы за результаты
        base = 500000  # Базовый пакет
        performance_bonus = (
            club.season_wins * 50000 +
            club.season_draws * 15000
        )
        reputation_factor = club.reputation / 80
        return (base + performance_bonus) * reputation_factor

    def _calculate_prize_money(self, club: Club) -> float:
        """Расчет призовых"""
        # Зависит от позиции в таблице
        position = club.league_position
        if position == 1:
            return 2000000
        elif position <= 3:
            return 1000000
        elif position <= 6:
            return 500000
        elif position <= 10:
            return 200000
        else:
            return 50000

    def get_expense_breakdown(self, club_id: str) -> Dict[str, float]:
        """
        Разбивка расходов клуба.

        Returns:
            Словарь с статьями расходов
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {}

        wage_expense = club.wage_bill
        transfer_amortization = self._calculate_transfer_amortization(club)
        maintenance = self._calculate_stadium_maintenance(club)
        staff = self._calculate_staff_costs(club)
        travel = self._calculate_travel_costs(club)
        youth = self._calculate_youth_costs(club)

        return {
            'wages': round(wage_expense, 2),
            'transfer_amortization': round(transfer_amortization, 2),
            'stadium_maintenance': round(maintenance, 2),
            'staff': round(staff, 2),
            'travel': round(travel, 2),
            'youth_academy': round(youth, 2),
            'total': round(
                wage_expense + transfer_amortization + maintenance + staff + travel + youth,
                2
            ),
        }

    def _calculate_transfer_amortization(self, club: Club) -> float:
        """Амортизация трансферов"""
        # Стоимость трансферов делится на срок контракта
        total_amortization = 0
        for transfer in self.game_state.transfers:
            if (transfer.to_club_id == club.id and
                    transfer.status == 'completed' and
                    transfer.fee > 0):
                # Амортизация в неделю
                weekly = transfer.fee / (transfer.contract_years * 52)
                total_amortization += weekly
        return total_amortization

    def _calculate_stadium_maintenance(self, club: Club) -> float:
        """Расходы на содержание стадиона"""
        return club.stadium_capacity * 0.5  # 0.5 за место в неделю

    def _calculate_staff_costs(self, club: Club) -> float:
        """Расходы на персонал"""
        # Тренерский штат + медицинский + административный
        base = 200000
        reputation_factor = club.reputation / 50
        return base * reputation_factor

    def _calculate_travel_costs(self, club: Club) -> float:
        """Транспортные расходы"""
        # В среднем 1 выезд в неделю
        return 50000 + (club.reputation * 500)

    def _calculate_youth_costs(self, club: Club) -> float:
        """Расходы на академию"""
        youth_count = len(club.youth_squad)
        return youth_count * 5000  # 5000 за молодого игрока в неделю

    def calculate_revenue(self, club_id: str) -> Dict[str, Any]:
        """
        Полный расчет доходов俱乐部.

        Returns:
            Прогноз доходов
        """
        income = self.get_income_breakdown(club_id)
        expenses = self.get_expense_breakdown(club_id)

        net = income['total'] - expenses['total']

        return {
            'income': income,
            'expenses': expenses,
            'net_weekly': round(net, 2),
            'net_annual': round(net * 52, 2),
            'projected_balance_next_season': round(
                self.game_state.clubs[club_id].balance + net * 52,
                2
            ) if club_id in self.game_state.clubs else 0,
        }

    def pay_wages(self, club_id: str) -> Dict[str, Any]:
        """
        Выплата зарплат.

        Returns:
            Результат выплаты
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        wage_bill = club.wage_bill

        if wage_bill > club.balance:
            return {
                'success': False,
                'message': f'Недостаточно средств для выплаты зарплат ({wage_bill:,.0f})',
                'shortfall': wage_bill - club.balance,
            }

        club.balance -= wage_bill

        return {
            'success': True,
            'message': f'Зарплата выплачена: {wage_bill:,.0f}',
            'amount': wage_bill,
            'new_balance': club.balance,
        }

    def pay_transfer(
        self,
        club_id: str,
        amount: float,
        installment: bool = True
    ) -> Dict[str, Any]:
        """
        Оплата трансфера.

        Args:
            club_id: ID клуба
            amount: Сумма
            installment: Рассрочка на 3 года

        Returns:
            Результат оплаты
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        if installment:
            # Первая часть сразу
            initial_payment = amount / self.TRANSFER_INSTALLMENT_YEARS
            if initial_payment > club.balance:
                return {
                    'success': False,
                    'message': f'Недостаточно средств (первый взнос: {initial_payment:,.0f})',
                }
            club.balance -= initial_payment
            return {
                'success': True,
                'message': f'Оплачен первый взнос: {initial_payment:,.0f} (из {amount:,.0f})',
                'initial_payment': initial_payment,
                'remaining': amount - initial_payment,
                'installments': self.TRANSFER_INSTALLMENT_YEARS - 1,
            }
        else:
            # Полная оплата
            if amount > club.balance:
                return {
                    'success': False,
                    'message': f'Недостаточно средств ({amount:,.0f})',
                }
            club.balance -= amount
            return {
                'success': True,
                'message': f'Трансфер оплачен: {amount:,.0f}',
                'amount': amount,
                'new_balance': club.balance,
            }

    def receive_sponsorship(self, club_id: str) -> Dict[str, Any]:
        """
        Получение спонсорских выплат.

        Returns:
            Результат получения
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        amount = club.sponsor_deal / 52  # Еженедельная выплата
        club.balance += amount

        return {
            'success': True,
            'message': f'Спонсорская выплата: {amount:,.0f}',
            'amount': amount,
            'new_balance': club.balance,
        }

    def sell_player(
        self,
        club_id: str,
        player_id: str,
        sale_price: float
    ) -> Dict[str, Any]:
        """
        Зачисление средств от продажи игрока.

        Args:
            club_id: ID клуба
            player_id: ID игрока
            sale_price: Цена продажи

        Returns:
            Результат
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        club.balance += sale_price

        # Бонус за молодого игрока (FFP)
        player = self.game_state.players.get(player_id)
        if player and player.age < 23:
            # Бонус за本土ного игрока
            bonus = sale_price * 0.1
            club.balance += bonus

        return {
            'success': True,
            'message': f'Зачислено {sale_price:,.0f} от продажи',
            'amount': sale_price,
            'new_balance': club.balance,
        }

    def get_financial_health(self, club_id: str) -> Dict[str, Any]:
        """
        Оценка финансового здоровья клуба.

        Returns:
            Показатели финансового здоровья
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'error': 'Клуб не найден'}

        income = self.get_income_breakdown(club_id)
        expenses = self.get_expense_breakdown(club_id)

        # Ключевые метрики
        revenue = income['total']
        total_expenses = expenses['total']
        wage_ratio = club.wage_bill / revenue if revenue > 0 else 1
        net_profit = revenue - total_expenses

        # Оценка по шкале
        if wage_ratio <= 0.5:
            wage_health = 'excellent'
        elif wage_ratio <= 0.7:
            wage_health = 'good'
        elif wage_ratio <= 0.85:
            wage_health = 'warning'
        else:
            wage_health = 'critical'

        # FFP проверка
        ffp_status = self.check_ffp_compliance(club_id)

        return {
            'club_id': club_id,
            'club_name': club.name,
            'balance': club.balance,
            'revenue_weekly': round(revenue, 2),
            'expenses_weekly': round(total_expenses, 2),
            'net_profit_weekly': round(net_profit, 2),
            'wage_to_revenue_ratio': round(wage_ratio, 3),
            'wage_health': wage_health,
            'ffp_status': ffp_status,
            'overall_health': self._calculate_overall_health(
                wage_ratio, net_profit, club.balance, ffp_status
            ),
        }

    def _calculate_overall_health(
        self,
        wage_ratio: float,
        net_profit: float,
        balance: float,
        ffp_status: Dict[str, Any]
    ) -> str:
        """Общая оценка финансового здоровья"""
        score = 0

        # Баланс
        if balance > 10000000:
            score += 3
        elif balance > 5000000:
            score += 2
        elif balance > 0:
            score += 1

        # Прибыльность
        if net_profit > 0:
            score += 2
        elif net_profit > -500000:
            score += 1

        # Зарплатная нагрузка
        if wage_ratio < 0.6:
            score += 3
        elif wage_ratio < 0.75:
            score += 2
        elif wage_ratio < 0.9:
            score += 1

        # FFP
        if ffp_status.get('compliant', False):
            score += 2

        if score >= 8:
            return 'excellent'
        elif score >= 6:
            return 'good'
        elif score >= 4:
            return 'stable'
        elif score >= 2:
            return 'warning'
        else:
            return 'critical'

    def check_ffp_compliance(self, club_id: str) -> Dict[str, Any]:
        """
        Проверка соответствия FFP (Financial Fair Play).

        Returns:
            Статус соответствия FFP
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'compliant': False, 'error': 'Клуб не найден'}

        # Расчет убытка за сезон
        income = self.get_income_breakdown(club_id)
        expenses = self.get_expense_breakdown(club_id)
        annual_loss = (income['total'] - expenses['total']) * 52

        compliant = annual_loss >= self.FFP_LOSS_LIMIT

        return {
            'compliant': compliant,
            'annual_profit_loss': round(annual_loss, 2),
            'ffp_limit': self.FFP_LOSS_LIMIT,
            'remaining_capacity': round(annual_loss - self.FFP_LOSS_LIMIT, 2),
            'warning': (
                None if compliant
                else f'Убыток {abs(annual_loss):,.0f} превышает лимит FFP {abs(self.FFP_LOSS_LIMIT):,.0f}'
            ),
        }

    def project_season(self, club_id: str) -> Dict[str, Any]:
        """
        Прогноз финансов на сезон.

        Returns:
            Финансовый прогноз
        """
        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'error': 'Клуб не найден'}

        weeks_remaining = 52 - self.game_state.current_week

        income = self.get_income_breakdown(club_id)
        expenses = self.get_expense_breakdown(club_id)

        weekly_net = income['total'] - expenses['total']
        projected_annual = weekly_net * 52

        return {
            'current_balance': club.balance,
            'projected_end_balance': round(club.balance + weekly_net * weeks_remaining, 2),
            'projected_annual_profit_loss': round(projected_annual, 2),
            'weeks_remaining': weeks_remaining,
            'income_projection': round(income['total'] * weeks_remaining, 2),
            'expense_projection': round(expenses['total'] * weeks_remaining, 2),
            'recommendations': self._generate_financial_recommendations(club, weekly_net),
        }

    def _generate_financial_recommendations(
        self,
        club: Club,
        weekly_net: float
    ) -> List[str]:
        """Генерация финансовых рекомендаций"""
        recommendations = []

        if weekly_net < 0:
            recommendations.append('Расходы превышают доходы. Рассмотрите продажу игроков.')

        wage_ratio = club.wage_bill / (club.sponsor_deal / 52) if club.sponsor_deal > 0 else 1
        if wage_ratio > 0.7:
            recommendations.append('Зарплатная нагрузка слишком высокая. Обновите контракты.')

        if club.balance < club.budget * 0.3:
            recommendations.append('Низкий баланс. Избегайте крупных трансферов.')

        if club.reputation < 40:
            recommendations.append('Низкая репутация. Инвестируйте в маркетинг.')

        return recommendations
