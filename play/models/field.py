from typing import List

from core.models import Base
from play.enum import FieldType
from play.models.field_resource import FieldResource


# position 의 경우 1 ~ 15 까지의 숫자로 이루어진 좌표의 index 값을 사용한다.
# Position index 값 배치도
# 1 2 3 4 5
# 6 7 8 9 10
# 11 12 13 14 15
class Field(Base):
    _field_type: FieldType
    _position: int
    _is_in: FieldResource

    def __init__(
            self,
            field_type: FieldType,
            position: int,
            is_in: dict | None = None,
    ):
        self._field_type = field_type
        self._position = position
        self._is_in = FieldResource.from_dict(**is_in) or FieldResource()

    @classmethod
    def initialize(cls) -> 'List[Field]':
        room1 = cls(
            field_type=FieldType.ROOM,
            position=6,
            is_in=FieldResource.initialize_player().to_dict()
        )
        room2 = cls(
            field_type=FieldType.ROOM,
            position=11,
            is_in=FieldResource.initialize_player().to_dict()
        )
        # FIXME: 테스트 환경을 위해 임시로 5마리의 양을 배치
        room3 = cls(
            field_type=FieldType.CAGE,
            position=5,
            is_in=FieldResource(sheep=5).to_dict()
        )
        return [room1, room2, room3]

    def move(self, arrival: 'Field', animal: str, count: int) -> None:
        # TODO: 이동이 가능한지에 대한 예외 처리

        # # exception 처리를 위한 transaction 처리 - deepcopy
        # departure = FieldResource(**self._is_in.to_dict())

        # 옮기는 필드에 동물이 없다면 에러를 발생 시킴.
        departure_animal_count: int = self._is_in.get(animal)
        if departure_animal_count == 0:
            raise Exception("옮기고자 하는 동물이 없다.")

        elif departure_animal_count < count:
            raise Exception("옮기고자 하는 동물의 수가 부족하다.")

        # 옮긴 이후 방에 동물을 추가한다.
        arrival_animal_count = arrival.get("is_in").get(animal)
        arrival.get("is_in").set(animal, arrival_animal_count + count)
        self._is_in.set(animal, departure_animal_count - count)

        # # exception 처리를 위한 transaction 처리 - deepcopy 적용
        # self._is_in = FieldResource.from_dict(**departure.to_dict())
        return None

    def to_dict(self) -> dict:
        return {
            "field_type": self._field_type.value,
            "position": self._position,
            "is_in": self._is_in.to_dict(),
        }

    @classmethod
    def from_dict(cls, **kwargs):
        field_type = kwargs.pop("field_type")
        kwargs["field_type"] = FieldType(field_type)
        return super().from_dict(**kwargs)
