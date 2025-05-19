from .Transaction import Transaction
from .TransactionMapper import TransactionMapper
from typing import List
from backend.db.Database import Database
import logging

logger = logging.getLogger(__name__)

class TransactionRepository:
    __transactions = []
    __transactionMapper = None
    __db = None

    def __init__(self, db: Database):
        self.__db = db

    # Get methods
    def getTransactions(self) -> List[Transaction]:
        if len(self.__transactions) == 0:
            self.initializeTransactions()
        return self.__transactions

    def getTransactionMapper(self) -> TransactionMapper:
        if self.__transactionMapper is None:
            self.__transactionMapper = TransactionMapper()
        return self.__transactionMapper

    def getTransactionsByUserId(self, user_id: int) -> List[dict]:
        transactions = self.getTransactionMapper().getTransactionsByUserId(user_id, self.__db)
        return [t.getDataObject() for t in transactions]

    def getTransactionsByCampsiteId(self, campsite_id: int) -> List[dict]:
        transactions = self.getTransactionMapper().getTransactionsByCampsiteId(campsite_id, self.__db)
        return [t.getDataObject() for t in transactions]

    def getDb(self) -> Database:
        return self.__db

    # Set methods
    def setTransactions(self, transactions: List[Transaction]) -> None:
        self.__transactions = transactions

    def setTransactionMapper(self, transactionMapper: TransactionMapper) -> None:
        self.__transactionMapper = transactionMapper

    def initializeTransactions(self) -> None:
        self.setTransactions(self.getTransactionMapper().getTransactionObjects(self.__db))

    def setDb(self, db: Database) -> None:
        self.__db = db

    # Other methods
    def clearCache(self) -> None:
        self.__transactions = []
        if self.__transactionMapper:
            self.__transactionMapper = None