import abc
from typing import Any, Tuple

from requests import PreparedRequest, Session
from requests.auth import AuthBase

import pyavrio.logging

logger = pyavrio.logging.get_logger(__name__)


class Authentication(metaclass=abc.ABCMeta):
    """
    Abstract base class for authentication mechanisms.
    """
    @abc.abstractmethod
    def set_http_session(self, http_session: Session) -> Session:
        pass

    def get_exceptions(self) -> Tuple[Any, ...]:
        return tuple()


class AvrioAuthentication(Authentication):
    """
    Implementation of Authentication class for Avrio authentication.
    """
    def __init__(self, token: str):
        self.token = token

    def set_http_session(self, http_session: Session) -> Session:
        """
        Method to set HTTP session with Avrio authentication.
        
        Parameters:
            http_session (Session): The HTTP session to set authentication.
        
        Returns:
            Session: The HTTP session with Avrio authentication set.
        """
        http_session.auth = _BearerAuth(self.token)
        return http_session

    def get_exceptions(self) -> Tuple[Any, ...]:
        return ()

    def __eq__(self, other: object) -> bool:
        """
        Equality comparison method for AvrioAuthentication instances.
        
        Parameters:
            other (object): The object to compare with.
        
        Returns:
            bool: True if equal, False otherwise.
        """
        if not isinstance(other, AvrioAuthentication):
            return False
        return self.token == other.token


class _BearerAuth(AuthBase):
    """
    Custom implementation of Authentication class for bearer token
    """

    def __init__(self, token: str):
        self.token = token

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers["Authorization"] = "Bearer " + self.token
        return r
