# 9c-sim

A small model of the sample stage of the 9C beamline diffractometer, as it stands now (2026-10-23):

- `motor.py`: `Motor` (pydantic) with a position and soft limits that are checked on every assignment; `BeamlineState` with the six motors `th`, `phi`, `chi`, `shold`, `sx`, `sy`; `MotorManager` with `move`, `get_pos` and a `wh` printout.
- `sample.py`: `Sample.get_global_pos`, the 4x4 homogeneous kinematic chain Lab <- th <- chi <- phi <- translation (sx, sy + shold) applied to the sample origin.

No 9C limit values are set: every motor defaults to minus to plus infinity, so the limit check only fires for limits you pass yourself. There is no diffraction calculation here; the rocking-scan simulator is a separate repository (rocking_xrd_sim).

## Run

```bash
uv sync
uv run sample.py
```

This moves `shold` to 0.05 and `phi` to 180 and prints the sample origin in the lab frame, `[0.05, ~0, 0, 1]`.
