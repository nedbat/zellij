"""Pytest initialization"""

from hypothesis import settings

# To really run a lot of Hypothesis:
# pytest --hypothesis-profile=crazy --hypothesis-show-statistics
settings.register_profile("crazy", settings(max_examples=100000, timeout=600))
