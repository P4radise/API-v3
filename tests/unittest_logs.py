import json
from unittest import TextTestResult as baseTextTestResult
from unittest import TextTestRunner as baseTextTestRunner

from onevizion import IntegrationLog, LogLevel

from module import ModuleError, OVAccessParameters


class TextTestResult(baseTextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open('settings.json', 'rb') as settings_file:
            settings_data = json.loads(settings_file.read().decode('utf-8'))

        ov_access_parameters = OVAccessParameters(settings_data['ovUrl'],
                                                  settings_data['ovAccessKey'],
                                                  settings_data['ovSecretKey'])

        with open('ihub_parameters.json', 'rb') as ihub_parameters_file:
            module_data = json.loads(ihub_parameters_file.read().decode('utf-8'))

        self._module_log = IntegrationLog(
            module_data['processId'], ov_access_parameters.ov_url_without_protocol,
            ov_access_parameters.ov_access_key, ov_access_parameters.ov_secret_key,
            None, True, module_data['logLevel']
        )

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._module_log.add(LogLevel.INFO, f'[FAIL] {str(test)}', str(err[1]))

    def addError(self, test, err):
        super().addError(test, err)
        self._module_log.add(LogLevel.ERROR, f'[ERROR] {str(test)}', str(err[1]))

    def addSuccess(self, test):
        super().addSuccess(test)
        self._module_log.add(LogLevel.INFO, f'[OK] {str(test)}')


class TextTestRunner(baseTextTestRunner):
    resultclass = TextTestResult
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, test):
        result = super().run(test)
        if not result.wasSuccessful():
            raise ModuleError('Not all tests were completed without errors',
                              ", ".join(self._get_types_of_failed_tests(result)))

    def _get_types_of_failed_tests(self, result) -> list:
        types_of_failed_tests = []
        failed, errored = len(result.failures), len(result.errors)
        if failed:
            types_of_failed_tests.append(f'failures={failed}')
        if errored:
            types_of_failed_tests.append(f'errors={errored}')
        return types_of_failed_tests
