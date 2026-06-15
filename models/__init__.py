# -*- coding: utf-8 -*-
"""
Модели данных для game_manager engine/services.
Определяет основные сущности: игроки, команды, матчи, контракты и т.д.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


# --- Перечисления ---

class Position(Enum):
    """Игровые позиции"""
    GK = "GK"
    CB = "CB"
    LB = "LB"
    RB = "RB"
    CDM = "CDM"
    CM = "CM"
    CAM = "CAM"
    LW = "LW"
    RW = "RW"
    ST = "ST"
    CF = "CF"


class Formation:
    """Формации команд"""
    F_442 = "4-4-2"
    F_433 = "4-3-3"
    F_4231 = "4-2-3-1"
    F_352 = "3-5-2"
    F_343 = "3-4-3"
    F_532 = "5-3-2"
    F_4141 = "4-1-4-1"


class TrainingFocus:
    """Фокус тренировки"""
    ATTACK = "attack"
    DEFENSE = "defense"
    FITNESS = "fitness"
    TACTICS = "tactics"
    SHOOTING = "shooting"
    PASSING = "passing"
    HEADING = "heading"
    SET_PIECES = "set_pieces"
    YOUTH_DEV = "youth_development"


class TrainingIntensity:
    """Интенсивность тренировки"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class MatchStatus:
    """Статус матча"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class TransferStatus:
    """Статус трансфера"""
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    AGREED = "agreed"
    COMPLETED = "completed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    LOAN = "loan"


class ContractStatus:
    """Статус контракта"""
    ACTIVE = "active"
    EXPIRING = "expiring"
    TERMINATED = "terminated"
    EXPIRED = "expired"


# --- Атрибуты игрока ---

@dataclass
class PlayerAttributes:
    """Атрибуты игрока (от 1 до 99)"""
    pace: int = 50
    shooting: int = 50
    passing: int = 50
    dribbling: int = 50
    defending: int = 50
    physical: int = 50
    heading: int = 50
    crossing: int = 50
    tackling: int = 50
    positioning: int = 50
    reflexes: int = 50
    diving: int = 50
    kicking: int = 50
    stamina: int = 50
    strength: int = 50
    jumping: int = 50
    vision: int = 50
    composure: int = 50
    flair: int = 50
    work_rate: int = 50

    def overall(self) -> float:
        """Средний рейтинг атрибутов"""
        attrs = [
            self.pace, self.shooting, self.passing, self.dribbling,
            self.defending, self.physical, self.heading, self.crossing,
            self.tackling, self.positioning, self.stamina, self.strength,
            self.jumping, self.vision, self.composure, self.flair, self.work_rate
        ]
        return sum(attrs) / len(attrs)

    def to_dict(self) -> Dict[str, int]:
        """Конвертация в словарь"""
        return {
            'pace': self.pace, 'shooting': self.shooting,
            'passing': self.passing, 'dribbling': self.dribbling,
            'defending': self.defending, 'physical': self.physical,
            'heading': self.heading, 'crossing': self.crossing,
            'tackling': self.tackling, 'positioning': self.positioning,
            'reflexes': self.reflexes, 'diving': self.diving,
            'kicking': self.kicking, 'stamina': self.stamina,
            'strength': self.strength, 'jumping': self.jumping,
            'vision': self.vision, 'composure': self.composure,
            'flair': self.flair, 'work_rate': self.work_rate,
        }


# --- Основные модели ---

@dataclass
class Player:
    """Футбольный игрок"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    first_name: str = ""
    last_name: str = ""
    age: int = 20
    nationality: str = "Russia"
    position: str = "CM"
    secondary_positions: List[str] = field(default_factory=list)
    attributes: PlayerAttributes = field(default_factory=PlayerAttributes)
    potential: int = 70
    value: float = 1000000.0
    wage: float = 10000.0
    form: float = 50.0
    morale: float = 70.0
    fatigue: float = 0.0
    injury: Optional[str] = None
    injury_weeks: int = 0
    goals_season: int = 0
    assists_season: int = 0
    appearances: int = 0
    minutes_played: int = 0
    yellow_cards: int = 0
    red_cards: int = 0
    is_captain: bool = False
    contract_id: Optional[str] = None
    club_id: Optional[str] = None
    is_youth: bool = False
    training_focus: Optional[str] = None
    development_points: float = 0.0

    @property
    def full_name(self) -> str:
        """Полное имя"""
        return f"{self.first_name} {self.last_name}".strip() or self.name

    @property
    def overall_rating(self) -> float:
        """Общий рейтинг на основе атрибутов"""
        base = self.attributes.overall()
        form_modifier = (self.form - 50) / 100
        age_modifier = 0
        if self.age < 24:
            age_modifier = (24 - self.age) * 0.01
        elif self.age > 30:
            age_modifier = -(self.age - 30) * 0.02
        return max(1, min(99, base + form_modifier * 10 + age_modifier * 10))

    @property
    def wage_weekly(self) -> float:
        """Недельная зарплата"""
        return self.wage

    @property
    def wage_annual(self) -> float:
        """Годовая зарплата"""
        return self.wage * 52

    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь"""
        return {
            'id': self.id, 'name': self.full_name,
            'first_name': self.first_name, 'last_name': self.last_name,
            'age': self.age, 'nationality': self.nationality,
            'position': self.position, 'secondary_positions': self.secondary_positions,
            'attributes': self.attributes.to_dict(),
            'potential': self.potential, 'value': self.value,
            'wage': self.wage, 'form': self.form, 'morale': self.morale,
            'fatigue': self.fatigue, 'injury': self.injury,
            'injury_weeks': self.injury_weeks,
            'goals_season': self.goals_season, 'assists_season': self.assists_season,
            'appearances': self.appearances, 'minutes_played': self.minutes_played,
            'yellow_cards': self.yellow_cards, 'red_cards': self.red_cards,
            'is_captain': self.is_captain, 'club_id': self.club_id,
            'is_youth': self.is_youth,
        }


@dataclass
class Contract:
    """Контракт игрока"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    player_id: str = ""
    club_id: str = ""
    wage: float = 10000.0
    duration_years: int = 3
    start_date: str = ""
    end_date: str = ""
    release_clause: Optional[float] = None
    bonus_goals: float = 0.0
    bonus_assists: float = 0.0
    bonus_caps: float = 0.0
    signing_fee: float = 0.0
    status: str = "active"

    @property
    def is_expiring_soon(self) -> bool:
        return self.status == "expiring"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id, 'player_id': self.player_id,
            'club_id': self.club_id, 'wage': self.wage,
            'duration_years': self.duration_years,
            'start_date': self.start_date, 'end_date': self.end_date,
            'release_clause': self.release_clause,
            'bonus_goals': self.bonus_goals, 'bonus_assists': self.bonus_assists,
            'bonus_caps': self.bonus_caps, 'signing_fee': self.signing_fee,
            'status': self.status,
        }


