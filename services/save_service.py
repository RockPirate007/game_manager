# -*- coding: utf-8 -*-
"""
Сервис сохранений.
Управление сохранениями игры: создание, загрузка, удаление, экспорт.
"""

import os
import json
import shutil
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from ..models import GameStateNew as GameState
except ImportError:
    from models import GameStateNew as GameState


class SaveService:
    """
    Сервис сохранений.
    Управление JSON-файлами сохранений.
    """

    # Константы
    MAX_SLOTS = 10
    AUTO_SAVE_SLOT = 0
    SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'saves')
    BACKUP_DIR = os.path.join(SAVE_DIR, 'backups')

    def __init__(self):
        """Инициализация сервиса сохранений"""
        # Создание директорий
        os.makedirs(self.SAVE_DIR, exist_ok=True)
        os.makedirs(self.BACKUP_DIR, exist_ok=True)

    def save_game(
        self,
        game_state: GameState,
        slot: int,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Сохранение игры в слот.

        Args:
            game_state: Состояние игры
            slot: Номер слота (0-9, 0 = автосохранение)
            name: Название сохранения

        Returns:
            Результат сохранения
        """
        if slot < 0 or slot > self.MAX_SLOTS:
            return {'success': False, 'message': f'Неверный слот. Допустимо: 0-{self.MAX_SLOTS}'}

        # Обновление метаданных
        game_state.last_saved = datetime.now().isoformat()
        if name:
            game_state.save_name = name
        elif not game_state.save_name:
            game_state.save_name = f"Сохранение {slot}"

        # Формирование пути
        filename = f"save_slot_{slot}.json"
        filepath = os.path.join(self.SAVE_DIR, filename)

        # Бэкап существующего сохранения
        if os.path.exists(filepath):
            self._backup_save(slot)

        # Сериализация
        try:
            data = game_state.to_dict()
            data['_metadata'] = {
                'slot': slot,
                'saved_at': game_state.last_saved,
                'version': '1.0',
                'checksum': self._calculate_checksum(data),
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            return {
                'success': True,
                'message': f'Игра сохранена в слот {slot}',
                'slot': slot,
                'filename': filename,
                'size': os.path.getsize(filepath),
                'saved_at': game_state.last_saved,
            }
        except Exception as e:
            return {'success': False, 'message': f'Ошибка сохранения: {str(e)}'}

    def load_game(self, slot: int) -> Dict[str, Any]:
        """
        Загрузка игры из слота.

        Args:
            slot: Номер слота

        Returns:
            Состояние игры или ошибка
        """
        if slot < 0 or slot > self.MAX_SLOTS:
            return {'success': False, 'message': f'Неверный слот. Допустимо: 0-{self.MAX_SLOTS}'}

        filename = f"save_slot_{slot}.json"
        filepath = os.path.join(self.SAVE_DIR, filename)

        if not os.path.exists(filepath):
            return {'success': False, 'message': f'Сохранение в слоте {slot} не найдено'}

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Проверка контрольной суммы
            metadata = data.get('_metadata', {})
            stored_checksum = metadata.get('checksum')
            if stored_checksum:
                calculated = self._calculate_checksum(
                    {k: v for k, v in data.items() if k != '_metadata'}
                )
                if stored_checksum != calculated:
                    return {
                        'success': False,
                        'message': 'Файл сохранения повреждён (контрольная сумма не совпадает)',
                    }

            # Восстановление состояния
            game_state = GameState.from_dict(data)

            return {
                'success': True,
                'message': f'Игра загружена из слота {slot}',
                'game_state': game_state,
                'slot': slot,
                'save_name': game_state.save_name,
                'saved_at': metadata.get('saved_at', 'Неизвестно'),
                'week': game_state.current_week,
                'season': game_state.current_season,
            }
        except json.JSONDecodeError:
            return {'success': False, 'message': 'Повреждённый JSON файл'}
        except Exception as e:
            return {'success': False, 'message': f'Ошибка загрузки: {str(e)}'}

    def delete_save(self, slot: int) -> Dict[str, Any]:
        """
        Удаление сохранения.

        Args:
            slot: Номер слота

        Returns:
            Результат удаления
        """
        if slot < 0 or slot > self.MAX_SLOTS:
            return {'success': False, 'message': f'Неверный слот. Допустимо: 0-{self.MAX_SLOTS}'}

        filename = f"save_slot_{slot}.json"
        filepath = os.path.join(self.SAVE_DIR, filename)

        if not os.path.exists(filepath):
            return {'success': False, 'message': f'Сохранение в слоте {slot} не найдено'}

        try:
            # Перемещение в корзину (бэкап перед удалением)
            self._backup_save(slot)
            os.remove(filepath)

            return {
                'success': True,
                'message': f'Сохранение в слоте {slot} удалено',
            }
        except Exception as e:
            return {'success': False, 'message': f'Ошибка удаления: {str(e)}'}

    def list_saves(self) -> List[Dict[str, Any]]:
        """
        Список всех сохранений.

        Returns:
            Информация о сохранениях
        """
        saves = []

        for slot in range(self.MAX_SLOTS + 1):
            filename = f"save_slot_{slot}.json"
            filepath = os.path.join(self.SAVE_DIR, filename)

            if os.path.exists(filepath):
                try:
                    stat = os.stat(filepath)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    metadata = data.get('_metadata', {})
                    save_info = {
                        'slot': slot,
                        'filename': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'save_name': data.get('save_name', f'Сохранение {slot}'),
                        'week': data.get('current_week', 0),
                        'season': data.get('current_season', 2026),
                        'user_club': data.get('user_club_id', ''),
                        'saved_at': metadata.get('saved_at', 'Неизвестно'),
                    }
                    saves.append(save_info)
                except Exception:
                    saves.append({
                        'slot': slot,
                        'filename': filename,
                        'error': 'Ошибка чтения',
                    })
            else:
                saves.append({
                    'slot': slot,
                    'filename': filename,
                    'exists': False,
                })

        return saves

    def auto_save(self, game_state: GameState) -> Dict[str, Any]:
        """
        Автосохранение.

        Args:
            game_state: Состояние игры

        Returns:
            Результат автосохранения
        """
        game_state.save_name = f"Автосохранение (Неделя {game_state.current_week})"
        return self.save_game(game_state, self.AUTO_SAVE_SLOT)

    def get_save_info(self, slot: int) -> Dict[str, Any]:
        """
        Получение информации о сохранении без загрузки.

        Args:
            slot: Номер слота

        Returns:
            Информация о сохранении
        """
        filename = f"save_slot_{slot}.json"
        filepath = os.path.join(self.SAVE_DIR, filename)

        if not os.path.exists(filepath):
            return {'exists': False, 'slot': slot}

        try:
            stat = os.stat(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            metadata = data.get('_metadata', {})

            # Подсчет объектов
            clubs_count = len(data.get('clubs', {}))
            players_count = len(data.get('players', {}))
            matches_count = len(data.get('matches', []))
            transfers_count = len(data.get('transfers', []))

            return {
                'exists': True,
                'slot': slot,
                'filename': filename,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'save_name': data.get('save_name', f'Сохранение {slot}'),
                'week': data.get('current_week', 0),
                'season': data.get('current_season', 2026),
                'user_club_id': data.get('user_club_id', ''),
                'clubs': clubs_count,
                'players': players_count,
                'matches': matches_count,
                'transfers': transfers_count,
                'saved_at': metadata.get('saved_at', 'Неизвестно'),
                'version': metadata.get('version', 'Неизвестно'),
            }
        except Exception as e:
            return {'exists': True, 'slot': slot, 'error': str(e)}

    def export_save(
        self,
        slot: int,
        export_path: str
    ) -> Dict[str, Any]:
        """
        Экспорт сохранения в указанный путь.

        Args:
            slot: Номер слота
            export_path: Путь для экспорта

        Returns:
            Результат экспорта
        """
        filename = f"save_slot_{slot}.json"
        source = os.path.join(self.SAVE_DIR, filename)

        if not os.path.exists(source):
            return {'success': False, 'message': f'Сохранение в слоте {slot} не найдено'}

        try:
            # Создание директории если не существует
            os.makedirs(os.path.dirname(export_path) or '.', exist_ok=True)

            # Копирование файла
            shutil.copy2(source, export_path)

            return {
                'success': True,
                'message': f'Сохранение экспортировано в {export_path}',
                'source': source,
                'destination': export_path,
                'size': os.path.getsize(export_path),
            }
        except Exception as e:
            return {'success': False, 'message': f'Ошибка экспорта: {str(e)}'}

    def import_save(
        self,
        import_path: str,
        target_slot: int
    ) -> Dict[str, Any]:
        """
        Импорт сохранения из файла.

        Args:
            import_path: Путь к файлу
            target_slot: Целевой слот

        Returns:
            Результат импорта
        """
        if not os.path.exists(import_path):
            return {'success': False, 'message': f'Файл не найден: {import_path}'}

        if target_slot < 0 or target_slot > self.MAX_SLOTS:
            return {'success': False, 'message': f'Неверный слот. Допустимо: 0-{self.MAX_SLOTS}'}

        try:
            # Проверка валидности JSON
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Проверка структуры
            required_keys = ['save_id', 'current_week', 'clubs', 'players']
            for key in required_keys:
                if key not in data:
                    return {
                        'success': False,
                        'message': f'Неверный формат файла: отсутствует {key}',
                    }

            # Копирование в слот
            target_path = os.path.join(
                self.SAVE_DIR,
                f"save_slot_{target_slot}.json"
            )

            # Бэкап существующего
            if os.path.exists(target_path):
                self._backup_save(target_slot)

            shutil.copy2(import_path, target_path)

            return {
                'success': True,
                'message': f'Сохранение импортировано в слот {target_slot}',
                'source': import_path,
                'slot': target_slot,
                'size': os.path.getsize(target_path),
            }
        except json.JSONDecodeError:
            return {'success': False, 'message': 'Неверный JSON файл'}
        except Exception as e:
            return {'success': False, 'message': f'Ошибка импорта: {str(e)}'}

    def _backup_save(self, slot: int) -> bool:
        """Создание бэкапа сохранения"""
        try:
            filename = f"save_slot_{slot}.json"
            source = os.path.join(self.SAVE_DIR, filename)
            if not os.path.exists(source):
                return False

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_slot_{slot}_{timestamp}.json"
            backup_path = os.path.join(self.BACKUP_DIR, backup_name)

            shutil.copy2(source, backup_path)

            # Ограничение количества бэкапов (оставляем последние 5)
            self._cleanup_backups(slot)

            return True
        except Exception:
            return False

    def _cleanup_backups(self, slot: int, max_backups: int = 5):
        """Очистка старых бэкапов"""
        try:
            backups = []
            for f in os.listdir(self.BACKUP_DIR):
                if f.startswith(f"backup_slot_{slot}_") and f.endswith('.json'):
                    filepath = os.path.join(self.BACKUP_DIR, f)
                    backups.append((os.path.getmtime(filepath), filepath))

            # Сортировка по дате (новые первые)
            backups.sort(reverse=True)

            # Удаление старых
            for _, filepath in backups[max_backups:]:
                os.remove(filepath)
        except Exception:
            pass

    @staticmethod
    def _calculate_checksum(data: Any) -> str:
        """Вычисление контрольной суммы данных"""
        json_str = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(json_str.encode('utf-8')).hexdigest()

    def get_storage_info(self) -> Dict[str, Any]:
        """Информация о хранилище сохранений"""
        total_size = 0
        file_count = 0

        for f in os.listdir(self.SAVE_DIR):
            if f.endswith('.json'):
                filepath = os.path.join(self.SAVE_DIR, f)
                total_size += os.path.getsize(filepath)
                file_count += 1

        backup_count = 0
        backup_size = 0
        if os.path.exists(self.BACKUP_DIR):
            for f in os.listdir(self.BACKUP_DIR):
                if f.endswith('.json'):
                    filepath = os.path.join(self.BACKUP_DIR, f)
                    backup_size += os.path.getsize(filepath)
                    backup_count += 1

        return {
            'save_dir': self.SAVE_DIR,
            'backup_dir': self.BACKUP_DIR,
            'saves_count': file_count,
            'saves_size': total_size,
            'backups_count': backup_count,
            'backups_size': backup_size,
            'total_size': total_size + backup_size,
        }
