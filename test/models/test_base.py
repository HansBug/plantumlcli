import os
from typing import Optional
from unittest.mock import Mock

import pytest
import where
from urlobject import URLObject

from plantumlcli import LocalPlantuml, RemotePlantuml
from plantumlcli.models.base import PlantumlType, PlantumlResourceType, try_plantuml
from plantumlcli.models.remote import OFFICIAL_PLANTUML_HOST
from plantumlcli.utils import all_func
from ..test import unittest, PRIMARY_JAR_PATH, mark_select, is_file_func


@unittest
class TestModelsBaseEnums:
    def test_plantuml_type(self):
        assert PlantumlType.LOCAL == 1
        assert PlantumlType.REMOTE == 2
        assert PlantumlType.REMOTE != PlantumlType.LOCAL

    def test_plantuml_resource_type(self):
        assert PlantumlResourceType.TXT
        assert PlantumlResourceType.PNG
        assert PlantumlResourceType.EPS
        assert PlantumlResourceType.SVG
        assert len({
            PlantumlResourceType.TXT,
            PlantumlResourceType.PNG,
            PlantumlResourceType.EPS,
            PlantumlResourceType.SVG,
        }) == 4

    def test_plantuml_resource_type_load(self):
        assert PlantumlResourceType.load('txt') == PlantumlResourceType.TXT
        assert PlantumlResourceType.load('pNG') == PlantumlResourceType.PNG
        assert PlantumlResourceType.load('Svg') == PlantumlResourceType.SVG
        assert PlantumlResourceType.load('EPS') == PlantumlResourceType.EPS
        with pytest.raises(KeyError):
            PlantumlResourceType.load('invalid_type')

        assert PlantumlResourceType.load(1) == PlantumlResourceType.TXT
        assert PlantumlResourceType.load(2) == PlantumlResourceType.PNG
        assert PlantumlResourceType.load(3) == PlantumlResourceType.SVG
        assert PlantumlResourceType.load(4) == PlantumlResourceType.EPS
        with pytest.raises(ValueError):
            PlantumlResourceType.load(-1)

        assert PlantumlResourceType.load(PlantumlResourceType.TXT) == PlantumlResourceType.TXT
        assert PlantumlResourceType.load(PlantumlResourceType.PNG) == PlantumlResourceType.PNG
        assert PlantumlResourceType.load(PlantumlResourceType.SVG) == PlantumlResourceType.SVG
        assert PlantumlResourceType.load(PlantumlResourceType.EPS) == PlantumlResourceType.EPS

        with pytest.raises(TypeError):
            # noinspection PyTypeChecker
            PlantumlResourceType.load(None)


_primary_jar_condition = all_func(is_file_func(PRIMARY_JAR_PATH))


class TestModelsBaseTryPlantuml:
    @classmethod
    def _get_local_plantuml_by_try_plantuml(cls, plantuml: str, java: Optional[str] = None) -> LocalPlantuml:
        _success, _data = try_plantuml(LocalPlantuml, plantuml=plantuml, java=java)
        if _success:
            return _data
        else:
            raise _data

    @mark_select(_primary_jar_condition)
    def test_local_plantuml(self):
        plantuml = self._get_local_plantuml_by_try_plantuml(plantuml=PRIMARY_JAR_PATH)
        assert isinstance(plantuml, LocalPlantuml)
        assert plantuml.java == where.first('java')
        assert plantuml.plantuml == PRIMARY_JAR_PATH

    @mark_select(_primary_jar_condition)
    def test_local_plantuml_error(self):
        with pytest.raises(FileNotFoundError):
            _ = self._get_local_plantuml_by_try_plantuml(java='path_not_exist', plantuml=PRIMARY_JAR_PATH)
        with pytest.raises(IsADirectoryError):
            _ = self._get_local_plantuml_by_try_plantuml(java=os.path.dirname(PRIMARY_JAR_PATH),
                                                         plantuml=PRIMARY_JAR_PATH)

        with pytest.raises(FileNotFoundError):
            _ = self._get_local_plantuml_by_try_plantuml(plantuml='path_not_exist')
        with pytest.raises(IsADirectoryError):
            _ = self._get_local_plantuml_by_try_plantuml(plantuml=os.path.dirname(PRIMARY_JAR_PATH))

    @classmethod
    def _get_remote_plantuml_by_try_plantuml(cls, host: Optional[str] = None) -> RemotePlantuml:
        _success, _data = try_plantuml(RemotePlantuml, host=host)
        if _success:
            return _data
        else:
            raise _data

    @unittest
    def test_remote_plantuml(self):
        plantuml = self._get_remote_plantuml_by_try_plantuml(OFFICIAL_PLANTUML_HOST)
        assert plantuml.host == OFFICIAL_PLANTUML_HOST

        _get_func, os.environ.get = os.environ.get, Mock(return_value='https://plantuml-host')
        plantuml = self._get_remote_plantuml_by_try_plantuml()
        assert plantuml.host == 'https://plantuml-host'
        os.environ.get = _get_func

        plantuml = self._get_remote_plantuml_by_try_plantuml()
        assert plantuml.host == OFFICIAL_PLANTUML_HOST

    @unittest
    def test_remote_plantuml_error(self):
        with pytest.raises(ValueError):
            self._get_remote_plantuml_by_try_plantuml(str(URLObject(OFFICIAL_PLANTUML_HOST).with_scheme('socks5')))


# TODO: Add test for try_plantuml and Plantuml (abstract class)

if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
