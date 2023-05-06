import os
import shutil
from unittest.mock import patch

import pytest
from urlobject import URLObject

from plantumlcli import LocalPlantuml, RemotePlantuml
from plantumlcli.models.base import PlantumlType, PlantumlResourceType, try_plantuml
from plantumlcli.models.remote import OFFICIAL_PLANTUML_HOST


@pytest.mark.unittest
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


@pytest.fixture()
def plantuml_local(plantuml_jar_file):
    ok, data = try_plantuml(LocalPlantuml, plantuml=plantuml_jar_file, java=shutil.which('java'))
    if ok:
        return data
    else:
        raise data


@pytest.mark.unittest
class TestModelsBaseTryPlantuml:
    def test_local_plantuml(self, plantuml_local, plantuml_jar_file):
        assert isinstance(plantuml_local, LocalPlantuml)
        assert plantuml_local.java == shutil.which('java')
        assert plantuml_local.plantuml == plantuml_jar_file

    def test_local_plantuml_error(self, plantuml_jar_file):
        with pytest.raises(FileNotFoundError):
            _ = LocalPlantuml.autoload(java='path_not_exist', plantuml=plantuml_jar_file)
        with pytest.raises(IsADirectoryError):
            _ = LocalPlantuml.autoload(java=os.path.dirname(plantuml_jar_file), plantuml=plantuml_jar_file)
        with pytest.raises(FileNotFoundError):
            _ = LocalPlantuml.autoload(java=None, plantuml='path_not_exist')
        with pytest.raises(IsADirectoryError):
            _ = LocalPlantuml.autoload(java=None, plantuml=os.path.dirname(plantuml_jar_file))

    def test_remote_plantuml(self):
        plantuml = RemotePlantuml.autoload(OFFICIAL_PLANTUML_HOST)
        assert plantuml.host == OFFICIAL_PLANTUML_HOST

        with patch.dict('os.environ', values={'PLANTUML_HOST': 'https://plantuml-host'}):
            plantuml = RemotePlantuml.autoload()
            assert plantuml.host == 'https://plantuml-host'

        with patch.dict('os.environ', values={'PLANTUML_HOST': OFFICIAL_PLANTUML_HOST}):
            plantuml = RemotePlantuml.autoload()
            assert plantuml.host == OFFICIAL_PLANTUML_HOST

    def test_remote_plantuml_error(self):
        with pytest.raises(ValueError):
            RemotePlantuml.autoload(str(URLObject(OFFICIAL_PLANTUML_HOST).with_scheme('socks5')))
