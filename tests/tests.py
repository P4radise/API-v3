import json
import os
from copy import deepcopy
from datetime import date, datetime, timedelta
from time import sleep
from typing import Any, Dict, List
from unittest import TestCase

from onevizion import IntegrationLog, LogLevel

from module import OVAccessParameters, OVImport, OVTrackor, OVWorkplan
from module_error import ModuleError


class WorkplanTestCase(TestCase):
    #region constants
    ASSIGN_WP_1_TRACKOR_KEY = 'Assign-WP-1'
    GET_WP_ID_1_TRACKOR_KEY = 'Get-Wp-Id-1'
    UPDATE_TASK_1_TRACKOR_KEY = 'Update-Task-1'

    YEAR_MONTH_DAY_DATE_FORMAT = '%Y-%m-%d'

    WP_ID = 'id'
    WP_NAME = 'name'
    WP_TEMPLATE_NAME = 'template_name'
    WP_START_DATE = 'proj_start_date'
    WP_FINISH_DATE = 'proj_finish_date'
    WP_TEMPLATE = 'Test WorkPlan'
    WP_TRACKOR_ID = 'trackor_id'
    WP_ACTIVE = 'active'
    WP_ASSIGN_ACTIVE_NAME = 'Assign Test Workplan Active'
    WP_ASSIGN_NOT_ACTIVE_NAME = 'Assign Test Workplan Not Active'
    WP_GET_WP_ID_NAME = 'Get-Wp-Id-Test WorkPlan'
    TASK_ORDER_NUMBER_1 = '1'
    TASK_ORDER_NUMBER_2 = '2'
    TASK_ID = 'id'

    BASELINE_S = 'baseline_start_date'
    BASELINE_F = 'baseline_finish_date'
    PROJECTED_S = 'projected_start_date'
    PROJECTED_F = 'projected_finish_date'
    ACTUAL_S = 'actual_start_date'
    ACTUAL_F = 'actual_finish_date'
    DYNAMIC_DATES = 'dynamic_dates'
    DYNAMIC_S = 'start_date'
    DYNAMIC_F = 'finish_date'
    DYNAMIC_DATE_TYPE_ID = 'date_type_id'

    DYNAMIC_DATES_LIST_WITH_EMPTY_DATES = [
        {
            'label': 'Month 1',
            'date_type_id': None,
            'start_date': None,
            'finish_date': None
        }, {
            'label': 'Week 1',
            'date_type_id': None,
            'start_date': None,
            'finish_date': None
        }
    ]

    PARENT_TRACKOR_TYPE = 'VHMPYAPI_ParentTrackor'
    PARENT_TRACKOR_ID = 'TRACKOR_ID'
    PARENT_TRACKOR_KEY = 'TRACKOR_KEY'
    #endregion

    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'rb') as settings_file:
            settings_data = json.loads(settings_file.read().decode('utf-8'))

        ov_access_parameters = OVAccessParameters(settings_data['ovUrl'],
                                                  settings_data['ovAccessKey'],
                                                  settings_data['ovSecretKey'])

        cls._ov_parent_trackor = OVTrackor(ov_access_parameters,
                                           WorkplanTestCase.PARENT_TRACKOR_TYPE)
        cls._ov_workplan = OVWorkplan(ov_access_parameters)
        cls._current_date = date.today()
        cls._current_date_str = date.today().strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT)

        with open('ihub_parameters.json', 'rb') as ihub_parameters_file:
            module_data = json.loads(ihub_parameters_file.read().decode('utf-8'))

        cls._module_log = IntegrationLog(
            module_data['processId'], ov_access_parameters.ov_url_without_protocol,
            ov_access_parameters.ov_access_key, ov_access_parameters.ov_secret_key,
            None, True, module_data['logLevel']
        )

    def setUp(self):
        self._module_log.add(LogLevel.INFO, f'{datetime.now()} {self._testMethodName} start')

    def tearDown(self):
        self._module_log.add(LogLevel.INFO, f'{datetime.now()} {self._testMethodName} finish')

    def test_assign_workplan(self):
        trackor_id = self._get_trackor_id(WorkplanTestCase.ASSIGN_WP_1_TRACKOR_KEY)

        workplan_active_with_current_date = self._ov_parent_trackor.assign_workplan(trackor_id,
                                                                                    WorkplanTestCase.WP_TEMPLATE,
                                                                                    WorkplanTestCase.WP_ASSIGN_ACTIVE_NAME,
                                                                                    True,
                                                                                    self._current_date_str)
        self._check_wp_names_are_equal(workplan_active_with_current_date[WorkplanTestCase.WP_NAME],
                                       WorkplanTestCase.WP_ASSIGN_ACTIVE_NAME)
        self._check_wp_template_names_are_equal(workplan_active_with_current_date[WorkplanTestCase.WP_TEMPLATE_NAME],
                                                WorkplanTestCase.WP_TEMPLATE)
        self._check_wp_start_dates_are_equal(workplan_active_with_current_date[WorkplanTestCase.WP_START_DATE],
                                             self._current_date_str)
        self._check_wp_finish_dates_are_equal(workplan_active_with_current_date[WorkplanTestCase.WP_FINISH_DATE],
                                              (self._current_date + timedelta(2)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        self._check_wp_trackor_ids_are_equal(workplan_active_with_current_date[WorkplanTestCase.WP_TRACKOR_ID],
                                             trackor_id)
        self.assertTrue(workplan_active_with_current_date[WorkplanTestCase.WP_ACTIVE])

        workplan_not_active_with_next_date = self._ov_parent_trackor.assign_workplan(trackor_id,
                                                                                     WorkplanTestCase.WP_TEMPLATE,
                                                                                     WorkplanTestCase.WP_ASSIGN_NOT_ACTIVE_NAME,
                                                                                     False,
                                                                                     None,
                                                                                     (self._current_date + timedelta(5)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        self._check_wp_names_are_equal(workplan_not_active_with_next_date[WorkplanTestCase.WP_NAME],
                                       WorkplanTestCase.WP_ASSIGN_NOT_ACTIVE_NAME)
        self._check_wp_template_names_are_equal(workplan_not_active_with_next_date[WorkplanTestCase.WP_TEMPLATE_NAME],
                                                WorkplanTestCase.WP_TEMPLATE)
        self._check_wp_start_dates_are_equal(workplan_not_active_with_next_date[WorkplanTestCase.WP_START_DATE],
                                             (self._current_date + timedelta(3)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        self._check_wp_finish_dates_are_equal(workplan_not_active_with_next_date[WorkplanTestCase.WP_FINISH_DATE],
                                              (self._current_date + timedelta(5)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        self._check_wp_trackor_ids_are_equal(workplan_not_active_with_next_date[WorkplanTestCase.WP_TRACKOR_ID],
                                             trackor_id)
        self.assertFalse(workplan_not_active_with_next_date[WorkplanTestCase.WP_ACTIVE])

    def test_get_workplan(self):
        actual_workplan_id = self._ov_workplan.get_workplan_id(self._get_trackor_id(WorkplanTestCase.GET_WP_ID_1_TRACKOR_KEY),
                                                               WorkplanTestCase.WP_TEMPLATE)
        workplan_data = self._ov_workplan.get_workplan_by_workplan_id(actual_workplan_id)
        self._check_wp_names_are_equal(workplan_data[WorkplanTestCase.WP_NAME],
                                       WorkplanTestCase.WP_GET_WP_ID_NAME)

    def test_update_task(self):
        yesterday_date_str = (self._current_date - timedelta(1)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT)
        tomorrow_date_str = (self._current_date + timedelta(1)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT)

        workplan_id = self._ov_workplan.get_workplan_id(self._get_trackor_id(WorkplanTestCase.UPDATE_TASK_1_TRACKOR_KEY),
                                                        WorkplanTestCase.WP_TEMPLATE)
        task_first = self._ov_workplan.get_task_by_order_number(workplan_id,
                                                                WorkplanTestCase.TASK_ORDER_NUMBER_1)

        expected_dynamic_dates_before_update = self._update_dynamic_date_type_ids(deepcopy(WorkplanTestCase.DYNAMIC_DATES_LIST_WITH_EMPTY_DATES),
                                                                                  task_first[WorkplanTestCase.DYNAMIC_DATES]) 
        self._check_task_dates_are_equal(task_first[WorkplanTestCase.BASELINE_S],
                                         self._current_date_str)
        self._check_task_dates_are_equal(task_first[WorkplanTestCase.BASELINE_F],
                                         tomorrow_date_str)
        self._check_task_dates_are_equal(task_first[WorkplanTestCase.PROJECTED_S],
                                         self._current_date_str)
        self._check_task_dates_are_equal(task_first[WorkplanTestCase.PROJECTED_F],
                                         tomorrow_date_str)
        self._check_task_dates_are_equal(task_first[WorkplanTestCase.ACTUAL_S],
                                         None)
        self._check_task_dates_are_equal(task_first[WorkplanTestCase.ACTUAL_F],
                                         None)
        self._check_task_dynamic_dates_are_equal(task_first[WorkplanTestCase.DYNAMIC_DATES][0],
                                                 expected_dynamic_dates_before_update[0])
        self._check_task_dynamic_dates_are_equal(task_first[WorkplanTestCase.DYNAMIC_DATES][1],
                                                 expected_dynamic_dates_before_update[1])

        expected_dynamic_dates_after_update = self._update_dynamic_dates(expected_dynamic_dates_before_update,
                                                                         (self._current_date + timedelta(3)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT),
                                                                         None,
                                                                         (self._current_date + timedelta(10)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT),
                                                                         (self._current_date + timedelta(20)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        task_first[WorkplanTestCase.ACTUAL_F] = yesterday_date_str
        task_first[WorkplanTestCase.DYNAMIC_DATES] = expected_dynamic_dates_after_update

        task_id = task_first[WorkplanTestCase.TASK_ID]
        self._ov_workplan.update_task(task_id, task_first, [])

        task_first_updated = self._ov_workplan.get_task_by_task_id(task_id)
        self._check_task_dates_are_equal(task_first_updated[WorkplanTestCase.BASELINE_S],
                                         self._current_date_str)
        self._check_task_dates_are_equal(task_first_updated[WorkplanTestCase.BASELINE_F],
                                         tomorrow_date_str)
        self._check_task_dates_are_equal(task_first_updated[WorkplanTestCase.PROJECTED_S],
                                         (self._current_date - timedelta(2)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        self._check_task_dates_are_equal(task_first_updated[WorkplanTestCase.PROJECTED_F],
                                         yesterday_date_str)
        self._check_task_dates_are_equal(task_first_updated[WorkplanTestCase.ACTUAL_S],
                                         (self._current_date - timedelta(2)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        self._check_task_dates_are_equal(task_first_updated[WorkplanTestCase.ACTUAL_F],
                                         yesterday_date_str)
        self._check_task_dynamic_dates_are_equal(task_first_updated[WorkplanTestCase.DYNAMIC_DATES][0],
                                                 expected_dynamic_dates_after_update[0])
        self._check_task_dynamic_dates_are_equal(task_first_updated[WorkplanTestCase.DYNAMIC_DATES][1],
                                                 expected_dynamic_dates_after_update[1])

    def test_update_task_partial(self):
        day_before_yesterday_str = (self._current_date - timedelta(2)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT)
        day_after_tomorrow_str = (self._current_date + timedelta(2)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT)

        workplan_id = self._ov_workplan.get_workplan_id(self._get_trackor_id(WorkplanTestCase.UPDATE_TASK_1_TRACKOR_KEY),
                                                        WorkplanTestCase.WP_TEMPLATE)
        task_second = self._ov_workplan.get_task_by_order_number(workplan_id,
                                                                 WorkplanTestCase.TASK_ORDER_NUMBER_2)

        expected_dynamic_dates_before_update = self._update_dynamic_date_type_ids(deepcopy(WorkplanTestCase.DYNAMIC_DATES_LIST_WITH_EMPTY_DATES),
                                                                                  task_second[WorkplanTestCase.DYNAMIC_DATES]) 
        self._check_task_dates_are_equal(task_second[WorkplanTestCase.BASELINE_S],
                                         self._current_date_str)
        self._check_task_dates_are_equal(task_second[WorkplanTestCase.BASELINE_F],
                                         day_after_tomorrow_str)
        self._check_task_dates_are_equal(task_second[WorkplanTestCase.PROJECTED_S],
                                         self._current_date_str)
        self._check_task_dates_are_equal(task_second[WorkplanTestCase.PROJECTED_F],
                                         day_after_tomorrow_str)
        self._check_task_dates_are_equal(task_second[WorkplanTestCase.ACTUAL_S],
                                         None)
        self._check_task_dates_are_equal(task_second[WorkplanTestCase.ACTUAL_F],
                                         None)
        self._check_task_dynamic_dates_are_equal(task_second[WorkplanTestCase.DYNAMIC_DATES][0],
                                                 expected_dynamic_dates_before_update[0])
        self._check_task_dynamic_dates_are_equal(task_second[WorkplanTestCase.DYNAMIC_DATES][1],
                                                 expected_dynamic_dates_before_update[1])

        expected_dynamic_dates_after_update = self._update_dynamic_dates(expected_dynamic_dates_before_update,
                                                                         None,
                                                                         (self._current_date + timedelta(4)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT),
                                                                         (self._current_date - timedelta(5)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT),
                                                                         (self._current_date - timedelta(4)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        task_id = task_second[WorkplanTestCase.TASK_ID]
        task_fields_dict = {
            WorkplanTestCase.ACTUAL_F: day_before_yesterday_str
        }
        self._ov_workplan.update_task_partial(task_id,
                                              task_fields_dict,
                                              expected_dynamic_dates_after_update)

        task_second_updated = self._ov_workplan.get_task_by_task_id(task_id)
        self._check_task_dates_are_equal(task_second_updated[WorkplanTestCase.BASELINE_S],
                                         self._current_date_str)
        self._check_task_dates_are_equal(task_second_updated[WorkplanTestCase.BASELINE_F],
                                         day_after_tomorrow_str)
        self._check_task_dates_are_equal(task_second_updated[WorkplanTestCase.PROJECTED_S],
                                         (self._current_date - timedelta(4)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        self._check_task_dates_are_equal(task_second_updated[WorkplanTestCase.PROJECTED_F],
                                         day_before_yesterday_str)
        self._check_task_dates_are_equal(task_second_updated[WorkplanTestCase.ACTUAL_S],
                                         (self._current_date - timedelta(4)).strftime(WorkplanTestCase.YEAR_MONTH_DAY_DATE_FORMAT))
        self._check_task_dates_are_equal(task_second_updated[WorkplanTestCase.ACTUAL_F],
                                         day_before_yesterday_str)
        self._check_task_dynamic_dates_are_equal(task_second_updated[WorkplanTestCase.DYNAMIC_DATES][0],
                                                 expected_dynamic_dates_after_update[0])
        self._check_task_dynamic_dates_are_equal(task_second_updated[WorkplanTestCase.DYNAMIC_DATES][1],
                                                 expected_dynamic_dates_after_update[1])

    def _update_dynamic_date_type_ids(self, dynamic_dates: List[Dict[str, Any]], actual_dynamic_dates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        dynamic_dates[0][WorkplanTestCase.DYNAMIC_DATE_TYPE_ID] = actual_dynamic_dates[0][WorkplanTestCase.DYNAMIC_DATE_TYPE_ID]
        dynamic_dates[1][WorkplanTestCase.DYNAMIC_DATE_TYPE_ID] = actual_dynamic_dates[1][WorkplanTestCase.DYNAMIC_DATE_TYPE_ID]
        return dynamic_dates

    def _update_dynamic_dates(self, dynamic_dates: List[Dict[str, Any]], first_dynamic_s_date: Any,
                              first_dynamic_f_date: Any, second_dynamic_s_date: Any,
                              second_dynamic_f_date: Any) -> List[Dict[str, Any]]:
        dynamic_dates[0][WorkplanTestCase.DYNAMIC_S] = first_dynamic_s_date
        dynamic_dates[0][WorkplanTestCase.DYNAMIC_F] = first_dynamic_f_date
        dynamic_dates[1][WorkplanTestCase.DYNAMIC_S] = second_dynamic_s_date
        dynamic_dates[1][WorkplanTestCase.DYNAMIC_F] = second_dynamic_f_date
        return dynamic_dates

    def _check_wp_names_are_equal(self, actual_wp_name: str, expected_wp_name: str):
        self.assertEqual(actual_wp_name, expected_wp_name, 'WP names are not equal.')

    def _check_wp_template_names_are_equal(self, actual_wp_template_name: str, expected_wp_template_name: str):
        self.assertEqual(actual_wp_template_name, expected_wp_template_name, 'WP template names are not equal.')

    def _check_wp_start_dates_are_equal(self, actual_wp_start_date: str, expected_wp_start_date: str):
        self.assertEqual(actual_wp_start_date, expected_wp_start_date, 'WP start dates are not equal.')

    def _check_wp_finish_dates_are_equal(self, actual_wp_finish_date: str, expected_wp_finish_date: str):
        self.assertEqual(actual_wp_finish_date, expected_wp_finish_date, 'WP finish dates are not equal.')

    def _check_wp_trackor_ids_are_equal(self, actual_wp_trackor_id: str, expected_wp_trackor_id: str):
        self.assertEqual(actual_wp_trackor_id, expected_wp_trackor_id, 'WP trackor ids are not equal.')

    def _check_task_dates_are_equal(self, actual_date: str, expected_date: Any):
        self.assertEqual(actual_date, expected_date, 'Task dates are not equal.')

    def _check_task_dynamic_dates_are_equal(self, actual_dynamic_dates: Dict[str, Any], expected_dynamic_dates: Dict[str, Any]):
        self.assertEqual(actual_dynamic_dates, expected_dynamic_dates, 'Task dynamic dates are not equal.')

    def _get_trackor_id(self, trackor_key: str) -> int:
        parent_filters_dict = {
            f'{WorkplanTestCase.PARENT_TRACKOR_TYPE}.{WorkplanTestCase.PARENT_TRACKOR_KEY}': trackor_key
        }
        parent_get_trackor = self._ov_parent_trackor.get_trackor_by_filters_dict(parent_filters_dict)
        return parent_get_trackor[0][WorkplanTestCase.PARENT_TRACKOR_ID]


class TrackorTestCase(TestCase):
    #region constants
    UPLOAD_FILE_1_TRACKOR_KEY = 'Upload-File-1'
    UPLOAD_FILE_BY_FILE_CONTENTS_1_TRACKOR_KEY = 'Upload-File-By-File-Contents-1'
    GET_FILE_BY_FIELDNAME_1_TRACKOR_KEY = 'Get-File-By-Fieldname-1'
    GET_FILE_BY_BLOB_1_TRACKOR_KEY = 'Get-File-By-Blob-1'
    CREATE_PARENT_TRACKOR_1_TRACKOR_KEY = 'Create-Parent-Trackor-1'
    CREATE_CHILD_TRACKOR_1_TRACKOR_KEY = 'Create-Child-Trackor-1'
    UPDATE_TRACKOR_1_TRACKOR_KEY = 'Update-Trackor-1'
    DELETE_TRACKOR_1_TRACKOR_KEY = 'Delete-Trackor-1'

    PARENT_TRACKOR_TYPE = 'VHMPYAPI_ParentTrackor'
    PARENT_TRACKOR_ID = 'TRACKOR_ID'
    PARENT_TRACKOR_KEY = 'TRACKOR_KEY'
    PARENT_FIELD_TEXT = 'PYAPI_PT_TEXT'
    PARENT_FIELD_NUMBER = 'PYAPI_PT_NUMBER'
    PARENT_FIELD_EFILE = 'PYAPI_PT_EFILE'
    PARENT_TRACKOR_ID_WITH_TRACKOR_TYPE = f'{PARENT_TRACKOR_TYPE}.{PARENT_TRACKOR_ID}'

    CHILD_TRACKOR_TYPE = 'VHMPYAPI_ChildTrackor'
    CHILD_TRACKOR_ID = 'TRACKOR_ID'
    CHILD_TRACKOR_KEY = 'TRACKOR_KEY'
    CHILD_FIELD_TEXT = 'PYAPI_CT_TEXT'
    CHILD_FIELD_NUMBER = 'PYAPI_CT_NUMBER'
    CHILD_TRACKOR_ID_WITH_TRACKOR_TYPE = f'{CHILD_TRACKOR_TYPE}.{CHILD_TRACKOR_ID}'

    PARENT_CREATE_TRACKOR_DICT = {
        PARENT_TRACKOR_KEY: CREATE_PARENT_TRACKOR_1_TRACKOR_KEY,
        PARENT_FIELD_NUMBER: '123',
        PARENT_FIELD_TEXT: 'Create-Parent-Trackor-Text-Value-1'
    }
    CHILD_CREATE_TRACKOR_DICT = {
        CHILD_TRACKOR_KEY: CREATE_CHILD_TRACKOR_1_TRACKOR_KEY,
        CHILD_FIELD_NUMBER: '456',
        CHILD_FIELD_TEXT: 'Create-Child-Trackor-Text-Value-1'
    }

    NUMBER_VALUE_BEFORE_UPDATE_TRACKOR = '123'
    NUMBER_VALUE_AFTER_UPDATE_TRACKOR = '789'
    TEXT_VALUE_BEFORE_UPDATE_TRACKOR = 'Update-Trackor-Text-Value-1'
    TEXT_VALUE_AFTER_UPDATE_TRACKOR = 'Update-Trackor-Text-Value-2'

    GET_FILES_FOLDER = 'get_files'
    UPLOAD_FILE_NAME = 'upload_test_file.txt'
    UPLOAD_FILE_NAME_PATH = 'upload_files/upload_test_file.txt'
    UPLOAD_NEW_FILE_NAME = 'upload_new_test_file.txt'
    GET_BY_FIELDNAME_FILE_NAME = 'get_file_by_fieldname_test.txt'
    GET_BY_FIELDNAME_FILE_DATA = 123
    GET_BY_BLOB_FILE_NAME = 'get_file_by_blob_test.txt'
    GET_BY_BLOB_FILE_DATA = 456

    FILE_DATA_123 = 'MTIz'
    FILE_DICT_DATA = 'data'
    FILE_DICT_FILE_NAME = 'file_name'
    FILE_DICT_EMPTY = {
        'data': None, 'file_name': None
    }
    #endregion

    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'rb') as settings_file:
            settings_data = json.loads(settings_file.read().decode('utf-8'))

        ov_access_parameters = OVAccessParameters(settings_data['ovUrl'],
                                                  settings_data['ovAccessKey'],
                                                  settings_data['ovSecretKey'])

        cls._ov_parent_trackor = OVTrackor(ov_access_parameters,
                                           TrackorTestCase.PARENT_TRACKOR_TYPE)
        cls._ov_child_trackor = OVTrackor(ov_access_parameters,
                                          TrackorTestCase.CHILD_TRACKOR_TYPE)

        with open('ihub_parameters.json', 'rb') as ihub_parameters_file:
            module_data = json.loads(ihub_parameters_file.read().decode('utf-8'))

        cls._module_log = IntegrationLog(
            module_data['processId'], ov_access_parameters.ov_url_without_protocol,
            ov_access_parameters.ov_access_key, ov_access_parameters.ov_secret_key,
            None, True, module_data['logLevel']
        )

    def setUp(self):
        self._module_log.add(LogLevel.INFO, f'{datetime.now()} {self._testMethodName} start')

    def tearDown(self):
        self._module_log.add(LogLevel.INFO, f'{datetime.now()} {self._testMethodName} finish')

    def test_upload_file(self):
        parent_trackor_id = self._get_trackor_id(TrackorTestCase.UPLOAD_FILE_1_TRACKOR_KEY)
        self._ov_parent_trackor.upload_file(parent_trackor_id,
                                            TrackorTestCase.PARENT_FIELD_EFILE,
                                            TrackorTestCase.UPLOAD_FILE_NAME_PATH,
                                            TrackorTestCase.UPLOAD_NEW_FILE_NAME)

        parent_fields_list = [TrackorTestCase.PARENT_FIELD_EFILE]
        parent_get_trackor = self._ov_parent_trackor.get_trackor_by_trackor_id(parent_trackor_id,
                                                                               parent_fields_list)

        expected_efile_field_value = deepcopy(TrackorTestCase.FILE_DICT_EMPTY)
        expected_efile_field_value[TrackorTestCase.FILE_DICT_DATA] = TrackorTestCase.FILE_DATA_123
        expected_efile_field_value[TrackorTestCase.FILE_DICT_FILE_NAME] = TrackorTestCase.UPLOAD_NEW_FILE_NAME
        self._check_file_dicts_are_equal(parent_get_trackor[TrackorTestCase.PARENT_FIELD_EFILE],
                                         expected_efile_field_value)

    def test_upload_file_by_file_contents(self):
        parent_trackor_id = self._get_trackor_id(TrackorTestCase.UPLOAD_FILE_BY_FILE_CONTENTS_1_TRACKOR_KEY)
        with open(TrackorTestCase.UPLOAD_FILE_NAME_PATH, 'rb') as file_path:
            self._ov_parent_trackor.upload_file_by_file_contents(parent_trackor_id,
                                                                 TrackorTestCase.PARENT_FIELD_EFILE,
                                                                 TrackorTestCase.UPLOAD_FILE_NAME,
                                                                 file_path)

        parent_fields_list = [TrackorTestCase.PARENT_FIELD_EFILE]
        parent_get_trackor = self._ov_parent_trackor.get_trackor_by_trackor_id(parent_trackor_id,
                                                                               parent_fields_list)

        expected_efile_field_value = deepcopy(TrackorTestCase.FILE_DICT_EMPTY)
        expected_efile_field_value[TrackorTestCase.FILE_DICT_DATA] = TrackorTestCase.FILE_DATA_123
        expected_efile_field_value[TrackorTestCase.FILE_DICT_FILE_NAME] = TrackorTestCase.UPLOAD_FILE_NAME
        self._check_file_dicts_are_equal(parent_get_trackor[TrackorTestCase.PARENT_FIELD_EFILE],
                                         expected_efile_field_value)

    def test_get_file(self):
        self._create_get_files_folder()
        current_directory = os.getcwd()
        os.chdir(f'{current_directory}/{TrackorTestCase.GET_FILES_FOLDER}')

        try:
            parent_trackor_id = self._get_trackor_id(TrackorTestCase.GET_FILE_BY_FIELDNAME_1_TRACKOR_KEY)
            actual_file_name_by_fieldname = self._ov_parent_trackor.get_file_by_fieldname(parent_trackor_id,
                                                                                          TrackorTestCase.PARENT_FIELD_EFILE)

            self._check_file_names_are_equal(actual_file_name_by_fieldname,
                                             TrackorTestCase.GET_BY_FIELDNAME_FILE_NAME)
            self._check_file_test_data_are_equal(actual_file_name_by_fieldname,
                                                 TrackorTestCase.GET_BY_FIELDNAME_FILE_DATA)

            parent_trackor_id = self._get_trackor_id(TrackorTestCase.GET_FILE_BY_BLOB_1_TRACKOR_KEY)
            parent_fields_list = [TrackorTestCase.PARENT_FIELD_NUMBER]
            parent_get_trackor = self._ov_parent_trackor.get_trackor_by_trackor_id(parent_trackor_id,
                                                                                   parent_fields_list)
            actual_file_name_by_blob = self._ov_parent_trackor.get_file_by_blob(parent_get_trackor[TrackorTestCase.PARENT_FIELD_NUMBER])

            self._check_file_names_are_equal(actual_file_name_by_blob,
                                             TrackorTestCase.GET_BY_BLOB_FILE_NAME)
            self._check_file_test_data_are_equal(actual_file_name_by_blob,
                                                 TrackorTestCase.GET_BY_BLOB_FILE_DATA)
        finally:
            os.chdir(current_directory)
            self._delete_received_files()

    def _create_get_files_folder(self):
        if not os.path.exists(TrackorTestCase.GET_FILES_FOLDER):
            os.makedirs(TrackorTestCase.GET_FILES_FOLDER)

    def _delete_received_files(self):
        for file_name in os.listdir(TrackorTestCase.GET_FILES_FOLDER):
            try:
                os.remove(f'{TrackorTestCase.GET_FILES_FOLDER}/{file_name}')
                self._module_log.add(LogLevel.DEBUG, f'File [{file_name}] has been deleted')
            except FileNotFoundError:
                pass
            except Exception as exception:
                self._module_log.add(LogLevel.ERROR, f'File [{file_name}] can\'t been deleted. Error: [{exception}]')

    def test_create_trackor(self):
        parent_create_trackor = self._ov_parent_trackor.create_trackor(TrackorTestCase.PARENT_CREATE_TRACKOR_DICT)

        parent_filters_dict = {
            TrackorTestCase.PARENT_TRACKOR_ID_WITH_TRACKOR_TYPE: parent_create_trackor[TrackorTestCase.PARENT_TRACKOR_ID]
        }
        parent_fields_list = [
            TrackorTestCase.PARENT_FIELD_NUMBER,
            TrackorTestCase.PARENT_FIELD_TEXT
        ]
        parent_get_trackor = self._ov_parent_trackor.get_trackor_by_filters_dict(parent_filters_dict,
                                                                                 parent_fields_list)

        self._check_trackor_fields_are_equal(parent_get_trackor[0][TrackorTestCase.PARENT_FIELD_NUMBER],
                                             TrackorTestCase.PARENT_CREATE_TRACKOR_DICT[TrackorTestCase.PARENT_FIELD_NUMBER])
        self._check_trackor_fields_are_equal(parent_get_trackor[0][TrackorTestCase.PARENT_FIELD_TEXT],
                                             TrackorTestCase.PARENT_CREATE_TRACKOR_DICT[TrackorTestCase.PARENT_FIELD_TEXT])

        parents_dict = {
            TrackorTestCase.PARENT_TRACKOR_TYPE: parent_filters_dict
        }
        child_create_trackor = self._ov_child_trackor.create_trackor(TrackorTestCase.CHILD_CREATE_TRACKOR_DICT,
                                                                     parents_dict)

        child_filters_dict = {
            TrackorTestCase.CHILD_TRACKOR_ID_WITH_TRACKOR_TYPE: child_create_trackor[TrackorTestCase.CHILD_TRACKOR_ID]
        }
        child_fields_list = [
            TrackorTestCase.CHILD_FIELD_NUMBER,
            TrackorTestCase.CHILD_FIELD_TEXT
        ]
        child_get_trackor = self._ov_child_trackor.get_trackor_by_filters_dict(child_filters_dict,
                                                                               child_fields_list)

        self._check_trackor_fields_are_equal(child_get_trackor[0][TrackorTestCase.CHILD_FIELD_NUMBER],
                                             TrackorTestCase.CHILD_CREATE_TRACKOR_DICT[TrackorTestCase.CHILD_FIELD_NUMBER])
        self._check_trackor_fields_are_equal(child_get_trackor[0][TrackorTestCase.CHILD_FIELD_TEXT],
                                             TrackorTestCase.CHILD_CREATE_TRACKOR_DICT[TrackorTestCase.CHILD_FIELD_TEXT])

    def test_update_trackor(self):
        parent_trackor_id = self._get_trackor_id(TrackorTestCase.UPDATE_TRACKOR_1_TRACKOR_KEY)
        parent_fields_list = [
            TrackorTestCase.PARENT_FIELD_NUMBER,
            TrackorTestCase.PARENT_FIELD_TEXT,
            TrackorTestCase.PARENT_FIELD_EFILE
        ]
        parent_get_trackor = self._ov_parent_trackor.get_trackor_by_trackor_id(parent_trackor_id,
                                                                               parent_fields_list)

        self._check_trackor_fields_are_equal(parent_get_trackor[TrackorTestCase.PARENT_FIELD_NUMBER],
                                             TrackorTestCase.NUMBER_VALUE_BEFORE_UPDATE_TRACKOR)
        self._check_trackor_fields_are_equal(parent_get_trackor[TrackorTestCase.PARENT_FIELD_TEXT],
                                             TrackorTestCase.TEXT_VALUE_BEFORE_UPDATE_TRACKOR)
        self._check_file_dicts_are_equal(parent_get_trackor[TrackorTestCase.PARENT_FIELD_EFILE],
                                          TrackorTestCase.FILE_DICT_EMPTY)

        expected_efile_field_value = deepcopy(TrackorTestCase.FILE_DICT_EMPTY)
        expected_efile_field_value[TrackorTestCase.FILE_DICT_DATA] = TrackorTestCase.FILE_DATA_123
        expected_efile_field_value[TrackorTestCase.FILE_DICT_FILE_NAME] = TrackorTestCase.UPLOAD_FILE_NAME
        parent_update_fields_dict = {
            TrackorTestCase.PARENT_FIELD_NUMBER: TrackorTestCase.NUMBER_VALUE_AFTER_UPDATE_TRACKOR,
            TrackorTestCase.PARENT_FIELD_TEXT: TrackorTestCase.TEXT_VALUE_AFTER_UPDATE_TRACKOR,
            TrackorTestCase.PARENT_FIELD_EFILE: expected_efile_field_value
        }
        self._ov_parent_trackor.update_trackor(parent_trackor_id,
                                               parent_update_fields_dict)
        
        parent_update_trackor = self._ov_parent_trackor.get_trackor_by_trackor_id(parent_trackor_id,
                                                                                  parent_fields_list)
        self._check_trackor_fields_are_equal(parent_update_trackor[TrackorTestCase.PARENT_FIELD_NUMBER],
                                             parent_update_fields_dict[TrackorTestCase.PARENT_FIELD_NUMBER])
        self._check_trackor_fields_are_equal(parent_update_trackor[TrackorTestCase.PARENT_FIELD_TEXT],
                                             parent_update_fields_dict[TrackorTestCase.PARENT_FIELD_TEXT])
        self._check_file_dicts_are_equal(parent_update_trackor[TrackorTestCase.PARENT_FIELD_EFILE],
                                         parent_update_fields_dict[TrackorTestCase.PARENT_FIELD_EFILE])

    def test_delete_trackor(self):
        parent_trackor_id = self._get_trackor_id(TrackorTestCase.DELETE_TRACKOR_1_TRACKOR_KEY)
        self._ov_parent_trackor.delete_trackor(parent_trackor_id)

        module_error_description = None
        parent_fields_list = [
            TrackorTestCase.PARENT_FIELD_NUMBER,
            TrackorTestCase.PARENT_FIELD_TEXT
        ]
        try:
            self._ov_parent_trackor.get_trackor_by_trackor_id(parent_trackor_id,
                                                              parent_fields_list)
        except ModuleError as module_error:
            module_error_description = module_error.description

        self.assertIsInstance(module_error_description, list)
        self.assertIsInstance(module_error_description[0], list)
        self.assertEqual(module_error_description[0][0], f'404 = \nTrackor with id=[{parent_trackor_id}] not found')

    def _get_trackor_id(self, trackor_key: str) -> int:
        parent_filters_dict = {
            f'{TrackorTestCase.PARENT_TRACKOR_TYPE}.{TrackorTestCase.PARENT_TRACKOR_KEY}': trackor_key
        }
        parent_get_trackor = self._ov_parent_trackor.get_trackor_by_filters_dict(parent_filters_dict)
        return parent_get_trackor[0][TrackorTestCase.PARENT_TRACKOR_ID]

    def _check_trackor_fields_are_equal(self, actual_field_value: str, expected_field_value: str):
        self.assertEqual(actual_field_value, expected_field_value, 'Trackor fields are not equal.')

    def _check_file_dicts_are_equal(self, actual_efile_field_value: Dict[str, Any], expected_efile_field_value: Dict[str, Any]):
        self.assertEqual(actual_efile_field_value, expected_efile_field_value, 'File dicts are not equal')

    def _check_file_names_are_equal(self, actual_file_name: str, expected_file_name: str):
        self.assertEqual(actual_file_name, expected_file_name, 'File names are not equal.')

    def _check_file_test_data_are_equal(self, actual_file_name: str, expected_file_data: int):
        with open(actual_file_name, 'rb') as actual_file:
            actual_file_data = json.loads(actual_file.read().decode('utf-8'))
        
        self.assertEqual(actual_file_data, expected_file_data, 'File data are not equal.')


class ImportTestCase(TestCase):
    #region constants
    IMPORT_RUN_COMMENT = 'Import started by module [{module_name}]. Module Run Process ID: [{module_process_id}]'
    IMPORT_INTERRUPT_COMMENT = '\r\nImport was in [Running: "Import Start" rules] status when interrupted'

    IMPORT_PARENT_TRACKOR_1_TRACKOR_KEY = 'Import-Parent-Trackor-1'
    IMPORT_PARENT_TRACKOR_2_TRACKOR_KEY = 'Import-Parent-Trackor-2'
    IMPORT_CHILD_TRACKOR_1_TRACKOR_KEY = 'Import-Child-Trackor-1'
    IMPORT_CHILD_TRACKOR_2_TRACKOR_KEY = 'Import-Child-Trackor-2'
    IMPORT_PARENT_INTERRUPT_1_TRACKOR_KEY = 'Import-Parent-Interrupt-1'

    IMPORT_PARENT_TRACKOR_1_NUMBER_VALUE = '10'
    IMPORT_PARENT_TRACKOR_2_NUMBER_VALUE = '30'
    IMPORT_PARENT_TRACKOR_1_TEXT_VALUE = 'Import-Parent-Trackor-Text-Value-1'
    IMPORT_PARENT_TRACKOR_2_TEXT_VALUE = 'Import-Parent-Trackor-Text-Value-2'
    IMPORT_CHILD_TRACKOR_1_NUMBER_VALUE = '20'
    IMPORT_CHILD_TRACKOR_2_NUMBER_VALUE = '40'
    IMPORT_CHILD_TRACKOR_1_TEXT_VALUE = 'Import-Child-Trackor-Text-Value-1'
    IMPORT_CHILD_TRACKOR_2_TEXT_VALUE = 'Import-Child-Trackor-Text-Value-2'

    IMPORT_NAME = 'Test Import'
    IMPORT_FILE_NAME_PATH = 'import_files/test_import.csv'
    INTERRUPT_IMPORT_NAME = 'Test Interrupt Import'
    INTERRUPT_IMPORT_FILE_NAME_PATH = 'import_files/test_interrupt_import.csv'
    IMPORT_ACTION_I = 'INSERT'
    IMPORT_ACTION_U = 'UPDATE'
    IMPORT_ACTION_IU = 'INSERT_UPDATE'

    IMPORT_NAME_PARAMETER = 'import_name'
    IMPORT_COMMENTS_PARAMETER = 'comments'
    IMPORT_STATUS_PARAMETER = 'status'

    EXECUTED_WITHOUT_WARNINGS_IMPORT_STATUS = 'EXECUTED_WITHOUT_WARNINGS'
    RUNNING_RULES_IMPORT_STATUS = 'RUNNING_RULES_IMP_START'
    INTERRUPTED_IMPORT_STATUS = 'INTERRUPTED'

    PARENT_TRACKOR_TYPE = 'VHMPYAPI_ParentTrackor'
    PARENT_TRACKOR_KEY = 'TRACKOR_KEY'
    PARENT_FIELD_TEXT = 'PYAPI_PT_TEXT'
    PARENT_FIELD_NUMBER = 'PYAPI_PT_NUMBER'
    PARENT_FILTERS_DICT = {
        f'{PARENT_TRACKOR_TYPE}.{PARENT_TRACKOR_KEY}': 'Import-Parent-Trackor'
    }

    CHILD_TRACKOR_TYPE = 'VHMPYAPI_ChildTrackor'
    CHILD_TRACKOR_KEY = 'TRACKOR_KEY'
    CHILD_FIELD_TEXT = 'PYAPI_CT_TEXT'
    CHILD_FIELD_NUMBER = 'PYAPI_CT_NUMBER'
    CHILD_FILTERS_DICT = {
        f'{CHILD_TRACKOR_TYPE}.{CHILD_TRACKOR_KEY}': 'Import-Child-Trackor'
    }
    #endregion

    @classmethod
    def setUpClass(cls):
        with open('settings.json', 'rb') as settings_file:
            settings_data = json.loads(settings_file.read().decode('utf-8'))

        ov_access_parameters = OVAccessParameters(settings_data['ovUrl'],
                                                  settings_data['ovAccessKey'],
                                                  settings_data['ovSecretKey'])
        cls._ov_import = OVImport(ov_access_parameters)
        cls._ov_parent_trackor = OVTrackor(ov_access_parameters,
                                           ImportTestCase.PARENT_TRACKOR_TYPE)
        cls._ov_child_trackor = OVTrackor(ov_access_parameters,
                                          ImportTestCase.CHILD_TRACKOR_TYPE)

        with open('ihub_parameters.json', 'rb') as ihub_parameters_file:
            module_data = json.loads(ihub_parameters_file.read().decode('utf-8'))

        cls._process_id = module_data['processId']
        cls._module_name = module_data['integrationName']
        cls._module_log = IntegrationLog(
            module_data['processId'], ov_access_parameters.ov_url_without_protocol,
            ov_access_parameters.ov_access_key, ov_access_parameters.ov_secret_key,
            None, True, module_data['logLevel']
        )

        cls._import_run_comment = ImportTestCase.IMPORT_RUN_COMMENT.format(module_name=cls._module_name,
                                                                           module_process_id=cls._process_id)

    def setUp(self):
        self._module_log.add(LogLevel.INFO, f'{datetime.now()} {self._testMethodName} start')

    def tearDown(self):
        self._module_log.add(LogLevel.INFO, f'{datetime.now()} {self._testMethodName} finish')

    def test_run_import(self):
        import_id = self._ov_import.get_import_id(ImportTestCase.IMPORT_NAME)
        ov_import = self._ov_import.run_import(import_id,
                                               ImportTestCase.IMPORT_ACTION_IU,
                                               ImportTestCase.IMPORT_FILE_NAME_PATH,
                                               self._process_id,
                                               self._module_name)

        # We need to wait a second before calling get_import_process_data because
        # we may get the status RUNNING_RULES_IMP_START instead of EXECUTED_WITHOUT_WARNINGS
        sleep(1)
        import_process_data = self._ov_import.get_import_process_data(ov_import,
                                                                      ov_import.processId)
        self._check_import_names_are_equal(import_process_data[ImportTestCase.IMPORT_NAME_PARAMETER],
                                           ImportTestCase.IMPORT_NAME)
        self._check_import_comments_are_equal(import_process_data[ImportTestCase.IMPORT_COMMENTS_PARAMETER],
                                              self._import_run_comment)
        self._check_import_statuses_are_equal(import_process_data[ImportTestCase.IMPORT_STATUS_PARAMETER],
                                              ImportTestCase.EXECUTED_WITHOUT_WARNINGS_IMPORT_STATUS)

        parent_fields_list = [
            ImportTestCase.PARENT_FIELD_NUMBER,
            ImportTestCase.PARENT_FIELD_TEXT
        ]
        parent_get_trackor = self._ov_parent_trackor.get_trackor_by_filters_dict(ImportTestCase.PARENT_FILTERS_DICT,
                                                                                 parent_fields_list)
        self._check_trackor_fields_are_equal(parent_get_trackor[0][ImportTestCase.PARENT_FIELD_NUMBER],
                                             ImportTestCase.IMPORT_PARENT_TRACKOR_1_NUMBER_VALUE)
        self._check_trackor_fields_are_equal(parent_get_trackor[0][ImportTestCase.PARENT_FIELD_TEXT],
                                             ImportTestCase.IMPORT_PARENT_TRACKOR_1_TEXT_VALUE)
        self._check_trackor_fields_are_equal(parent_get_trackor[1][ImportTestCase.PARENT_FIELD_NUMBER],
                                             ImportTestCase.IMPORT_PARENT_TRACKOR_2_NUMBER_VALUE)
        self._check_trackor_fields_are_equal(parent_get_trackor[1][ImportTestCase.PARENT_FIELD_TEXT],
                                             ImportTestCase.IMPORT_PARENT_TRACKOR_2_TEXT_VALUE)

        child_fields_list = [
            ImportTestCase.CHILD_FIELD_NUMBER,
            ImportTestCase.CHILD_FIELD_TEXT
        ]
        child_get_trackor = self._ov_child_trackor.get_trackor_by_filters_dict(ImportTestCase.CHILD_FILTERS_DICT,
                                                                               child_fields_list)
        self._check_trackor_fields_are_equal(child_get_trackor[0][ImportTestCase.CHILD_FIELD_NUMBER],
                                             ImportTestCase.IMPORT_CHILD_TRACKOR_1_NUMBER_VALUE)
        self._check_trackor_fields_are_equal(child_get_trackor[0][ImportTestCase.CHILD_FIELD_TEXT],
                                             ImportTestCase.IMPORT_CHILD_TRACKOR_1_TEXT_VALUE)
        self._check_trackor_fields_are_equal(child_get_trackor[1][ImportTestCase.CHILD_FIELD_NUMBER],
                                             ImportTestCase.IMPORT_CHILD_TRACKOR_2_NUMBER_VALUE)
        self._check_trackor_fields_are_equal(child_get_trackor[1][ImportTestCase.CHILD_FIELD_TEXT],
                                             ImportTestCase.IMPORT_CHILD_TRACKOR_2_TEXT_VALUE)

    def test_interrupt_import(self):
        import_id = self._ov_import.get_import_id(ImportTestCase.INTERRUPT_IMPORT_NAME)
        ov_import = self._ov_import.run_import(import_id,
                                               ImportTestCase.IMPORT_ACTION_IU,
                                               ImportTestCase.INTERRUPT_IMPORT_FILE_NAME_PATH,
                                               self._process_id,
                                               self._module_name)

        import_process_data_before_interrupt = self._ov_import.get_import_process_data(ov_import,
                                                                         ov_import.processId)
        self._check_import_names_are_equal(import_process_data_before_interrupt[ImportTestCase.IMPORT_NAME_PARAMETER],
                                           ImportTestCase.INTERRUPT_IMPORT_NAME)
        self._check_import_comments_are_equal(import_process_data_before_interrupt[ImportTestCase.IMPORT_COMMENTS_PARAMETER],
                                              self._import_run_comment)
        self._check_import_statuses_are_equal(import_process_data_before_interrupt[ImportTestCase.IMPORT_STATUS_PARAMETER],
                                              ImportTestCase.RUNNING_RULES_IMPORT_STATUS)

        self._ov_import.interrupt_import(ov_import, ov_import.processId)
        import_process_data_after_interrupt = self._ov_import.get_import_process_data(ov_import,
                                                                         ov_import.processId)
        self._check_import_names_are_equal(import_process_data_after_interrupt[ImportTestCase.IMPORT_NAME_PARAMETER],
                                           ImportTestCase.INTERRUPT_IMPORT_NAME)
        self._check_import_comments_are_equal(import_process_data_after_interrupt[ImportTestCase.IMPORT_COMMENTS_PARAMETER],
                                              f'{self._import_run_comment}{ImportTestCase.IMPORT_INTERRUPT_COMMENT}')
        self._check_import_statuses_are_equal(import_process_data_after_interrupt[ImportTestCase.IMPORT_STATUS_PARAMETER],
                                              ImportTestCase.INTERRUPTED_IMPORT_STATUS)

    def _check_import_names_are_equal(self, actual_import_name: str, expected_import_name: str):
        self.assertEqual(actual_import_name, expected_import_name, 'Import names are not equal')

    def _check_import_comments_are_equal(self, actual_import_comments: str, expected_import_comments: str):
        self.assertEqual(actual_import_comments, expected_import_comments, 'Import comments are not equal')

    def _check_import_statuses_are_equal(self, actual_import_status: str, expected_import_status: str):
        self.assertEqual(actual_import_status, expected_import_status, 'Import statuses are not equal')

    def _check_trackor_fields_are_equal(self, actual_field_value: str, expected_field_value: str):
        self.assertEqual(actual_field_value, expected_field_value, 'Trackor fields are not equal.')
