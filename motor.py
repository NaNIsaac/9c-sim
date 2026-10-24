from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Motor(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    name: str
    current_pos: float = 0.0
    min_limit: float = Field(default=-float("inf"), description="Soft limit min")
    max_limit: float = Field(default=float("inf"), description="Soft limit max")

    @model_validator(mode="after")
    def check_range(self) -> Self:
        if not (self.min_limit <= self.current_pos <= self.max_limit):
            raise ValueError(
                f"motor [{self.name}] out of range!\nTarget:{self.current_pos}, Range: [{self.min_limit}, {self.max_limit}]"
            )
        return self


class BeamlineState(BaseModel):
    th: Motor = Field(default_factory=lambda: Motor(name="th"))
    phi: Motor = Field(default_factory=lambda: Motor(name="phi"))
    chi: Motor = Field(default_factory=lambda: Motor(name="chi"))
    shold: Motor = Field(default_factory=lambda: Motor(name="shold"))
    sx: Motor = Field(default_factory=lambda: Motor(name="sx"))
    sy: Motor = Field(default_factory=lambda: Motor(name="sy"))


class MotorManager:
    def __init__(self, state: BeamlineState):
        self._state = state

    def _get_motor_instance(self, name: str) -> Motor:
        try:
            return getattr(self._state, name)
        except AttributeError:
            raise ValueError(f"❌ '{name}' is not defined in 9C Beamline") from None

    def move(self, name: str, pos: float) -> None:
        motor = self._get_motor_instance(name)
        # The assignment runs the Pydantic @model_validator, which checks the limits.
        motor.current_pos = pos
        print(f"Motor {name} moved to {pos}")

    def get_pos(self, name: str) -> float:
        return self._get_motor_instance(name).current_pos

    def get_motor(self, name: str) -> Motor:
        return self._get_motor_instance(name)

    def get_all_motors(self) -> dict[str, Motor]:
        return {field: getattr(self._state, field) for field in self._state.model_fields}

    def wh(self):
        print(f"{'Motor':<10} {'Position':<10}")
        print("-" * 20)
        for name, motor in self.get_all_motors().items():
            print(f"{name:<10} {motor.current_pos:<10.4f}")
