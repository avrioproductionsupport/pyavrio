from sqlalchemy.dialects import registry
from .util import _url as URL


registry.register("pyavrio", "pyavrio.sqlalchemy.dialect", "TrinoDialect")

