from say.schema.base import CamelModel


class MigrateSocialWorkerChildrenSchema(CamelModel):
    destination_social_worker_id: int
