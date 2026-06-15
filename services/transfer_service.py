# -*- coding: utf-8 -*-
"""
Сервис трансферов.
Поиск игроков, подача заявок, переговоры, завершение трансферов.
"""

import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    from ..models import Player, Club, Transfer, TransferStatus, Contract
except ImportError:
    from models import Player, Club, Transfer, TransferStatus, Contract


class TransferService:
    """
    Сервис трансферов.
    Управление трансферной деятельностью клуба.
    """

    def __init__(self, game_state):
        """
        Инициализация сервиса.

        Args:
            game_state: Объект GameState с данными игры
        """
        self.game_state = game_state
        self.market_inflation = 1.0  # Инфляция рынка
        self.bidding_war_chance = 0.15  # Шанс торговой войны

    def search_players(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Поиск игроков на трансферном рынке.

        Args:
            filters: Фильтры поиска:
                - position: позиция
                - min_age/max_age: возраст
                - min_rating/max_rating: рейтинг
                - max_price: максимальная цена
                - nationality: национальность
                - club_id: текущий клуб
                - free_agents_only: только свободные агенты

        Returns:
            Список найденных игроков
        """
        if filters is None:
            filters = {}

        results = []
        for player in self.game_state.players.values():
            # Проверка фильтров
            if not self._matches_filters(player, filters):
                continue

            # Проверка, что игрок доступен для трансфера
            if not self._is_available_for_transfer(player):
                continue

            # Расчет рыночной цены
            estimated_fee = self._estimate_transfer_fee(player)

            results.append({
                'player': player.to_dict(),
                'estimated_fee': estimated_fee,
                'contract_status': self._get_contract_status(player),
                'wage_demands': self._estimate_wage_demands(player),
            })

        # Сортировка по рейтингу
        results.sort(
            key=lambda x: x['player'].get('form', 50),
            reverse=True
        )

        return results

    def _matches_filters(self, player: Player, filters: Dict[str, Any]) -> bool:
        """Проверка соответствия игрока фильтрам"""
        if 'position' and player.position != filters['position']:
            if player.position not in player.secondary_positions:
                return False

        if 'min_age' in filters and player.age < filters['min_age']:
            return False
        if 'max_age' in filters and player.age > filters['max_age']:
            return False

        if 'min_rating' in filters and player.overall_rating < filters['min_rating']:
            return False
        if 'max_rating' in filters and player.overall_rating > filters['max_rating']:
            return False

        if 'max_price' in filters and player.value > filters['max_price']:
            return False

        if 'nationality' in filters and player.nationality != filters['nationality']:
            return False

        if 'free_agents_only' in filters and filters['free_agents_only']:
            if player.club_id:
                return False

        return True

    def _is_available_for_transfer(self, player: Player) -> bool:
        """Проверка доступности игрока для трансфера"""
        # Свободный агент всегда доступен
        if not player.club_id:
            return True

        # Проверка контракта
        contract = self._get_player_contract(player)
        if contract:
            if contract.release_clause and contract.release_clause > 0:
                return True
            # Контракт истекает - можно купить дешевле
            if contract.status == ContractStatus.EXPIRING:
                return True

        # Игрок не в списке на продажу - только за высокую цену
        return True

    def _get_player_contract(self, player: Player) -> Optional[Contract]:
        """Получение контракта игрока"""
        for contract in self.game_state.contracts.values():
            if contract.player_id == player.id:
                return contract
        return None

    def _estimate_transfer_fee(self, player: Player) -> float:
        """Оценка трансферной стоимости"""
        base_value = player.value

        # Модификатор контракта
        contract = self._get_player_contract(player)
        if contract:
            if contract.release_clause:
                return contract.release_clause * self.market_inflation
            if contract.status == ContractStatus.EXPIRING:
                base_value *= 0.5  # Дешевле если контракт истекает

        # Модификатор инфляции
        return base_value * self.market_inflation

    def _get_contract_status(self, player: Player) -> str:
        """Получение статуса контракта"""
        contract = self._get_player_contract(player)
        if not contract:
            return "free_agent"
        return contract.status

    def _estimate_wage_demands(self, player: Player) -> float:
        """Оценка зарплатных требований"""
        base_wage = player.wage

        # Если игрок свободный агент, требования выше
        if not player.club_id:
            base_wage *= 1.3

        # Возраст влияет на требования
        if player.age < 24:
            base_wage *= 1.1  # Молодые хотят больше
        elif player.age > 30:
            base_wage *= 0.9  # Старшие соглашаются на меньшее

        return round(base_wage, -2)  # Округление до сотен

    def make_bid(
        self,
        player_id: str,
        buying_club_id: str,
        amount: float,
        wage_offered: float = 0,
        contract_years: int = 4
    ) -> Dict[str, Any]:
        """
        Подача заявки на игрока.

        Args:
            player_id: ID игрока
            buying_club_id: ID покупающего клуба
            amount: Предлагаемая сумма
            wage_offered: Предлагаемая зарплата
            contract_years: Срок контракта

        Returns:
            Результат заявки
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        buying_club = self.game_state.clubs.get(buying_club_id)
        if not buying_club:
            return {'success': False, 'message': 'Клуб не найден'}

        # Проверка бюджета
        if amount > buying_club.balance:
            return {
                'success': False,
                'message': f'Недостаточно средств. Баланс: {buying_club.balance:,.0f}'
            }

        # Проверка лимита зарплат
        if wage_offered > 0 and wage_offered * 52 > buying_club.wage_budget * 0.3:
            return {
                'success': False,
                'message': 'Предлагаемая зарплата превышает допустимый лимит'
            }

        # Определяем продающий клуб
        selling_club_id = player.club_id
        estimated_fee = self._estimate_transfer_fee(player)

        # Создание заявки
        transfer = Transfer(
            player_id=player_id,
            player_name=player.full_name,
            from_club_id=selling_club_id or '',
            from_club_name=self.game_state.clubs[selling_club_id].name if selling_club_id and selling_club_id in self.game_state.clubs else 'Свободный агент',
            to_club_id=buying_club_id,
            to_club_name=buying_club.name,
            fee=amount,
            wage_offered=wage_offered or player.wage,
            contract_years=contract_years,
            status=TransferStatus.PENDING,
            bid_date=f"Week {self.game_state.current_week}",
        )

        # Автоматический ответ от ИИ клуба
        response = self._ai_respond_to_bid(transfer, player, estimated_fee)

        if response['accepted']:
            transfer.status = TransferStatus.NEGOTIATING
            self.game_state.transfers.append(transfer)
            return {
                'success': True,
                'message': 'Заявка принята к рассмотрению',
                'transfer_id': transfer.id,
                'status': 'negotiating',
                'seller_response': response['message'],
            }
        else:
            transfer.status = TransferStatus.REJECTED
            self.game_state.transfers.append(transfer)
            return {
                'success': False,
                'message': response['message'],
                'transfer_id': transfer.id,
                'status': 'rejected',
            }

    def _ai_respond_to_bid(
        self,
        transfer: Transfer,
        player: Player,
        estimated_fee: float
    ) -> Dict[str, Any]:
        """Автоматический ответ ИИ на заявку"""
        if not transfer.from_club_id:
            # Свободный агент - всегда соглашается
            return {'accepted': True, 'message': 'Игрок заинтересован'}

        selling_club = self.game_state.clubs.get(transfer.from_club_id)
        if not selling_club:
            return {'accepted': False, 'message': 'Клуб не найден'}

        # Факторы принятия решения
        fee_ratio = transfer.fee / estimated_fee if estimated_fee > 1 else 0

        # Клуб хочет продать?
        want_to_sell = self._should_sell(player, selling_club)

        if want_to_sell:
            if fee_ratio >= 0.9:
                return {'accepted': True, 'message': 'Клуб согласен на條件'}
            elif fee_ratio >= 0.7:
                # Контрпредложение
                counter_offer = estimated_fee * 1.1
                return {
                    'accepted': False,
                    'message': f'Контрпредложение: {counter_offer:,.0f}'
                }
            else:
                return {
                    'accepted': False,
                    'message': f'Предложение слишком низкое. Минимум: {estimated_fee:,.0f}'
                }
        else:
            if fee_ratio >= 1.5:
                return {'accepted': True, 'message': 'Клуб принял из-за высокой суммы'}
            else:
                return {
                    'accepted': False,
                    'message': 'Клуб не заинтересован в продаже этого игрока'
                }

    def _should_sell(self, player: Player, club: Club) -> bool:
        """Должен ли клуб продать игрока"""
        # Старше 32 - продадут
        if player.age > 32:
            return True

        # Низкая форма - могут продать
        if player.form < 30:
            return random.random() < 0.6

        # Много денег нужно клубу
        if club.balance < club.budget * 0.2:
            return random.random() < 0.4

        # Игрок хочет уйти (низкое настроение)
        if player.morale < 30:
            return random.random() < 0.7

        return False

    def negotiate_fee(
        self,
        transfer_id: str,
        counter_offer: float,
        response: str = 'accept'
    ) -> Dict[str, Any]:
        """
        Переговоры по трансферной сумме.

        Args:
            transfer_id: ID трансфера
            counter_offer: Контрпредложение
            response: 'accept', 'reject', 'counter'

        Returns:
            Результат переговоров
        """
        transfer = None
        for t in self.game_state.transfers:
            if t.id == transfer_id:
                transfer = t
                break

        if not transfer:
            return {'success': False, 'message': 'Трансфер не найден'}

        if transfer.status != TransferStatus.NEGOTIATING:
            return {'success': False, 'message': 'Трансфер не в статусе переговоров'}

        if response == 'accept':
            # Игрок принимает предложение
            transfer.fee = counter_offer
            transfer.status = TransferStatus.AGREED
            return {'success': True, 'message': 'Сумма согласована'}

        elif response == 'counter':
            # Игрок делает контрпредложение
            transfer.fee = counter_offer
            return {
                'success': True,
                'message': f'Контрпредложение: {counter_offer:,.0f}',
                'status': 'counter_offer'
            }

        else:
            transfer.status = TransferStatus.CANCELLED
            return {'success': True, 'message': 'Переговоры прекращены'}

    def complete_transfer(
        self,
        transfer_id: str
    ) -> Dict[str, Any]:
        """
        Завершение трансфера.

        Args:
            transfer_id: ID трансфера

        Returns:
            Результат завершения
        """
        transfer = None
        for t in self.game_state.transfers:
            if t.id == transfer_id:
                transfer = t
                break

        if not transfer:
            return {'success': False, 'message': 'Трансфер не найден'}

        if transfer.status not in [
            TransferStatus.AGREED,
            TransferStatus.NEGOTIATING
        ]:
            return {'success': False, 'message': 'Трансфер не может быть завершён'}

        player = self.game_state.players.get(transfer.player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        buying_club = self.game_state.clubs.get(transfer.to_club_id)
        selling_club = self.game_state.clubs.get(transfer.from_club_id) if transfer.from_club_id else None

        # Проверка средств покупателя
        if buying_club and transfer.fee > buying_club.balance:
            return {'success': False, 'message': 'Недостаточно средств'}

        # Перевод средств
        if selling_club and buying_club:
            selling_club.balance += transfer.fee
            buying_club.balance -= transfer.fee

        # Обновление данных игрока
        old_club_id = player.club_id
        player.club_id = transfer.to_club_id
        player.wage = transfer.wage_offered

        # Обновление составов клубов
        if old_club_id and old_club_id in self.game_state.clubs:
            old_club = self.game_state.clubs[old_club_id]
            if player.id in old_club.squad:
                old_club.squad.remove(player.id)
            old_club.transfers_out.append(player.id)

        if buying_club:
            if player.id not in buying_club.squad:
                buying_club.squad.append(player.id)
            buying_club.transfers_in.append(player.id)
            buying_club.wage_bill += transfer.wage_offered

        # Создание нового контракта
        contract = Contract(
            player_id=player.id,
            club_id=transfer.to_club_id,
            wage=transfer.wage_offered,
            duration_years=transfer.contract_years,
            status=ContractStatus.ACTIVE,
        )
        self.game_state.contracts[contract.id] = contract
        player.contract_id = contract.id

        # Обновление статуса трансфера
        transfer.status = TransferStatus.COMPLETED
        transfer.completion_date = f"Week {self.game_state.current_week}"

        return {
            'success': True,
            'message': f'{player.full_name} перешёл в {buying_club.name if buying_club else "новый клуб"}!',
            'transfer': transfer.to_dict(),
        }

    def loan_player(
        self,
        player_id: str,
        to_club_id: str,
        duration_weeks: int = 26,
        wage_contribution: float = 0.5
    ) -> Dict[str, Any]:
        """
        Отправка игрока в аренду.

        Args:
            player_id: ID игрока
            to_club_id: ID принимающего клуба
            duration_weeks: Длительность аренды в неделях
            wage_contribution: Доля зарплаты, оплачиваемая арендодателем (0-1)

        Returns:
            Результат аренды
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        to_club = self.game_state.clubs.get(to_club_id)
        if not to_club:
            return {'success': False, 'message': 'Клуб не найден'}

        from_club = self.game_state.clubs.get(player.club_id)
        if not from_club:
            return {'success': False, 'message': 'Игрок не состоит в клубе'}

        # Создание аренды
        transfer = Transfer(
            player_id=player_id,
            player_name=player.full_name,
            from_club_id=player.club_id,
            from_club_name=from_club.name,
            to_club_id=to_club_id,
            to_club_name=to_club.name,
            fee=0,
            wage_offered=player.wage * wage_contribution,
            status=TransferStatus.LOAN,
            is_loan=True,
            loan_duration_weeks=duration_weeks,
            bid_date=f"Week {self.game_state.current_week}",
        )

        # Временное перемещение игрока
        player.club_id = to_club_id
        if player.id in from_club.squad:
            from_club.squad.remove(player.id)
        if player.id not in to_club.squad:
            to_club.squad.append(player.id)

        self.game_state.transfers.append(transfer)

        return {
            'success': True,
            'message': f'{player.full_name} отправлен в аренду в {to_club.name} на {duration_weeks} недель',
            'transfer': transfer.to_dict(),
        }

    def free_agent_signing(
        self,
        player_id: str,
        club_id: str,
        wage: float,
        contract_years: int = 3
    ) -> Dict[str, Any]:
        """
        Подписание свободного агента.

        Args:
            player_id: ID игрока
            club_id: ID клуба
            wage: Зарплата
            contract_years: Срок контракта

        Returns:
            Результат подписания
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        if player.club_id:
            return {'success': False, 'message': 'Игрок не является свободным агентом'}

        club = self.game_state.clubs.get(club_id)
        if not club:
            return {'success': False, 'message': 'Клуб не найден'}

        # Проверка бюджета
        annual_wage = wage * 52
        if annual_wage > club.wage_budget * 0.2:
            return {'success': False, 'message': 'Зарплата превышает допустимый лимит'}

        # Подписание
        player.club_id = club_id
        player.wage = wage
        club.squad.append(player.id)
        club.wage_bill += wage

        # Создание контракта
        contract = Contract(
            player_id=player.id,
            club_id=club_id,
            wage=wage,
            duration_years=contract_years,
            status=ContractStatus.ACTIVE,
        )
        self.game_state.contracts[contract.id] = contract
        player.contract_id = contract.id

        # Создание записи о трансфере
        transfer = Transfer(
            player_id=player_id,
            player_name=player.full_name,
            from_club_id='',
            from_club_name='Свободный агент',
            to_club_id=club_id,
            to_club_name=club.name,
            fee=0,
            wage_offered=wage,
            contract_years=contract_years,
            status=TransferStatus.COMPLETED,
            completion_date=f"Week {self.game_state.current_week}",
        )
        self.game_state.transfers.append(transfer)

        return {
            'success': True,
            'message': f'{player.full_name} подписан на {contract_years} лет!',
            'transfer': transfer.to_dict(),
        }

    def list_for_sale(
        self,
        player_id: str,
        asking_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Выставление игрока на продажу.

        Args:
            player_id: ID игрока
            asking_price: Запрашиваемая цена (если None, автоматическая)

        Returns:
            Результат
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        if not player.club_id:
            return {'success': False, 'message': 'Игрок не состоит в клубе'}

        price = asking_price or self._estimate_transfer_fee(player)

        # Помечаем игрока как доступного
        # (в реальной игре это было бы отдельное поле, здесь используем morale как индикатор)
        player.morale = max(0, player.morale - 5)  # Немного снижаем настроение

        return {
            'success': True,
            'message': f'{player.full_name} выставлен за {price:,.0f}',
            'asking_price': price,
        }

    def delist_player(self, player_id: str) -> Dict[str, Any]:
        """
        Снятие игрока с продажи.

        Args:
            player_id: ID игрока

        Returns:
            Результат
        """
        player = self.game_state.players.get(player_id)
        if not player:
            return {'success': False, 'message': 'Игрок не найден'}

        # Восстанавливаем настроение
        player.morale = min(100, player.morale + 3)

        return {
            'success': True,
            'message': f'{player.full_name} снят с продажи',
        }

    def get_transfer_history(
        self,
        club_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Получение истории трансферов.

        Args:
            club_id: Фильтр по клубу
            limit: Максимальное количество записей

        Returns:
            Список трансферов
        """
        transfers = [
            t for t in self.game_state.transfers
            if t.status == TransferStatus.COMPLETED
        ]

        if club_id:
            transfers = [
                t for t in transfers
                if t.from_club_id == club_id or t.to_club_id == club_id
            ]

        # Сортировка по дате
        transfers.sort(key=lambda t: t.completion_date, reverse=True)

        return [t.to_dict() for t in transfers[:limit]]
