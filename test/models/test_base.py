import os

import pytest

from plantumlcli.models.base import PlantumlType, PlantumlResourceType
from ..test import unittest


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


# TODO: Add test for try_plantuml and Plantuml (abstract class)

if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
