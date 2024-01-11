import re
from typing import Any, Dict, List

import requests
from module_error import ModuleError

from onevizion import Import, Task, Trackor, WorkPlan


class OVAccessParameters:
    #region constants
    REGEXP_PROTOCOLS = '^(https|http)://'
    #endregion

    def __init__(self, ov_url: str, ov_access_key: str, ov_secret_key: str) -> None:
        self.ov_url = ov_url
        self.ov_url_without_protocol = re.sub(OVAccessParameters.REGEXP_PROTOCOLS, '', ov_url)
        self.ov_access_key = ov_access_key
        self.ov_secret_key = ov_secret_key


class OVImport:
    #region constants
    RUN_COMMENT = 'Import started by module [{module_name}]. Module Run Process ID: [{module_process_id}]'
    IMPORT_NOT_FOUND_ID = -1
    #endregion

    def __init__(self, ov_access_parameters: OVAccessParameters):
        self._ov_url = ov_access_parameters.ov_url
        self._ov_url_without_protocol = ov_access_parameters.ov_url_without_protocol
        self._ov_access_key = ov_access_parameters.ov_access_key
        self._ov_secret_key = ov_access_parameters.ov_secret_key

    def get_import_id(self, import_name: str) -> int:
        import_id = OVImport.IMPORT_NOT_FOUND_ID
        for imp_data in self._get_imports():
            if imp_data['name'] == import_name:
                import_id = imp_data['id']
                break

        return import_id

    def _get_imports(self) -> List[Dict[str, Any]]:
        url = f'{self._ov_url}/api/v3/imports'
        headers = {'Content-type': 'application/json', 'Content-Encoding': 'utf-8',
                   'Authorization': f'Bearer {self._ov_access_key}:{self._ov_secret_key}'}
        response = requests.get(url=url, headers=headers)

        if not response.ok:
            raise ModuleError('Failed to get imports',  response.text)

        return response.json()

    def run_import(self, import_id: int, import_action: str, file_name: str, module_process_id: str, module_name: str) -> Import:
        comment = OVImport.RUN_COMMENT.format(module_name=module_name,
                                              module_process_id=module_process_id)
        ov_import = Import(self._ov_url_without_protocol,
                           self._ov_access_key,
                           self._ov_secret_key,
                           import_id,
                           file_name,
                           import_action,
                           comment,
                           isTokenAuth=True)
        if len(ov_import.errors) != 0:
            raise ModuleError('Failed to run import', ov_import.request.text)

        return ov_import

    def interrupt_import(self, ov_import: Import, import_process_id: int) -> str:
        ov_import.interrupt(
            ProcessID=import_process_id
        )
        return ov_import.processId

    def get_import_process_data(self, ov_import: Import, import_process_id: int) -> Dict[str, Any]:
        return ov_import.getProcessData(
            processId=import_process_id
        )


class OVTrackor:

    def __init__(self, ov_access_parameters: OVAccessParameters, trackor_type_name: str):
        self._ov_url_without_protocol = ov_access_parameters.ov_url_without_protocol
        self._ov_access_key = ov_access_parameters.ov_access_key
        self._ov_secret_key = ov_access_parameters.ov_secret_key
        self._trackor_type_wrapper = Trackor(
            trackorType=trackor_type_name,
            URL=self._ov_url_without_protocol,
            userName=self._ov_access_key,
            password=self._ov_secret_key,
            isTokenAuth=True
        )

    def delete_trackor(self, trackor_id: int) -> Dict[str, Any]:
        self._trackor_type_wrapper.delete(
            trackorId=trackor_id
        )

        if len(self._trackor_type_wrapper.errors) > 0:
            raise ModuleError('Failed to delete_trackor', self._trackor_type_wrapper.errors)

        return self._trackor_type_wrapper.jsonData

    def get_trackor_by_filters_dict(self, filters_dict: Dict[str, Any], fields_list: List[str] = []) -> List[Dict[str, Any]]:
        self._trackor_type_wrapper.read(
            filters=filters_dict,
            fields=fields_list
        )

        if len(self._trackor_type_wrapper.errors) > 0:
            raise ModuleError('Failed to get_trackor_by_filters_dict', self._trackor_type_wrapper.errors)

        return list(self._trackor_type_wrapper.jsonData)
    
    def get_trackor_by_trackor_id(self, trackor_id: int, fields_list: List[str]) -> Dict[str, Any]:
        self._trackor_type_wrapper.read(
            trackorId=trackor_id,
            fields=fields_list
        )

        if len(self._trackor_type_wrapper.errors) > 0:
            raise ModuleError('Failed to get_trackor_by_trackor_id', self._trackor_type_wrapper.errors)

        return self._trackor_type_wrapper.jsonData

    def create_trackor(self, fields_dict: Dict[str, Any], parents_dict: Dict[str, Any] = {}) -> Dict[str, Any]:
        self._trackor_type_wrapper.create(
            fields=fields_dict,
            parents=parents_dict
        )

        if len(self._trackor_type_wrapper.errors) > 0:
            raise ModuleError('Failed to create_trackor', self._trackor_type_wrapper.errors)

        return self._trackor_type_wrapper.jsonData

    def update_trackor(self, trackor_id: int, fields_dict: Dict[str, Any]) -> Dict[str, Any]:
        self._trackor_type_wrapper.update(
            trackorId=trackor_id,
            fields=fields_dict
        )

        if len(self._trackor_type_wrapper.errors) > 0:
            raise ModuleError('Failed to update_trackor', self._trackor_type_wrapper.errors)

        return self._trackor_type_wrapper.jsonData

    def assign_workplan(self, trackor_id: int, workplan_template_name: str, workplan_name: str,
                        workplan_is_active: bool = False, current_date: str = None, next_date: str = None) -> Dict[str, Any]:
        self._trackor_type_wrapper.assignWorkplan(
            trackorId=trackor_id,
            workplanTemplate=workplan_template_name,
            name=workplan_name,
            isActive=workplan_is_active,
            startDate=current_date,
            finishDate=next_date
        )

        if len(self._trackor_type_wrapper.errors) > 0:
            raise ModuleError('Failed to assign_workplan', self._trackor_type_wrapper.errors)

        return self._trackor_type_wrapper.jsonData

    def get_file_by_fieldname(self, trackor_id: int, field_name: str) -> str:
        return self._trackor_type_wrapper.GetFile(
            trackorId=trackor_id,
            fieldName=field_name
        )

    def get_file_by_blob(self, blob_data_id: int) -> str:
        return self._trackor_type_wrapper.GetFile(
            blobDataId=blob_data_id
        )

    def upload_file(self, trackor_id: int, field_name: str, file_name: str, new_file_name: str) -> None:
        self._trackor_type_wrapper.UploadFile(
            trackorId=trackor_id,
            fieldName=field_name,
            fileName=file_name,
            newFileName=new_file_name
        )

        if len(self._trackor_type_wrapper.errors) > 0:
            raise ModuleError('Failed to upload_file', self._trackor_type_wrapper.errors)

    def upload_file_by_file_contents(self, trackor_id: int, field_name: str, file_name: str, file_path: str) -> None:
        self._trackor_type_wrapper.UploadFileByFileContents(
            trackorId=trackor_id,
            fieldName=field_name,
            fileName=file_name,
            fileContents=file_path
        )

        if len(self._trackor_type_wrapper.errors) > 0:
            raise ModuleError('Failed to upload_file_by_file_contents', self._trackor_type_wrapper.errors)


