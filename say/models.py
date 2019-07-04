from flask import Flask
from say.config import db
from sqlalchemy import Table, Column,ForeignKey, String, Integer, Date, Boolean, Text, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


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
    balance = Column(Numeric)
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
    type_id = Column(Integer)
    firstName = Column(String)
    lastName = Column(String)
    userName = Column(String)
    password = Column(String)
    birthCertificateNumber = Column(String)
    idNumber = Column(String)
    idCardUrl = Column(String)
    passportNumber = Column(String)
    passportUrl = Column(String)
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

 





class Activity(base):
    __tablename__ = 'activity'

    id = Column(Integer, primary_key=True)
    socialworker_id = Column(Integer)
    activityCode = Column(Integer)

    # socialworker = relationship('socialWorker', foreign_keys='Activity.socialworker_id')
