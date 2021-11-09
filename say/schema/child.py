from datetime import date
from datetime import datetime
from typing import List

from .base import BaseModel
from .base import CamelModel


class FamilyMemberSchema(BaseModel):
    role: int
    username: str
    isDeleted: bool = None
    member_id: int = None
    avatarUrl: str = None

    class Config:
        orm_mode = True


class FamilyMemberSchemaV3(CamelModel):
    user_role: int
    username: str
    is_deleted: bool = None
    user_id: int = None
    avatar_url: str = None

    class Config:
        orm_mode = True


class ChildSchema(BaseModel):
    avatarUrl: str
    bio: str
    bioSummary: str
    birthDate: date
    childFamilyMembers: List[FamilyMemberSchema] = []
    done_needs_count: int
    existence_status: int
    familyId: int
    gender: bool
    generatedCode: str
    id: int = None
    is_gone: bool
    sayName: str
    spent_credit: int
    voiceUrl: str
    socialWorkerGeneratedCode: str

    class Config:
        orm_mode = True


class ChildSchemaV3(CamelModel):
    avatarUrl: str
    bio: str
    bioSummary: str
    birthDate: date
    family_members: List[FamilyMemberSchemaV3] = []
    done_needs_count: int
    existence_status: int
    family_id: int
    gender: bool
    generatedCode: str
    id: int = None
    is_gone: bool
    sayName: str
    spent_credit: int
    voiceUrl: str
    social_worker_generated_code: str

    class Config:
        orm_mode = True


class UserChildSchema(ChildSchema):
    userRole: int = None


class UserChildSchemaV3(ChildSchemaV3):
    userRole: int = None


class Participant(BaseModel):
    user_avatar: str = None


class NeedSummary(BaseModel):
    id: int
    imageUrl: str
    name: str
    progress: float
    cost: int
    isDone: bool
    isUrgent: bool
    category: int
    type: int
    participants: List[Participant] = []
    created: datetime
    doneAt: datetime = None
    unpayable: bool = None
