# -*- coding: utf-8 -*-
"""
Сервисы игры - трансферы, финансы, тренировки, молодёжь, контракты, сохранения.
"""

try:
    from .transfer_service import TransferService
    from .finance_service import FinanceService
    from .training_service import TrainingService
    from .youth_service import YouthService
    from .contract_service import ContractService
    from .save_service import SaveService
except ImportError:
    from services.transfer_service import TransferService
    from services.finance_service import FinanceService
    from services.training_service import TrainingService
    from services.youth_service import YouthService
    from services.contract_service import ContractService
    from services.save_service import SaveService

__all__ = [
    'TransferService', 'FinanceService', 'TrainingService',
    'YouthService', 'ContractService', 'SaveService'
]
