from .base import CamelModel


class ParticipantSchema(CamelModel):
    id: int
    id_family: int
    id_user: int
    id_need: int
    type: str = None
    user_role: int = None
    paid: int
