"""
game/media.py — Пресс-конференции и взаимодействие с прессой.
Менеджер отвечает на вопросы журналистов, что влияет на репутацию.
"""

import random
from typing import Any, Dict, List, Optional, Tuple


# Шаблоны вопросов по категориям
QUESTION_TEMPLATES = {
    "pre_match": [
        "Как вы оцениваете шансы вашей команды в предстоящем матче?",
        "Что вы говорили игрокам перед матчем?",
        "Как справляетесь с давлением перед важным матчем?",
        "Какой тактический план на игру?",
        "Ваши ожидания от матча?",
    ],
    "post_match_win": [
        "Поздравляем с победой! Как вы себя чувствуете?",
        "Что стало ключевым фактором в сегодняшней победе?",
        "Как оцените игру команды сегодня?",
        "Что вы скажете критикам, которые не верили в победу?",
        "Какие выводы можно сделать после этого матча?",
    ],
    "post_match_loss": [
        "Что пошло не так в сегодняшнем матче?",
        "Как вы прокомментируете поражение?",
        "Будут ли изменения в составе после этого матча?",
        "Как вы планируете выходить из ситуации?",
        "Что вы скажете болельщикам?",
    ],
    "post_match_draw": [
        "Как вы оцениваете результат матча?",
        "Ничья — это справедливый результат?",
        "Что нужно изменить, чтобы побеждать?",
        "Как вы мотивируете команду после ничьей?",
    ],
    "transfer": [
        "Правда ли, что клуб заинтересован в {player}?",
        "Можете ли вы подтвердить информацию о трансфере?",
        "Как обстоят дела с контрактом {player}?",
        "Есть ли бюджет на зимнее трансферное окно?",
        "Кто приоритетная цель для усиления команды?",
    ],
    "general": [
        "Как вы оцениваете текущую форму команды?",
        "Что вы думаете о выступлении в чемпионате?",
        "Какова ваша цель на сезон?",
        "Как вы относитесь к конкуренции в команде?",
        "Что для вас важнее всего в管理工作?",
    ],
    "crisis": [
        "Команда проиграла 3 матча подряд. Как вы это прокомментируете?",
        "Болельщики требуют вашей отставки. Что вы скажете?",
        "Довольны ли вы работой игроков?",
        "Готовы ли вы уйти в отставку?",
        "Что вы будете делать для исправления ситуации?",
    ],
}

# Шаблоны ответов по категориям и настроению (optimistic, neutral, defensive)
RESPONSE_TEMPLATES = {
    "optimistic": [
        "Мы хорошо подготовились и有信心 в успех.",
        "Команда в отличной форме, мы готовы к матчу.",
        "Мы работаем каждый день, и результаты не заставят себя ждать.",
        "Я верю в этих игроков, они покажут свой лучший футбол.",
        "Мы на правильном пути, и я доволен прогрессом команды.",
    ],
    "neutral": [
        "Мы стараемся изо всех сил и надеемся на лучший результат.",
        "Это будет сложный матч, но мы постараемся показать хорошую игру.",
        "Мы сосредоточены на своей игре и не думаем о сопернике.",
        "Каждый матч по-своему важен, и мы подходим к нему серьёзно.",
        "Мы работаем над ошибками и стремимся к улучшению.",
    ],
    "defensive": [
        "Я не согласен с этой оценкой, у нас свои планы.",
        "Критика — это нормально, но мы знаем, что делаем.",
        "Мы не будем отчитываться перед прессой, мы работаем на поле.",
        "Каждый имеет право на своё мнение, но мы верим в свою работу.",
        "Мы сосредоточены на задачах, а не на словах критиков.",
    ],
    "diplomatic": [
        "Соперник сильный, но мы постараемся показать достойную игру.",
        "Мы уважаем каждого соперника, но играем на победу.",
        "Футбол непредсказуем, и мы готовы к любому развитию событий.",
        "Мы сосредоточены на自己的 игре и не хотим комментировать других.",
    ],
}


