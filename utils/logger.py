"""Простой логгер для записи в файл и вывода в консоль."""

import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """Логгер с поддержкой уровней DEBUG, INFO, WARNING, ERROR."""

    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }

    LEVEL_NAMES = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
    }

    LEVEL_COLORS = {
        logging.DEBUG: "dim",
        logging.INFO: "green",
        logging.WARNING: "yellow",
        logging.ERROR: "bold red",
    }

    def __init__(
        self,
        name: str = "game_manager",
        log_file: str = "game_manager.log",
        level: str = "INFO",
        console_output: bool = True,
    ):
        """
        Инициализация логгера.

        Args:
            name: Имя логгера
            log_file: Путь к файлу логов
            level: Уровень логирования (DEBUG, INFO, WARNING, ERROR)
            console_output: Выводить ли в консоль
        """
        self.name = name
        self.log_file = log_file
        self.console_output = console_output
        self._level = self.LOG_LEVELS.get(level.upper(), logging.INFO)

        # Создаем логгер
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self._level)

        # Убираем обработчики по умолчанию
        self.logger.handlers.clear()

        # Форматтер для файла
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Форматтер для консоли (без даты, короче)
        console_formatter = logging.Formatter("%(levelname)-8s | %(message)s")

        # Обработчик для файла
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(self._level)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Обработчик для консоли (опционально)
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self._level)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

    @property
    def level(self) -> str:
        """Текущий уровень логирования."""
        return self.LEVEL_NAMES.get(self._level, "INFO")

    def set_level(self, level: str) -> None:
        """
        Установить уровень логирования.

        Args:
            level: Новый уровень (DEBUG, INFO, WARNING, ERROR)
        """
        level_upper = level.upper()
        if level_upper not in self.LOG_LEVELS:
            raise ValueError(
                f"Неизвестный уровень логирования: {level}. "
                f"Доступные: {', '.join(self.LOG_LEVELS.keys())}"
            )
        self._level = self.LOG_LEVELS[level_upper]
        self.logger.setLevel(self._level)
        for handler in self.logger.handlers:
            handler.setLevel(self._level)

    def debug(self, message: str, *args, **kwargs) -> None:
        """Записать сообщение уровня DEBUG."""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Записать сообщение уровня INFO."""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Записать сообщение уровня WARNING."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Записать сообщение уровня ERROR."""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Записать сообщение уровня CRITICAL."""
        self.logger.critical(message, *args, **kwargs)

    def log(self, level: str, message: str, *args, **kwargs) -> None:
        """
        Записать сообщение указанного уровня.

        Args:
            level: Уровень сообщения
            message: Текст сообщения
        """
        level_upper = level.upper()
        if level_upper in self.LOG_LEVELS:
            self.logger.log(self.LOG_LEVELS[level_upper], message, *args, **kwargs)

    def exception(self, message: str, *args, **kwargs) -> None:
        """Записать сообщение уровня ERROR с информацией об исключении."""
        self.logger.exception(message, *args, **kwargs)

    def get_log_content(self, lines: Optional[int] = None) -> str:
        """
        Прочитать содержимое файла логов.

        Args:
            lines: Количество последних строк (None = все)

        Returns:
            Содержимое логов
        """
        if not os.path.exists(self.log_file):
            return ""
        with open(self.log_file, "r", encoding="utf-8") as f:
            content = f.readlines()
        if lines:
            content = content[-lines:]
        return "".join(content)

    def clear_log(self) -> None:
        """Очистить файл логов."""
        if os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("")
            self.info("Файл логов очищен")

    def __repr__(self) -> str:
        return f"Logger(name='{self.name}', level='{self.level}', file='{self.log_file}')"
