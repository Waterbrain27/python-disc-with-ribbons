import pytest
from core.drawable.ribbon import Ribbon
from core.math_machinery.topology import Topology


@pytest.fixture
def clean_topology():
    """Возвращает пустой экземпляр Topology."""
    return Topology([])


def test_one_ordinary_ribbon():
    """Одна обычная (неперекрученная) ленточка → сфера с двумя дырками (g=0, h=2, orientable)."""
    ribbon = Ribbon(0, 180, width=10, twist=0)  # обычная
    topo = Topology([ribbon])
    topo.compute()

    assert topo.k == 1
    assert topo.l == 1
    assert topo._twisted_count == 0
    assert topo.is_orientable is True
    assert topo.h == 2
    assert topo.g == 0
    assert topo.m == 0
    assert topo.chi == 0
    assert topo.surface_type() == "Annulus (cylinder)"


def test_one_twisted_ribbon():
    """Одна перекрученная ленточка → лист Мёбиуса (m=1, h=1, non-orientable)."""
    ribbon = Ribbon(0, 180, width=10, twist=1)
    topo = Topology([ribbon])
    topo.compute()

    assert topo.k == 1
    assert topo.l == 0
    assert topo._twisted_count == 1
    assert topo.is_orientable is False
    assert topo.h == 1
    assert topo.g == 0
    assert topo.m == 1
    assert topo.chi == 0
    assert topo.surface_type() == "Möbius strip"


def test_two_ordinary_ribbons():
    """Две обычные непересекающиеся ленточки → сфера с тремя дырками (g=0, h=3)."""
    r1 = Ribbon(0, 90, width=10, twist=0)
    r2 = Ribbon(180, 270, width=10, twist=0)
    topo = Topology([r1, r2])
    topo.compute()

    assert topo.k == 2
    assert topo.l == 2
    assert topo.is_orientable is True
    assert topo.h == 3
    assert topo.g == 0
    assert topo.m == 0
    assert topo.chi == -1
    assert topo.surface_type() == "Sphere with 0 handles and 3 holes"


def test_mixed_ribbons():
    """Одна обычная + одна перекрученная (не пересекаются) → неориентируемая поверхность с m=1, g=0, h=2."""
    r1 = Ribbon(0, 90, width=10, twist=0)
    r2 = Ribbon(180, 270, width=10, twist=1)
    topo = Topology([r1, r2])
    topo.compute()

    assert topo.k == 2
    assert topo.l == 1
    assert topo._twisted_count == 1
    assert topo.is_orientable is False
    assert topo.h == 2
    assert topo.g == 0
    assert topo.m == 1
    assert topo.chi == -1
    assert topo.surface_type() == "Non-orientable surface with 2 boundaries and 1 crosscaps"


def test_two_intersecting_ordinary_ribbons():
    """Две обычные пересекающиеся ленточки → сфера с одной ручкой и одной дыркой (g=1, h=1)."""
    r1 = Ribbon(0, 180, width=10, twist=0)
    r2 = Ribbon(90, 270, width=10, twist=0)
    topo = Topology([r1, r2])
    topo.compute()

    assert topo.k == 2
    assert topo.l == 2
    assert topo.is_orientable is True
    assert topo.h == 1
    assert topo.g == 1
    assert topo.m == 0
    assert topo.chi == -1
    assert topo.surface_type() == "Torus with a hole (sphere with one handle and two hole)"