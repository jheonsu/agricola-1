class Base:
    """
    Base 클래스: 모든 게임 객체의 부모 클래스
    """

    # 자원 객체를 dict 형태로 변환
    def to_dict(self) -> dict:
        items = self.__dict__.items()
        return {key[1:]: value if not isinstance(value, Base) else value.to_dict() for key, value in items}

    # dict 형태의 자원 정보를 객체를 생성
    @classmethod
    def from_dict(cls, *args, **kwargs):
        return cls(**kwargs)

    # 객체에 존재하는 자원을 가져오는 함수
    def get(self, key: str):
        return self.__getattribute__(f'_{key}')

    # 객체에 존재하는 자원을 설정하는 함수
    def set(self, key: str, value):
        self.__setattr__(f'_{key}', value)

    def plus(self, key: str, value):
        prev_value = self.get(key)
        self.set(key, prev_value + value)

    def minus(self, key: str, value):
        prev_value = self.get(key)
        self.set(key, prev_value - value)
