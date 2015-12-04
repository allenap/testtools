# Copyright (c) 2015 testtools developers. See LICENSE for details.

"""A collection of sample TestCases.

These are primarily of use in testing the test framework.
"""

from testtools import TestCase
from testtools.matchers import (
    AfterPreprocessing,
    Contains,
    Equals,
    MatchesDict,
    MatchesListwise,
)


class _ConstructedTest(TestCase):
    """A test case where all of the stages."""

    def __init__(self, test_method_name, set_up=None, test_body=None,
                 tear_down=None, cleanups=()):
        """Construct a ``_ConstructedTest``.

        All callables are unary callables that receive this test as their
        argument.

        :param str test_method_name: The name of the test method.
        :param callable set_up: Implementation of setUp.
        :param callable test_body: Implementation of the actual test.
            Will be assigned to the test method.
        :param callable tear_down: Implementation of tearDown.
        :param cleanups: Iterable of callables that will be added as
            cleanups.
        """
        setattr(self, test_method_name, test_body)
        super(_ConstructedTest, self).__init__(test_method_name)
        self._set_up = set_up if set_up else _do_nothing
        self._test_body = test_body if test_body else _do_nothing
        self._tear_down = tear_down if tear_down else _do_nothing
        self._cleanups = cleanups

    def setUp(self):
        super(_ConstructedTest, self).setUp()
        for cleanup in self._cleanups:
            self.addCleanup(cleanup, self)
        self._set_up(self)

    def test_case(self):
        self._test_body(self)

    def tearDown(self):
        self._tear_down(self)
        super(_ConstructedTest, self).tearDown()


def _do_nothing(case):
    pass


def _success(case):
    pass


def _error(case):
    1/0  # arbitrary non-failure exception


def _failure(case):
    case.fail('arbitrary failure')


def _skip(case):
    case.skip('arbitrary skip message')


def _expected_failure(case):
    case.expectFailure('arbitrary expected failure', _failure, case)


def _unexpected_success(case):
    case.expectFailure('arbitrary unexpected success', _success)


class _TearDownFails(TestCase):
    """Passing test case with failing tearDown after upcall."""

    def test_success(self):
        pass

    def tearDown(self):
        super(_TearDownFails, self).tearDown()
        1/0


class _SetUpFailsOnGlobalState(TestCase):
    """Fail to upcall setUp on first run. Fail to upcall tearDown after.

    This simulates a test that fails to upcall in ``setUp`` if some global
    state is broken, and fails to call ``tearDown`` when the global state
    breaks but works after that.
    """

    first_run = True

    def setUp(self):
        if not self.first_run:
            return
        super(_SetUpFailsOnGlobalState, self).setUp()

    def test_success(self):
        pass

    def tearDown(self):
        if not self.first_run:
            super(_SetUpFailsOnGlobalState, self).tearDown()
        self.__class__.first_run = False

    @classmethod
    def make_scenario(cls):
        case = cls('test_success')
        return {
            'case': case,
            'expected_first_result': _test_error_traceback(
                case, Contains('TestCase.tearDown was not called')),
            'expected_second_result': _test_error_traceback(
                case, Contains('TestCase.setUp was not called')),
        }


def _test_error_traceback(case, traceback_matcher):
    """Match result log of single test that errored out.

    ``traceback_matcher`` is applied to the text of the traceback.
    """
    return MatchesListwise([
        Equals(('startTest', case)),
        MatchesListwise([
            Equals('addError'),
            Equals(case),
            MatchesDict({
                'traceback': AfterPreprocessing(
                    lambda x: x.as_text(),
                    traceback_matcher,
                )
            })
        ]),
        Equals(('stopTest', case)),
    ])


"""
A list that can be used with testscenarios to test every deterministic sample
case that we have.
"""
deterministic_sample_cases_scenarios = [
    ('simple-success-test', {
        'case': _ConstructedTest('test_success', test_body=_success)
    }),
    ('simple-error-test', {
        'case': _ConstructedTest('test_error', test_body=_error)
    }),
    ('simple-failure-test', {
        'case': _ConstructedTest('test_failure', test_body=_failure)
    }),
    ('simple-expected-failure-test', {
        'case': _ConstructedTest('test_failure', test_body=_expected_failure)
    }),
    ('simple-unexpected-success-test', {
        'case': _ConstructedTest('test_failure', test_body=_unexpected_success)
    }),
    ('simple-skip-test', {
        'case': _ConstructedTest('test_failure', test_body=_skip)
    }),
    ('teardown-fails', {'case': _TearDownFails('test_success')}),
]


"""
A list that can be used with testscenarios to test every non-deterministic
sample case that we have.
"""
nondeterministic_sample_cases_scenarios = [
    ('setup-fails-global-state', _SetUpFailsOnGlobalState.make_scenario()),
]
