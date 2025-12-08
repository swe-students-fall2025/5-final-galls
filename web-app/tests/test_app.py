"""Unit tests for the Flask app routes."""

import os
import sys
import json
from unittest.mock import patch

# from requests.exceptions import RequestException

import pytest  # pylint: disable=import-error

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # pylint: disable=C0413,E0401

def test_mock():
    assert True