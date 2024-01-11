import argparse
from unittest import TestSuite, makeSuite

from module import OVAccessParameters
from tests import ImportTestCase, TrackorTestCase, WorkplanTestCase
from unittest_logs import TextTestRunner

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--ov_url', type=str)
parser.add_argument('-a', '--ov_access_key', type=str)
parser.add_argument('-s', '--ov_secret_key', type=str)
args = parser.parse_args()

ov_access_parameters = OVAccessParameters(args.ov_url,
                                          args.ov_access_key,
                                          args.ov_secret_key)

test_suite = TestSuite()
test_suite.addTests(makeSuite(TrackorTestCase))
test_suite.addTests(makeSuite(WorkplanTestCase))
test_suite.addTests(makeSuite(ImportTestCase))

TextTestRunner().run(test_suite)
