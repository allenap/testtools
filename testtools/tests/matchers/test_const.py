# Copyright (c) 2016 testtools developers. See LICENSE for details.

from typing import ClassVar

from testtools import TestCase
from testtools.matchers import Always, Never
from testtools.tests.matchers.helpers import TestMatchersInterface


class TestAlwaysInterface(TestMatchersInterface, TestCase):
    """:py:func:`~testtools.matchers.Always` always matches."""

    matches_matcher = Always()
    matches_matches: ClassVar[list] = [42, object(), "hi mom"]
    matches_mismatches: ClassVar[list] = []

    str_examples: ClassVar[list] = [("Always()", Always())]
    describe_examples: ClassVar[list] = []


class TestNeverInterface(TestMatchersInterface, TestCase):
    """:py:func:`~testtools.matchers.Never` never matches."""

    matches_matcher = Never()
    matches_matches: ClassVar[list] = []
    matches_mismatches: ClassVar[list] = [42, object(), "hi mom"]

    str_examples: ClassVar[list] = [("Never()", Never())]
    describe_examples: ClassVar[list] = [("Inevitable mismatch on 42", 42, Never())]


def test_suite():
    from unittest import TestLoader

    return TestLoader().loadTestsFromName(__name__)
