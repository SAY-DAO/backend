from flask import Flask
from say.config import db
from sqlalchemy import Table, Column,ForeignKey, String, Integer, Date, Boolean, Text, Numeric , DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


base = declarative_base()




class NGO(base):
    __tablename__ = 'ngo'

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer)
    city_id = Column(Integer)
    coordinator_id = Column(Integer)
    name = Column(String)
    postalAddress = Column(Text)
    emailAddress = Column(String)
    phoneNumber = Column(String)
    logoUrl = Column(String)
    balance = Column(Integer)
    socialWorkerCount = Column(String)
    childrenCount = Column(String)
    registerDate = Column(Date)
    lastUpdateDate = Column(Date)
    isActive = Column(Boolean)
    isDeleted = Column(Boolean)




class Privileges(base):
    __tablename__ = 'social_worker_type'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    privilege = Column(Integer)




class socialWorker(base):
    __tablename__ = 'social_worker'

    id = Column(Integer, primary_key=True)
    generatedCode = Column(String)
    ngo_id = Column(Integer, ForeignKey(NGO.id))
    country_id = Column(Integer)
    city_id = Column(Integer)
    type_id = Column(Integer, ForeignKey(Privileges.id))
    firstName = Column(String)
    lastName = Column(String)
    userName = Column(String)
    password = Column(String)
    birthCertificateNumber = Column(String)
    idNumber = Column(String)
    idCardUrl = Column(String)
    passportNumber = Column(String)
    passportUrl = Column(String)

    # 0 for femail and 1 for male
    gender = Column(Boolean)
    birthDate = Column(Date)
    phoneNumber = Column(String)
    emergencyPhoneNumber = Column(String)
    emailAddress = Column(String)
    telegramId = Column(String)
    postalAddress = Column(String)
    avatarUrl = Column(String)
    childCount = Column(String)
    needCount = Column(String)
    bankAccountNumber = Column(String)
    bankAccountShebaNumber = Column(String)
    bankAccountCardNumber = Column(String)
    registerDate = Column(Date)
    lastUpdateDate = Column(Date)
    lastLoginDate = Column(Date)
    lastLogoutDate = Column(Date)
    isActive = Column(Boolean)
    isDeleted = Column(Boolean)

    privilege = relationship('Privileges', foreign_keys='socialWorker.type_id')
    ngo = relationship('NGO', foreign_keys='socialWorker.ngo_id')





class Activity(base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True)
    socialworker_id = Column(Integer, ForeignKey(socialWorker.id))
    activityCode = Column(Integer)

    socialworker = relationship('socialWorker', foreign_keys='Activity.socialworker_id')





# social_worker = socialWorker(generatedCode="4ss5sd4", ngo_id=1, country_id=1, city_id=2, type_id=1, firstName="Elham", lastName="Navidi", userName="eli", password="2016", birthCertificateNumber="2016", idNumber="2016", idCardUrl="2016", passportNumber="2016", passportUrl="2016", gender=True, birthDate="04/06/1994", phoneNumber="0937", emergencyPhoneNumber="2016", emailAddress="2016", telegramId="2016", postalAddress="2016", avatarUrl="2016", childCount="2016", needCount="2016", bankAccountNumber="2016", bankAccountShebaNumber="2016", bankAccountCardNumber="2016", registerDate="04-06-2019", lastUpdateDate="04-06-2019", lastLoginDate="04-06-2019", lastLogoutDate="04-06-2019", isActive=True, isDeleted=False)  

# session.add(social_worker)  
# session.commit()