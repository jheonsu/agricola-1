from play.models.base import Base
from play.models.resource import Resource


class Player(Base):
    _name: str
    _resource: Resource

    def __init__(
            self,
            name: str = "",
            resource: dict = None,
    ):
        self._name = name
        self._resource = Resource.from_dict(**resource) if resource else Resource()

    # 플레이어 행동 처리 (카드 드로우, 카드 사용, 자원 사용 등)
    # 만약 행동이 종료될 경우 True, 종료되지 않을 경우 False를 반환한다. (카드의 속성에 따라 다르게 처리)
    def action(self, card_number: str) -> bool:
        done = True
        not_done = False
        if card_number == "EARN_001":
            self._resource.set("food", self._resource.get("food") + 1)
            return done
        return not_done

    def to_dict(self):
        return {
            'name': self._name,
            'resource': self._resource.to_dict()
        }
