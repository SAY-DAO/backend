from sqlalchemy import Column, ForeignKey, String, Integer, Date, Boolean, \
    Text, Numeric, DateTime, FLOAT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, synonym


base = declarative_base()
