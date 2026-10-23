"""The kinematic chain in `sample.py` against an independent construction.

These checks say that the code does what its docstring says (Lab <- th <- chi <- phi <- translation).
They do not say that the chain is the real 9C stage: axis directions, motor signs and the 90 degree
chi offset are not checked here (DECISIONS #2, see README).
"""

import numpy as np
import pytest

from motor import BeamlineState, Motor
from sample import Sample

TOL = 1e-12


def rotation(axis: str, degrees: float) -> np.ndarray:
    """Rodrigues' formula, written separately from the matrices in sample.py."""
    unit = {"x": (1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0), "z": (0.0, 0.0, 1.0)}[axis]
    kx, ky, kz = unit
    k = np.array([[0.0, -kz, ky], [kz, 0.0, -kx], [-ky, kx, 0.0]])
    a = np.radians(degrees)
    return np.eye(3) + np.sin(a) * k + (1.0 - np.cos(a)) * (k @ k)


def state(**positions: float) -> BeamlineState:
    return BeamlineState(**{name: Motor(name=name, current_pos=pos) for name, pos in positions.items()})


@pytest.mark.parametrize("axis", ["x", "y", "z"])
def test_rotation_matrices_are_proper_rotations(axis):
    sample = Sample()
    build = getattr(sample, f"_matrix_rotate_{axis}")
    for angle in np.arange(-360.0, 360.0 + 1e-9, 7.5):
        m = build(angle)[:3, :3]
        assert np.abs(m.T @ m - np.eye(3)).max() <= TOL
        assert abs(np.linalg.det(m) - 1.0) <= TOL
        assert np.abs(m - rotation(axis, angle)).max() <= TOL


def test_chain_order_matches_the_docstring():
    rng = np.random.default_rng(0)
    sample = Sample()
    for _ in range(200):
        th, phi, chi = rng.uniform(-180.0, 180.0, 3)
        sx, sy, shold = rng.uniform(-5.0, 5.0, 3)
        got = sample.get_global_pos(state(th=th, phi=phi, chi=chi, sx=sx, sy=sy, shold=shold))
        translation = np.array([0.0, sy + shold, sx])
        expected = rotation("y", th) @ rotation("z", chi - 90.0) @ rotation("y", phi) @ translation
        assert np.abs(got[:3] - expected).max() <= TOL
        assert got[3] == 1.0


def test_a_point_on_the_th_axis_does_not_move_with_th():
    sample = Sample()
    # chi = 90 cancels the offset, phi = 0: the translated origin stays on the y axis through R_chi, R_phi.
    base = {"chi": 90.0, "phi": 0.0, "sy": 1.5, "shold": 0.25}
    reference = sample.get_global_pos(state(th=0.0, **base))
    for th in (-170.0, -33.0, 12.0, 90.0, 251.0):
        assert np.abs(sample.get_global_pos(state(th=th, **base)) - reference).max() <= TOL


def test_a_point_on_the_phi_axis_does_not_move_with_phi():
    sample = Sample()
    base = {"th": 23.0, "chi": 41.0, "sy": 1.5, "shold": 0.25}
    reference = sample.get_global_pos(state(phi=0.0, **base))
    for phi in (-170.0, -33.0, 12.0, 90.0, 251.0):
        assert np.abs(sample.get_global_pos(state(phi=phi, **base)) - reference).max() <= TOL


def test_readme_example():
    got = Sample().get_global_pos(state(shold=0.05, phi=180.0))
    assert np.allclose(got, [0.05, 0.0, 0.0, 1.0], atol=1e-12)


def test_motor_limits_are_checked_on_assignment():
    motor = Motor(name="th", min_limit=-10.0, max_limit=10.0)
    motor.current_pos = 10.0
    with pytest.raises(ValueError, match="out of range"):
        motor.current_pos = 10.5