class PressConference:
    """
    Класс пресс-конференции.
    Управляет вопросами, ответами и влиянием на репутацию.
    """

    def __init__(self) -> None:
        self._questions: List[Dict[str, Any]] = []
        self._answers: List[Dict[str, Any]] = []
        self._reputation_impact = 0.0
        self._conferences_held = 0

    # ── Получение вопросов ──────────────────────────────────────────
    def get_questions(
        self,
        category: str = "general",
        count: int = 3,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получение списка вопросов для пресс-конференции.
        :param category: категория вопросов
        :param count: количество вопросов
        :param context: контекст (имена игроков и т.д.)
        """
        templates = QUESTION_TEMPLATES.get(category, QUESTION_TEMPLATES["general"])
        selected = random.sample(templates, min(count, len(templates)))

        questions = []
        for i, template in enumerate(selected, 1):
            # Подставляем контекст если есть
            question_text = template
            if context and "{player}" in question_text:
                player_name = context.get("player_name", "игрок")
                question_text = question_text.replace("{player}", player_name)

            questions.append({
                "id": i,
                "text": question_text,
                "category": category,
            })

        self._questions = questions
        return questions

    # ── Ответ на вопрос ─────────────────────────────────────────────
    def answer_question(
        self,
        question_id: int,
        answer_tone: str = "neutral",
    ) -> Dict[str, Any]:
        """
        Ответ на вопрос журналиста.
        :param question_id: ID вопроса
        :param answer_tone: тон ответа (optimistic, neutral, defensive, diplomatic)
        :return: словарь с ответом и его影響ом
        """
        # Находим вопрос
        question = None
        for q in self._questions:
            if q["id"] == question_id:
                question = q
                break

        if not question:
            return {"error": "Вопрос не найден"}

        # Выбираем шаблон ответа
        tone_templates = RESPONSE_TEMPLATES.get(answer_tone, RESPONSE_TEMPLATES["neutral"])
        answer_text = random.choice(tone_templates)

        # Рассчитываем влияние на репутацию
        impact = self._calculate_impact(answer_tone, question.get("category", "general"))

        answer = {
            "question_id": question_id,
            "question": question["text"],
            "answer": answer_text,
            "tone": answer_tone,
            "reputation_impact": impact,
        }

        self._answers.append(answer)
        self._reputation_impact += impact

        return answer

    def _calculate_impact(self, tone: str, category: str) -> float:
        """
        Расчёт влияния ответа на репутацию.
        Оптимистичные ответы generally increase reputation,
        defensive ones may decrease it.
        """
        base_impact = {
            "optimistic": 0.5,
            "neutral": 0.1,
            "defensive": -0.3,
            "diplomatic": 0.3,
        }

        impact = base_impact.get(tone, 0.0)

        # Модификаторы по категории
        if category == "crisis":
            # В кризисе оптимизм ценится выше
            if tone == "optimistic":
                impact += 0.5
            elif tone == "defensive":
                impact -= 0.5
        elif category == "post_match_loss":
            # После поражения дипломатичность лучше
            if tone == "diplomatic":
                impact += 0.3
            elif tone == "optimistic":
                impact -= 0.2  # Слишком оптимистично после поражения

        return round(impact, 2)

    # ── Итоги пресс-конференции ─────────────────────────────────────
    def get_reputation_impact(self) -> float:
        """Общее влияние пресс-конференции на репутацию."""
        return self._reputation_impact

    def get_conference_summary(self) -> Dict[str, Any]:
        """Получение итогов пресс-конференции."""
        self._conferences_held += 1
        summary = {
            "conference_number": self._conferences_held,
            "questions_asked": len(self._questions),
            "answers_given": len(self._answers),
            "total_reputation_impact": self._reputation_impact,
            "answers": self._answers,
        }
        # Сбрасываем для следующей конференции
        self._questions.clear()
        self._answers.clear()
        self._reputation_impact = 0.0
        return summary

    # ── Пресеты ответов ─────────────────────────────────────────────
    def get_quick_answer(self, question_category: str) -> str:
        """Быстрый ответ без сохранения в историю."""
        tone = random.choice(["optimistic", "neutral", "diplomatic"])
        templates = RESPONSE_TEMPLATES.get(tone, RESPONSE_TEMPLATES["neutral"])
        return random.choice(templates)

    # ── Сериализация ────────────────────────────────────────────────
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация в словарь."""
        return {
            "conferences_held": self._conferences_held,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PressConference":
        """Десериализация из словаря."""
        pc = cls()
        pc._conferences_held = data.get("conferences_held", 0)
        return pc

    def __repr__(self) -> str:
        return f"PressConference(conferences_held={self._conferences_held})"
