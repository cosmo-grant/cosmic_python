# pytest: disable=redefined-outer-name
import sqlite3

import pytest

from db_tables import Schema


@pytest.fixture
def session():
    con = sqlite3.connect(":memory:")
    Schema(con).create_all()
    yield con