@dataclass
class Club:
    """Футбольный клуб"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    short_name: str = ""
    country: str = "Russia"
    league: str = ""
    division: int = 1
    budget: float = 10000000.0
    balance: float = 5000000.0
    wage_budget: float = 500000.0
    reputation: int = 50
    stadium_capacity: int = 30000
    attendance_avg: float = 20000
    ticket_price: float = 25.0
    sponsor_deal: float = 5000000.0
    formation: str = "4-4-2"
    style: str = "balanced"
    squad: List[str] = field(default_factory=list)
    youth_squad: List[str] = field(default_factory=list)
    transfers_in: List[str] = field(default_factory=list)
    transfers_out: List[str] = field(default_factory=list)
    wage_bill: float = 0.0
    season_wins: int = 0
    season_draws: int = 0
    season_losses: int = 0
    season_goals_for: int = 0
    season_goals_against: int = 0
    points: int = 0
    league_position: int = 1

    @property
    def goal_difference(self) -> int:
        return self.season_goals_for - self.season_goals_against

    @property
    def matches_played(self) -> int:
        return self.season_wins + self.season_draws + self.season_losses

    @property
    def squad_size(self) -> int:
        return len(self.squad)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id, 'name': self.name, 'short_name': self.short_name,
            'country': self.country, 'league': self.league,
            'division': self.division, 'budget': self.budget,
            'balance': self.balance, 'wage_budget': self.wage_budget,
            'reputation': self.reputation,
            'stadium_capacity': self.stadium_capacity,
            'attendance_avg': self.attendance_avg,
            'ticket_price': self.ticket_price,
            'sponsor_deal': self.sponsor_deal,
            'formation': self.formation, 'style': self.style,
            'squad': self.squad, 'youth_squad': self.youth_squad,
            'wage_bill': self.wage_bill,
            'season_wins': self.season_wins,
            'season_draws': self.season_draws,
            'season_losses': self.season_losses,
            'season_goals_for': self.season_goals_for,
            'season_goals_against': self.season_goals_against,
            'points': self.points,
            'league_position': self.league_position,
        }


@dataclass
class MatchEvent:
    """Событие матча"""
    minute: int = 0
    event_type: str = ""
    player_id: str = ""
    player_name: str = ""
    team_id: str = ""
    team_name: str = ""
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'minute': self.minute, 'event_type': self.event_type,
            'player_id': self.player_id, 'player_name': self.player_name,
            'team_id': self.team_id, 'team_name': self.team_name,
            'description': self.description, 'details': self.details,
        }


@dataclass
class Match:
    """Матч"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    home_team_id: str = ""
    home_team_name: str = ""
    away_team_id: str = ""
    away_team_name: str = ""
    home_score: int = 0
    away_score: int = 0
    status: str = "scheduled"
    date: str = ""
    week: int = 0
    league: str = ""
    venue: str = ""
    attendance: int = 0
    events: List[MatchEvent] = field(default_factory=list)
    home_stats: Dict[str, Any] = field(default_factory=dict)
    away_stats: Dict[str, Any] = field(default_factory=dict)
    commentary: List[str] = field(default_factory=list)

    @property
    def result(self) -> str:
        return f"{self.home_score} - {self.away_score}"

    @property
    def winner(self) -> Optional[str]:
        if self.home_score > self.away_score:
            return self.home_team_id
        elif self.away_score > self.home_score:
            return self.away_team_id
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'home_team_id': self.home_team_id,
            'home_team_name': self.home_team_name,
            'away_team_id': self.away_team_id,
            'away_team_name': self.away_team_name,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'status': self.status, 'date': self.date,
            'week': self.week, 'league': self.league,
            'venue': self.venue, 'attendance': self.attendance,
            'events': [e.to_dict() for e in self.events],
            'home_stats': self.home_stats,
            'away_stats': self.away_stats,
            'commentary': self.commentary,
        }