class OVWorkplan:
    #region constants
    WP_ID_LIST_ITEM = 'id'
    WP_ACTIVE_STATUS_LIST_ITEM = 'active'
    WP_NOT_FOUND_ID = -1
    #endregion

    def __init__(self, ov_access_parameters: OVAccessParameters):
        self._ov_workplan_wrapper = WorkPlan(
            URL=ov_access_parameters.ov_url_without_protocol,
            userName=ov_access_parameters.ov_access_key,
            password=ov_access_parameters.ov_secret_key, isTokenAuth=True
        )
        self._ov_task_wrapper = Task(
            URL=ov_access_parameters.ov_url_without_protocol,
            userName=ov_access_parameters.ov_access_key,
            password=ov_access_parameters.ov_secret_key, isTokenAuth=True
        )

    def get_workplan_id(self, trackor_id: int, workplan_template_name: str) -> int:
        workplan_id = OVWorkplan.WP_NOT_FOUND_ID
        for workplan in self._get_workplans(trackor_id, workplan_template_name):
            if workplan[OVWorkplan.WP_ACTIVE_STATUS_LIST_ITEM]:
                workplan_id = workplan[OVWorkplan.WP_ID_LIST_ITEM]

        return workplan_id

    def get_workplan_by_workplan_id(self, workplan_id: str):
        self._ov_workplan_wrapper.read(
            workplanId=workplan_id
        )

        if len(self._ov_workplan_wrapper.errors) > 0:
            raise ModuleError('Failed to get get_workplan_id', self._ov_workplan_wrapper.errors)

        return self._ov_workplan_wrapper.jsonData

    def _get_workplans(self, trackor_id: int, workplan_template_name: str) -> List[Dict[str, Any]]:
        self._ov_workplan_wrapper.read(
            trackorId=trackor_id,
            workplanTemplate=workplan_template_name
        )

        if len(self._ov_workplan_wrapper.errors) > 0:
            raise ModuleError('Failed to get_workplans', self._ov_workplan_wrapper.errors)

        return list(self._ov_workplan_wrapper.jsonData)

    def get_task_by_order_number(self, workplan_id: int, order_number: str) -> Dict[str, Any]:
        self._ov_task_wrapper.read(
            workplanId=workplan_id,
            orderNumber=order_number
        )

        if len(self._ov_task_wrapper.errors) > 0:
            raise ModuleError('Failed to get_task_by_order_number', self._ov_task_wrapper.errors)

        return self._ov_task_wrapper.jsonData

    def get_task_by_task_id(self, task_id: int) -> Dict[str, Any]:
        self._ov_task_wrapper.read(
            taskId=task_id
        )

        if len(self._ov_task_wrapper.errors) > 0:
            raise ModuleError('Failed to get_task_by_task_id', self._ov_task_wrapper.errors)

        return self._ov_task_wrapper.jsonData

    def update_task(self, task_id: int, fields: Dict[str, Any],
                    dynamic_dates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self._ov_task_wrapper.update(
            taskId=task_id,
            fields=fields,
            dynamicDates=dynamic_dates
        )

        if len(self._ov_task_wrapper.errors) > 0:
            raise ModuleError('Failed to update_task', self._ov_task_wrapper.errors)

        return list(self._ov_task_wrapper.jsonData)

    def update_task_partial(self, task_id: int, fields: Dict[str, Any],
                    dynamic_dates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self._ov_task_wrapper.updatePartial(
            taskId=task_id,
            fields=fields,
            dynamicDates=dynamic_dates
        )

        if len(self._ov_task_wrapper.errors) > 0:
            raise ModuleError('Failed to update_task_partial', self._ov_task_wrapper.errors)

        return list(self._ov_task_wrapper.jsonData)
