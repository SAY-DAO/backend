from datetime import datetime

from say.schema.base import CamelModel


class ChildMigrationSchema(CamelModel):
    id: int
    child_id: int
    new_sw_id: int
    old_sw_id: int
    migrated_at: datetime
    new_generated_code: str
    old_generated_code: str
