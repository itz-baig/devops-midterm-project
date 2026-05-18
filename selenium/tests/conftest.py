"""
conftest.py — pytest configuration for Quick-Task Hub Selenium test suite.

The `driver` fixture is defined in test_suite.py at module scope.
This file ensures pytest resolves the fixture correctly when TC-04
mixes Selenium driver tests with pure requests-based API tests.
"""