@dataclass
class Transfer:
    """Трансфер"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    player_id: str = ""
    player_name: str = ""
    from_club_id: str = ""
    from_club_name: str = ""
    to_club_id: str = ""
    to_club_name: str = ""
    fee: float = 0.0
    wage_offered: float = 0.0
    contract_years: int = 0
    status: str = "pending"
    bid_date: str = ""
    completion_date: str = ""
    is_loan: bool = False
    loan_duration_weeks: int = 0
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id, 'player_id': self.player_id,
            'player_name': self.player_name,
            'from_club_id': self.from_club_id,
            'from_club_name': self.from_club_name,
            'to_club_id': self.to_club_id,
            'to_club_name': self.to_club_name,
            'fee': self.fee, 'wage_offered': self.wage_offered,
            'contract_years': self.contract_years,
            'status': self.status, 'bid_date': self.bid_date,
            'completion_date': self.completion_date,
            'is_loan': self.is_loan,
            'loan_duration_weeks': self.loan_duration_weeks,
            'notes': self.notes,
        }


@dataclass
class TrainingSession:
    """Тренировочная сессия"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    week: int = 0
    focus: str = "balanced"
    intensity: str = "medium"
    team_id: str = ""
    players_trained: List[str] = field(default_factory=list)
    improvements: Dict[str, Dict[str, int]] = field(default_factory=dict)
    injuries_occurred: List[Dict[str, Any]] = field(default_factory=list)
    fitness_change: float = 0.0
    morale_change: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id, 'week': self.week,
            'focus': self.focus, 'intensity': self.intensity,
            'team_id': self.team_id,
            'players_trained': self.players_trained,
            'improvements': self.improvements,
            'injuries_occurred': self.injuries_occurred,
            'fitness_change': self.fitness_change,
            'morale_change': self.morale_change,
        }


