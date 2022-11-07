from fields import Field, FieldMetadata
from dataclasses import dataclass

@dataclass
class AK606Config:
    POSITION = FieldMetadata(16, -1000, 1000)
    SPEED = FieldMetadata(12, -45, 45)
    TORQUE = FieldMetadata(12, -18, 18)  # -9, 9?
    KP = FieldMetadata(12, 0, 500)
    KD = FieldMetadata(12, 0, 5)

    position: float
    speed: float    
    kp: float
    kd: float
    torque: float

    @property
    def can_data(self):
        return Field.pack([Field(self.position, self.POSITION),
                           Field(self.speed, self.SPEED),
                           Field(self.kp, self.KP),
                           Field(self.kd, self.KD),
                           Field(self.torque, self.TORQUE)])