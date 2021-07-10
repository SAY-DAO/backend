from datetime import date
from datetime import datetime
from typing import List

from .base import BaseModel


class FamilyMemberSchema(BaseModel):
    role: int
    username: str
    isDeleted: bool = None
    member_id: int = None


class UserChildSchema(BaseModel):
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
    userRole: int = None
    voiceUrl: str
    socialWorkerGeneratedCode: str


class Participant(BaseModel):
    user_avatar: str = None


class NeedSummary(BaseModel):
    id: int
    status: int
    isConfirmed: bool
    title: str = None
    imageUrl: str
    name: str
    progress: float
    cost: int
    isDone: bool
    isUrgent: bool
    category: int
    type: int
    created: datetime
    doneAt: datetime = None
    participants: List[Participant] = []
