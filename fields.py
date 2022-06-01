from dataclasses import dataclass
from bitstring import Bits

@dataclass
class FieldMetadata:
    length: int
    minimum: float
    maximum: float
    name: str = 'UNNAMED'

    def to_int(self, value: float):
        clamped = min(self.maximum, max(value, self.minimum))
        span = self.maximum - self.minimum
        magnitude = clamped - self.minimum
        ratio = ((1 << self.length) - 1) / span
        return int(magnitude * ratio)

    def to_float(self, value: int):
        span = self.maximum - self.minimum
        ratio = ((1 << self.length) - 1) / span
        return value / ratio + self.minimum

    def __set_name__(self, owner, name):
        self.name = name


@dataclass
class Field:
    value: float
    metadata: FieldMetadata

    def __repr__(self):
        return f'{self.metadata.name}: {self.value}'

    def to_int(self):
        return self.metadata.to_int(self.value)

    @classmethod
    def pack(cls, fields):
        bits = Bits()
        for field in fields:
            bits += Bits(length=field.metadata.length, uint=field.to_int())
        assert len(bits) % 8 == 0
        return bits.bytes

    @classmethod
    def unpack(cls, data, metadatas):
        bits = Bits(data)
        fields = []
        offset = 0
        for meta in metadatas:
            field_data = bits[offset:meta.length + offset]
            offset += meta.length
            value = meta.to_float(field_data.uint)
            fields.append(cls(value, meta))
        return fields
