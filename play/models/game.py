from typing import List

from core.const import FIRST_CHANGE_CARD_NUMBER, LAST_TURN
from play.models.action import Action
from play.models.base import Base
from play.models.player import Player
from play.models.resource import Resource

"""
게임 정보를 담는 클래스
first: 게임의 선 플레이어
turn: 게임의 턴
"""


class Game(Base):
    _first: int
    _turn: int
    _round: int
    _phase: int
    _players: List[Player]
    _action_on_round: List[Action]
    _common_resources: Resource

    def __init__(
            self,
            first: int = 0,
            turn: int = 0,
            round: int = 0,
            phase: int = 0,
            players: List[Player] = None,
            action_on_round: List[Action] = None,
            common_resources: Resource = Resource()
    ):
        if players is None:
            players = []
        if action_on_round is None:
            action_on_round = []
        self._first = first
        self._turn = turn
        self._round = round
        self._phase = phase
        self._players = players
        self._action_on_round = action_on_round
        self._common_resources = common_resources

    def play(self, card_number: str) -> dict:
        # 플레이어의 종료 여부 확인
        is_done = self.player_action(card_number=card_number)

        # 게임의 정보를 바탕으로 게임의 턴을 변경
        self.change_turn_and_round_and_phase(is_done=is_done)

        # 만약 선을 번경하는 카드를 낸 경우 게임의 선을 변경
        if card_number == FIRST_CHANGE_CARD_NUMBER:
            self._first = self._turn
        return self.to_dict()

    def player_action(self, card_number: str) -> bool:
        is_done = self._players[self._turn].action(card_number=card_number)

        # TODO: is_kid 처리 -> Player 정보 중 자식이 있으며, 자식이 움직이는 턴인지 확인
        self._action_on_round.append(
            Action(
                card_number=card_number,
                player=self._players[self._turn].get('name'),
                is_kid=False
            )
        )

        return is_done

    def change_turn_and_round_and_phase(self, is_done: bool) -> None:
        if not is_done:
            return

        if self._turn == LAST_TURN:
            self._turn = 0
            self._round += 1
            return
