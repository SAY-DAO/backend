from datetime import date

from pydantic import BaseModel
from typing import List


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