from datetime import datetime, time

from sqlalchemy.dialects.postgresql import HSTORE

from . import *


"""
Child Model
"""


class Child(base, Timestamp):
    __tablename__ = "child"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    id_ngo = Column(Integer, ForeignKey('ngo.id'), nullable=False)
    id_social_worker = Column(Integer, ForeignKey('social_worker.id'), nullable=False)

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
    city = Column(Integer, nullable=False)  # 1:tehran | 2:karaj / [must be change after using real country/city api]

    awakeAvatarUrl = Column(String, nullable=False)
    sleptAvatarUrl = Column(String, nullable=False)

    gender = Column(Boolean, nullable=False)  # true:male | false:female

    bio_translations = Column(HSTORE)
    bio = translation_hybrid(bio_translations)

    bio_summary_translations = Column(HSTORE)
    bioSummary = translation_hybrid(bio_summary_translations)

    voiceUrl = Column(String, nullable=False)
    birthPlace = Column(Text, nullable=True)  # 1:tehran | 2:karaj / [must be change after using real country/city api]
    birthDate = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    housingStatus = Column(
        Integer, nullable=True
    )  # 0:Street child | 1:Living at home | 2:Care centers
    familyCount = Column(Integer, nullable=True)
    sayFamilyCount = Column(Integer, nullable=False, default=0)
    education = Column(
        Integer, nullable=True
    )  # -3:Deprived of education | -2:Kinder garden | -1:Not attending | 0:Pre-school | 1:1st grade | 2:2nd grade | ... | 13:University
    status = Column(Integer, nullable=True)  # happy, sad, etc
    existence_status = Column(Integer, nullable=True, default=1)  # 0: dead :( | 1: alive and present | 2: alive but gone
    isDeleted = Column(Boolean, nullable=False, default=False)
    isConfirmed = Column(Boolean, nullable=False, default=False)
    confirmUser = Column(Integer, nullable=True)
    confirmDate = Column(Date, nullable=True)
    generatedCode = Column(String, nullable=False)
    isMigrated = Column(Boolean, nullable=False, default=False)
    migratedId = Column(Integer, nullable=True)
    migrateDate = Column(Date, nullable=True)

    @hybrid_property
    def avatarUrl(self):
        # TODO: Use right timezone
        now_time = datetime.utcnow().time()

        if self.country == '98' or self.country == '93':
            now_time += time(4, 30)

        if now_time >= time(21, 00) or now_time <= time(8, 00):
            return self.sleptAvatarUrl
        else:
            return self.awakeAvatarUrl

    @avatarUrl.expression
    def avatarUrl(cls):
        return

    @aggregated('needs', Column(Integer, default=0, nullable=False))
    def done_needs_count(cls):
        from . import Need
        # passing a dummy '1' to count
        return func.count('1') \
            .filter(Need.status > 1) \

    @aggregated('needs.payments', Column(Integer, default=0, nullable=False))
    def spent_credit(cls):
        from . import Payment
        return coalesce(
            func.sum(Payment.need_amount),
            0,
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
