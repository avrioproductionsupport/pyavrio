from enum import Enum, unique
from typing import Iterable

import pyavrio.client
import pyavrio.exceptions
import pyavrio.logging
from pyavrio import constants

logger = pyavrio.logging.get_logger(__name__)


NO_TRANSACTION = "NONE"
START_TRANSACTION = "START TRANSACTION"
ROLLBACK = "ROLLBACK"
COMMIT = "COMMIT"


@unique
class IsolationLevel(Enum):
    AUTOCOMMIT = 0
    READ_UNCOMMITTED = 1
    READ_COMMITTED = 2
    REPEATABLE_READ = 3
    SERIALIZABLE = 4

    @classmethod
    def levels(cls) -> Iterable[str]:
        return {isolation_level.name for isolation_level in IsolationLevel}

    @classmethod
    def values(cls) -> Iterable[int]:
        return {isolation_level.value for isolation_level in IsolationLevel}

    @classmethod
    def check(cls, level: int) -> int:
        if level not in cls.values():
            raise ValueError("invalid isolation level {}".format(level))
        return level


class Transaction(object):
    def __init__(self, request: pyavrio.client.TrinoRequest) -> None:
        self._request = request
        self._id = NO_TRANSACTION

    @property
    def id(self) -> str:
        return self._id

    @property
    def request(self) -> pyavrio.client.TrinoRequest:
        return self._request

    def begin(self) -> None:
        response = self._request.post(START_TRANSACTION)
        if not response.ok:
            raise pyavrio.exceptions.DatabaseError(
                "failed to start transaction: {}".format(response.status_code)
            )
        transaction_id = response.headers.get(constants.HEADER_STARTED_TRANSACTION)
        if transaction_id and transaction_id != NO_TRANSACTION:
            self._id = response.headers[constants.HEADER_STARTED_TRANSACTION]
        status = self._request.process(response)
        while status.next_uri:
            response = self._request.get(status.next_uri)
            transaction_id = response.headers.get(constants.HEADER_STARTED_TRANSACTION)
            if transaction_id and transaction_id != NO_TRANSACTION:
                self._id = response.headers[constants.HEADER_STARTED_TRANSACTION]
            status = self._request.process(response)
        self._request.transaction_id = self._id
        logger.info("transaction started: %s", self._id)

    def commit(self) -> None:
        query = pyavrio.client.TrinoQuery(self._request, COMMIT)
        try:
            list(query.execute())
        except Exception as err:
            raise pyavrio.exceptions.DatabaseError(
                "failed to commit transaction {}: {}".format(self._id, err)
            )
        self._id = NO_TRANSACTION
        self._request.transaction_id = self._id

    def rollback(self) -> None:
        query = pyavrio.client.TrinoQuery(self._request, ROLLBACK)
        try:
            list(query.execute())
        except Exception as err:
            raise pyavrio.exceptions.DatabaseError(
                "failed to rollback transaction {}: {}".format(self._id, err)
            )
        self._id = NO_TRANSACTION
        self._request.transaction_id = self._id
