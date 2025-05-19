from .Transaction import Transaction
from typing import List
from backend.db.Database import Database
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TransactionMapper:
    __transactionObjects = []

    def getTransactionObjects(self, db: Database, rebuildObjects: bool = False) -> List[Transaction]:
        if len(self.__transactionObjects) == 0 or rebuildObjects:
            self.__transactionObjects = []

            query = (
                "SELECT id, fk_user, fk_campsite, fk_module, price, moneyCurrency, dateOfTransaction "
                "FROM transaction"
            )
            selectedTransactions = db.execute(query)
            logger.debug(f"Query returned {len(selectedTransactions)} transactions")

            for transactionTuple in selectedTransactions:
                transactionObject = Transaction()
                transactionObject.setId(transactionTuple[0])
                transactionObject.setUserId(transactionTuple[1])
                transactionObject.setCampsiteId(transactionTuple[2])
                transactionObject.setModuleId(transactionTuple[3])
                transactionObject.setPrice(transactionTuple[4])
                transactionObject.setMoneyCurrency(transactionTuple[5])
                transactionObject.setDateOfTransaction(transactionTuple[6])

                self.__transactionObjects.append(transactionObject)
                logger.debug(f"Created transaction: ID {transactionObject.getId()}")

        return self.__transactionObjects

    def getTransactionsByUserId(self, user_id: int, db: Database) -> List[Transaction]:
        transactions = []
        query = (
            "SELECT id, fk_user, fk_campsite, fk_module, price, moneyCurrency, dateOfTransaction "
            "FROM transaction "
            "WHERE fk_user = %s"
        )
        selectedTransactions = db.execute(query, (user_id,))
        logger.debug(f"Query returned {len(selectedTransactions)} transactions for user_id {user_id}")

        for transactionTuple in selectedTransactions:
            transactionObject = Transaction()
            transactionObject.setId(transactionTuple[0])
            transactionObject.setUserId(transactionTuple[1])
            transactionObject.setCampsiteId(transactionTuple[2])
            transactionObject.setModuleId(transactionTuple[3])
            transactionObject.setPrice(transactionTuple[4])
            transactionObject.setMoneyCurrency(transactionTuple[5])
            transactionObject.setDateOfTransaction(transactionTuple[6])
            transactions.append(transactionObject)

        return transactions

    def getTransactionsByCampsiteId(self, campsite_id: int, db: Database) -> List[Transaction]:
        transactions = []
        query = (
            "SELECT id, fk_user, fk_campsite, fk_module, price, moneyCurrency, dateOfTransaction "
            "FROM transaction "
            "WHERE fk_campsite = %s"
        )
        selectedTransactions = db.execute(query, (campsite_id,))
        logger.debug(f"Query returned {len(selectedTransactions)} transactions for fk_campsite {campsite_id}")

        for transactionTuple in selectedTransactions:
            transactionObject = Transaction()
            transactionObject.setId(transactionTuple[0])
            transactionObject.setUserId(transactionTuple[1])
            transactionObject.setCampsiteId(transactionTuple[2])
            transactionObject.setModuleId(transactionTuple[3])
            transactionObject.setPrice(transactionTuple[4])
            transactionObject.setMoneyCurrency(transactionTuple[5])
            transactionObject.setDateOfTransaction(transactionTuple[6])
            transactions.append(transactionObject)

        return transactions