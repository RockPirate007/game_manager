"""Модуль валидации пользовательского ввода."""

import re
from typing import Optional, Tuple


def validate_amount(
    value: str,
    min_val: float = 0,
    max_val: float = float("inf"),
    allow_negative: bool = False,
) -> Tuple[bool, Optional[float], str]:
    """
    Проверить введённую сумму денег.

    Args:
        value: Строка с суммой
        min_val: Минимальное значение
        max_val: Максимальное значение
        allow_negative: Разрешить отрицательные значения

    Returns:
        Кортеж (успех, значение, сообщение об ошибке)

    Examples:
        >>> validate_amount("1500000", min_val=0, max_val=1000000000)
        (True, 1500000.0, '')
        >>> validate_amount("-100")
        (False, None, 'Сумма не может быть отрицательной')
    """
    value = value.strip()

    if not value:
        return False, None, "Сумма не может быть пустой"

    # Поддержка суффиксов K, M, B
    multiplier = 1
    if value.upper().endswith("K"):
        multiplier = 1_000
        value = value[:-1]
    elif value.upper().endswith("M"):
        multiplier = 1_000_000
        value = value[:-1]
    elif value.upper().endswith("B"):
        multiplier = 1_000_000_000
        value = value[:-1]

    try:
        amount = float(value) * multiplier
    except ValueError:
        return False, None, "Некорректный формат суммы"

    if not allow_negative and amount < 0:
        return False, None, "Сумма не может быть отрицательной"

    if amount < min_val:
        return False, None, f"Минимальная сумма: {min_val:,.0f}"

    if amount > max_val:
        return False, None, f"Максимальная сумма: {max_val:,.0f}"

    return True, amount, ""


def validate_name(
    name: str,
    min_length: int = 1,
    max_length: int = 50,
    allowed_chars: str = r"[a-zA-Zа-яА-ЯёЁ\s\-']",
) -> Tuple[bool, str]:
    """
    Проверить имя (игрока, команды и т.д.).

    Args:
        name: Проверяемое имя
        min_length: Минимальная длина
        max_length: Максимальная длина
        allowed_chars: Регулярное выражение допустимых символов

    Returns:
        Кортеж (успех, сообщение об ошибке)

    Examples:
        >>> validate_name("Александр Петров")
        (True, '')
        >>> validate_name("")
        (False, 'Имя не может быть пустым')
    """
    name = name.strip()

    if not name:
        return False, "Имя не может быть пустым"

    if len(name) < min_length:
        return False, f"Имя слишком короткое (минимум {min_length} символов)"

    if len(name) > max_length:
        return False, f"Имя слишком длинное (максимум {max_length} символов)"

    # Проверяем каждый символ
    for char in name:
        if not re.match(allowed_chars, char):
            return False, f"Недопустимый символ: '{char}'"

    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Проверить email адрес.

    Args:
        email: Проверяемый email

    Returns:
        Кортеж (успех, сообщение об ошибке)

    Examples:
        >>> validate_email("user@example.com")
        (True, '')
        >>> validate_email("invalid-email")
        (False, 'Некорректный формат email')
    """
    email = email.strip()

    if not email:
        return False, "Email не может быть пустым"

    # Простая проверка формата
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Некорректный формат email"

    return True, ""


def validate_slot(
    value: str, min_val: int, max_val: int
) -> Tuple[bool, Optional[int], str]:
    """
    Проверить числовой слот (номер позиции, выбор меню и т.д.).

    Args:
        value: Строка с числом
        min_val: Минимальное значение
        max_val: Максимальное значение

    Returns:
        Кортеж (успех, значение, сообщение об ошибке)

    Examples:
        >>> validate_slot("5", 1, 10)
        (True, 5, '')
        >>> validate_slot("abc", 1, 10)
        (False, None, 'Введите число')
    """
    value = value.strip()

    if not value:
        return False, None, "Введите число"

    try:
        slot = int(value)
    except ValueError:
        return False, None, "Введите целое число"

    if slot < min_val:
        return False, None, f"Минимальное значение: {min_val}"

    if slot > max_val:
        return False, None, f"Максимальное значение: {max_val}"

    return True, slot, ""


def validate_percentage(value: str) -> Tuple[bool, Optional[float], str]:
    """
    Проверить процентное значение (0-100).

    Args:
        value: Строка с процентом

    Returns:
        Кортеж (успех, значение, сообщение об ошибке)
    """
    value = value.strip().rstrip("%")

    if not value:
        return False, None, "Введите процент"

    try:
        percent = float(value)
    except ValueError:
        return False, None, "Некорректный формат процента"

    if percent < 0 or percent > 100:
        return False, None, "Процент должен быть от 0 до 100"

    return True, percent, ""


def validate_choice(
    value: str, valid_choices: list, case_sensitive: bool = False
) -> Tuple[bool, Optional[str], str]:
    """
    Проверить выбор из списка допустимых значений.

    Args:
        value: Введённое значение
        valid_choices: Список допустимых значений
        case_sensitive: Учитывать ли регистр

    Returns:
        Кортеж (успех, выбранное значение, сообщение об ошибке)
    """
    value = value.strip()

    if not value:
        return False, None, "Выберите вариант из списка"

    if case_sensitive:
        if value in valid_choices:
            return True, value, ""
    else:
        value_lower = value.lower()
        for choice in valid_choices:
            if choice.lower() == value_lower:
                return True, choice, ""

    choices_str = ", ".join(str(c) for c in valid_choices[:5])
    if len(valid_choices) > 5:
        choices_str += ", ..."

    return False, None, f"Допустимые варианты: {choices_str}"


def validate_yes_no(value: str) -> Tuple[bool, Optional[bool], str]:
    """
    Проверить ответ да/нет.

    Args:
        value: Введённое значение

    Returns:
        Кортеж (успех, bool значение, сообщение об ошибке)

    Examples:
        >>> validate_yes_no("да")
        (True, True, '')
        >>> validate_yes_no("нет")
        (True, False, '')
    """
    value = value.strip().lower()

    if value in ("да", "д", "y", "yes", "1", "true"):
        return True, True, ""
    elif value in ("нет", "н", "n", "no", "0", "false"):
        return True, False, ""

    return False, None, "Введите 'да' или 'нет'"
