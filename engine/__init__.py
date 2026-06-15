# -*- coding: utf-8 -*-
"""
Движок игры - обёртки над C++ модулями.
Содержит симулятор матчей, ИИ клуба и калькулятор статистик.
"""

try:
    from .match import MatchSimulator
    from .ai import ClubAIWrapper
    from .stats import StatCalculatorWrapper
except ImportError:
    from engine.match import MatchSimulator
    from engine.ai import ClubAIWrapper
    from engine.stats import StatCalculatorWrapper

__all__ = ['MatchSimulator', 'ClubAIWrapper', 'StatCalculatorWrapper']
