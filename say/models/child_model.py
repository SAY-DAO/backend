from datetime import time

import pytz
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import column_property

from say.orm.types import ResourceURL

from ..orm import session
from . import *
from .need_model import Need


"""
Child Model
"""


class Child(base, Timestamp):
    __tablename__ = "child"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_ngo = Column(Integer, ForeignKey('ngo.id'), nullable=False, index=True)
    id_social_worker = Column(
        Integer, ForeignKey('social_worker.id'), nullable=False, index=True
    )

    firstName_translations = Column(HSTORE)
    firstName = translation_hybrid(firstName_translations)

    lastName_translations = Column(HSTORE)
    lastName = translation_hybrid(lastName_translations)

    sayname_translations = Column(HSTORE)
    sayName = translation_hybrid(sayname_translations)

    phoneNumber = Column(Integer, nullable=False)
    nationality = Column(Integer, nullable=True)  # 98:iranian | 93:afghan
    country = Column(
        Integer, nullable=False
    )  # 98:iran | 93:afghanistan | ... (real country codes) / [must be change after using real country/city api]
    city = Column(
        Integer, nullable=False
    )  # 1:tehran | 2:karaj / [must be change after using real country/city api]

    awakeAvatarUrl = Column(ResourceURL, nullable=False)
    sleptAvatarUrl = Column(ResourceURL, nullable=False)

    gender = Column(Boolean, nullable=False)  # true:male | false:female

    bio_translations = Column(HSTORE)
    bio = translation_hybrid(bio_translations)

    bio_summary_translations = Column(HSTORE)
    bioSummary = translation_hybrid(bio_summary_translations)
    sayFamilyCount = Column(Integer, nullable=False, default=0)
    voiceUrl = Column(ResourceURL, nullable=False)
    birthPlace = Column(
        Text, nullable=True
    )  # 1:tehran | 2:karaj / [must be change after using real country/city api]
    birthDate = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    housingStatus = Column(
        Integer, nullable=True
    )  # 0:Street child | 1:Living at home | 2:Care centers
    familyCount = Column(Integer, nullable=True)
    education = Column(
        Integer, nullable=True
    )  # -3:Deprived of education | -2:Kinder garden | -1:Not attending | 0:Pre-school | 1:1st grade | 2:2nd grade | ... | 13:University
    status = Column(Integer, nullable=True)  # happy, sad, etc
    existence_status = Column(
        Integer, nullable=True, default=1, index=True
    )  # 0: dead :( | 1: alive and present | 2: alive but gone | 3: Temporarry gone
    isDeleted = Column(Boolean, nullable=False, default=False, index=True)
    isConfirmed = Column(Boolean, nullable=False, default=False)
    confirmUser = Column(Integer, nullable=True)
    confirmDate = Column(Date, nullable=True)
    generatedCode = Column(String, nullable=False, index=True)
    isMigrated = Column(Boolean, nullable=False, default=False, index=True)
    migratedId = Column(Integer, nullable=True, index=True)
    migrateDate = Column(Date, nullable=True)

    familyId = association_proxy('family', 'id')
    socialWorkerGeneratedCode = association_proxy('social_worker', 'generatedCode')
    childFamilyMembers = association_proxy('family', 'members')

    @hybrid_property
    def avatarUrl(self):
        # TODO: Use right timezone
        now_time = datetime.utcnow().time()

        if self.country == 98 or self.country == 93:
            tz = pytz.timezone('Asia/Tehran')
            now_time = datetime.now(tz).time()

        if now_time >= time(21, 00) or now_time <= time(8, 00):
            return self.sleptAvatarUrl
        else:
            return self.awakeAvatarUrl

    @avatarUrl.expression
    def avatarUrl(cls):
        # FIXME: Use right timezone
        tz = pytz.timezone('Asia/Tehran')
        now_time = datetime.now(tz).time()

        if now_time >= time(21, 00) or now_time <= time(8, 00):
            return cls.sleptAvatarUrl
        else:
            return cls.awakeAvatarUrl

    @hybrid_property
    def is_gone(self):
        return self.existence_status != 1

    @is_gone.expression
    def is_gone(cls):
        return cls.existence_status != 1

    done_needs_count = column_property(
        select(
            [
                coalesce(
                    func.count(Need.id),
                    0,
                )
            ]
        )
        .where(
            and_(
                Need.status >= 2,
                Need.isDeleted.is_(False),
                Need.child_id == id,
            )
        )
        .correlate_except(Need),
    )

    spent_credit = column_property(
        select(
            [
                coalesce(
                    func.sum(Need.paid),
                    0,
                )
            ]
        )
        .where(and_(Need.child_id == id, Need.isDeleted.is_(False)))
        .correlate_except(Need),
    )

    needs = relationship(
        'Need',
        back_populates='child',
        primaryjoin='and_(Need.child_id==Child.id, ~Need.isDeleted)',
    )
    family = relationship('Family', back_populates='child', uselist=False)

    ngo = relationship("Ngo", foreign_keys="Child.id_ngo")

    social_worker = relationship(
        "SocialWorker",
        foreign_keys=id_social_worker,
        back_populates='children',
    )
    migrations = relationship(
        'ChildMigration',
        back_populates='child',
    )

    @classmethod
    def get_actives(cls):
        from . import Need

        return (
            session.query(cls)
            .join(Need)
            .filter(
                Child.isConfirmed.is_(True),
                Child.isDeleted.is_(False),
                Child.is_gone.is_(False),
                Child.isMigrated.is_(False),
                Need.isConfirmed.is_(True),
                Need.isDeleted.is_(False),
            )
        )

    def migrate(self, new_sw):
        assert new_sw.id != self.social_worker.id

        from .child_migration_model import ChildMigration

        old_sw = self.social_worker
        old_generated_code = self.generatedCode
        new_generated_code = (
            new_sw.generatedCode + format(new_sw.childCount + 1, '04d'),
        )

        migration = ChildMigration(
            new_sw=new_sw,
            old_sw=old_sw,
            old_generated_code=old_generated_code,
            new_generated_code=new_generated_code,
        )
        self.migrations.append(migration)

        new_sw.childCount += 1
        old_sw.childCount -= 1

        self.generatedCode = new_generated_code
        self.social_worker = new_sw

        return migration
