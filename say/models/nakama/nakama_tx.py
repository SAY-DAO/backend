import re
from datetime import datetime

from eth_utils import address
from eth_utils import is_same_address
from eth_utils import remove_0x_prefix
from flask.globals import session
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import Timestamp

from say.config import configs
from say.constants import NAKAMA_ROLE
from say.orm import base
from say.web3 import w3

from .nakama import NakamaOwner
from .participation import NakamaParticipation


class NakamaTx(base, Timestamp):
    __tablename__ = 'nakama_txs'

    id = Column(Unicode(120), nullable=False, primary_key=True)

    sender_address = Column(Unicode(64), ForeignKey('nakama_owners.address'), nullable=True)
    need_id = Column(Integer, ForeignKey('need.id'), nullable=True)

    value = Column(BigInteger, nullable=True)
    is_confirmed = Column(Boolean, default=False)

    need = relationship('Need', foreign_keys=need_id)
    nakama_owner = relationship(
        'NakamaOwner',
        foreign_keys=sender_address,
        back_populates='nakama_txs',
        uselist=False,
    )

    def update(self):
        data = w3.eth.getTransaction(self.id)
        assert is_same_address(data.to, configs.NAKAMA_ADDRESS)

        self.sender_address = data['from'].lower()
        self.value = data.value
        self.need_id = self._parse_need(data.input)
        self.confirm()

    def confirm(self):
        from ..payment_model import Payment
        from ..user_model import User

        session = object_session(self)

        nakama_owner = session.query(NakamaOwner).get(self.sender_address)
        if not nakama_owner:
            self.nakama_owner = NakamaOwner(address=self.sender_address)

        session.flush()
        if self.need.isDone:
            raise ValueError('Need Already Done')

        self.need.done()

        nakama_user = session.query(User).filter(User.is_nakama == True).one()
        now = datetime.utcnow()

        payment = Payment(
            user=nakama_user,
            need=self.need,
            need_amount=self.need.cost - self.need.paid,
            donation_amount=0,
            credit_amount=self.need.cost,
            desc=f'Paid by {self.sender_address} from dapp',
            order_id=self.id,
            gateway_track_id=self.id,
            card_no=self.sender_address,
            is_nakama=True,
            transaction_date=now,
            verified=now,
            hashed_card_no=self.sender_address,
        )
        session.add(payment)

        new_participant = NakamaParticipation(
            family=self.need.child.family,
            user=nakama_user,
            need=self.need,
            user_role=NAKAMA_ROLE,
            address=self.sender_address,
        )
        session.add(new_participant)

        self.is_confirmed = True

    def _decode_input(self, input):
        return bytes.fromhex(remove_0x_prefix(input)).decode(errors='ignore')

    def _parse_need(self, input):
        input = self._decode_input(input)
        parsed_data = re.findall(r'needs/([0-9]+)', input)

        if len(parsed_data) != 1:
            raise ValueError('Invalid input data, need id not found!')

        return int(parsed_data[0])