@dataclass
class YouthPlayer:
    """Молодой игрок академии"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    player_id: str = ""
    name: str = ""
    age: int = 15
    potential: int = 70
    scout_rating: float = 50.0
    development_speed: float = 1.0
    promoted: bool = False
    promotion_date: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id, 'player_id': self.player_id,
            'name': self.name, 'age': self.age,
            'potential': self.potential,
            'scout_rating': self.scout_rating,
            'development_speed': self.development_speed,
            'promoted': self.promoted,
            'promotion_date': self.promotion_date,
            'notes': self.notes,
        }


@dataclass
class LeagueTable:
    """Таблица лиги"""
    league_name: str = ""
    season: str = ""
    standings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'league_name': self.league_name,
            'season': self.season,
            'standings': self.standings,
        }


@dataclass
class GameStateNew:
    """Полное состояние игры"""
    save_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    save_name: str = ""
    current_week: int = 1
    current_season: int = 2026
    user_club_id: str = ""
    clubs: Dict[str, Club] = field(default_factory=dict)
    players: Dict[str, Player] = field(default_factory=dict)
    contracts: Dict[str, Contract] = field(default_factory=dict)
    matches: List[Match] = field(default_factory=list)
    transfers: List[Transfer] = field(default_factory=list)
    training_sessions: List[TrainingSession] = field(default_factory=list)
    youth_players: List[YouthPlayer] = field(default_factory=list)
    league_tables: Dict[str, LeagueTable] = field(default_factory=dict)
    created_at: str = ""
    last_saved: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'save_id': self.save_id, 'save_name': self.save_name,
            'current_week': self.current_week,
            'current_season': self.current_season,
            'user_club_id': self.user_club_id,
            'clubs': {k: v.to_dict() for k, v in self.clubs.items()},
            'players': {k: v.to_dict() for k, v in self.players.items()},
            'contracts': {k: v.to_dict() for k, v in self.contracts.items()},
            'matches': [m.to_dict() for m in self.matches],
            'transfers': [t.to_dict() for t in self.transfers],
            'training_sessions': [s.to_dict() for s in self.training_sessions],
            'youth_players': [y.to_dict() for y in self.youth_players],
            'league_tables': {k: v.to_dict() for k, v in self.league_tables.items()},
            'created_at': self.created_at,
            'last_saved': self.last_saved,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameStateNew':
        """Создание GameState из словаря"""
        state = cls()
        state.save_id = data.get('save_id', state.save_id)
        state.save_name = data.get('save_name', '')
        state.current_week = data.get('current_week', 1)
        state.current_season = data.get('current_season', 2026)
        state.user_club_id = data.get('user_club_id', '')
        state.created_at = data.get('created_at', '')
        state.last_saved = data.get('last_saved', '')

        for club_id, club_data in data.get('clubs', {}).items():
            club = Club()
            for k, v in club_data.items():
                if hasattr(club, k):
                    setattr(club, k, v)
            state.clubs[club_id] = club

        for player_id, player_data in data.get('players', {}).items():
            player = Player()
            for k, v in player_data.items():
                if k == 'attributes':
                    attrs = PlayerAttributes()
                    for ak, av in v.items():
                        if hasattr(attrs, ak):
                            setattr(attrs, ak, av)
                    player.attributes = attrs
                elif hasattr(player, k):
                    setattr(player, k, v)
            state.players[player_id] = player

        for contract_id, contract_data in data.get('contracts', {}).items():
            contract = Contract()
            for k, v in contract_data.items():
                if hasattr(contract, k):
                    setattr(contract, k, v)
            state.contracts[contract_id] = contract

        return state


# --- Экспорт ---
__all__ = [
    'Position', 'Formation', 'TrainingFocus', 'TrainingIntensity',
    'MatchStatus', 'TransferStatus', 'ContractStatus',
    'PlayerAttributes', 'Player', 'Contract', 'Club',
    'MatchEvent', 'Match', 'Transfer', 'TrainingSession',
    'YouthPlayer', 'LeagueTable', 'GameStateNew',
]
