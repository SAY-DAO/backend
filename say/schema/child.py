from datetime import date

from pydantic import BaseModel
from typing import List


class FamilyMemberSchema(BaseModel):
    role: int
    username: str


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
    id: int
    is_gone: bool
    sayName: str
    spent_credit: int
    userRole: int
    voiceUrl: str
