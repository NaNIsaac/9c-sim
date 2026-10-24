import numpy as np

from motor import BeamlineState


class Sample:
    def __init__(self):

        self.origin = np.array([0, 0, 0, 1])

    def get_global_pos(self, motors: BeamlineState):
        """
        9C BeamLine Kinematic Chain:
        Lab <- th <- chi <- phi <- translation(sx, sy, shold) <- Sample
        """

        m_th = self._matrix_rotate_y(motors.th.current_pos)
        m_chi = self._matrix_rotate_z(motors.chi.current_pos - 90)
        m_phi = self._matrix_rotate_y(motors.phi.current_pos)

        m_trans = self._matrix_translate(
            x=0, y=motors.sy.current_pos + motors.shold.current_pos, z=motors.sx.current_pos
        )

        full_transform = m_th @ m_chi @ m_phi @ m_trans

        return full_transform @ self.origin

    def _matrix_rotate_x(self, angle: float):
        ang_rad = np.radians(angle)
        c, s = np.cos(ang_rad), np.sin(ang_rad)
        return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]])

    def _matrix_rotate_y(self, angle: float):
        ang_rad = np.radians(angle)
        c, s = np.cos(ang_rad), np.sin(ang_rad)
        return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])

    def _matrix_rotate_z(self, angle: float):
        ang_rad = np.radians(angle)
        c, s = np.cos(ang_rad), np.sin(ang_rad)
        return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    def _matrix_translate(self, x, y, z):
        return np.array([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])


if __name__ == "__main__":
    from motor import MotorManager

    state = BeamlineState()
    manager = MotorManager(state)
    sample = Sample()
    manager.move("shold", 0.05)
    manager.move("phi", 180)
    print(sample.get_global_pos(state))
