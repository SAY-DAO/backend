from datetime import datetime

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from say.models import City
from say.models import Country
from say.models import State


def basedata(db):

    from say.models.user_model import User

    # Creating DB Session
    session_factory = sessionmaker(
        db,
        autoflush=False,
        autocommit=False,
        expire_on_commit=True,
        twophase=False,
    )

    session = scoped_session(session_factory)

    # Inserting BaseData

    say_user = User(
        userName='SAY',
        password='ChangeThis!!!',
        emailAddress='say@say.company',
        avatarUrl='/public/resources/img/logo.png',
        firstName='SAY',
        lastName='',
        city=1,  # Tehran
        country=1,  # Iran
        lastLogin=datetime.utcnow(),
    )
    session.add(say_user)

    iran = Country(
        id=103,
        name='Iran',
        iso3='IRN',
        numeric_code='364',
        iso2='IR',
        phonecode='98',
        capital='Tehran',
        currency='IRR',
        currency_name='Iranian rial',
        currency_symbol='﷼',
        tld='.ir',
        native='ایران',
        region='Asia',
        subregion='Southern Asia',
        timezones='[{\"zoneName\":\"Asia/Tehran\",\"gmtOffset\":12600,\"gmtOffsetName\":\"UTC+03:30\",\"abbreviation\":\"IRDT\",\"tzName\":\"Iran Daylight Time\"}]',
        translations='{\"kr\":\"이란\",\"br\":\"Irã\",\"pt\":\"Irão\",\"nl\":\"Iran\",\"hr\":\"Iran\",\"fa\":\"ایران\",\"de\":\"Iran\",\"es\":\"Iran\",\"fr\":\"Iran\",\"ja\":\"イラン・イスラム共和国\",\"cn\":\"伊朗\"}',
        latitude=32,
        longitude=53,
        emoji='🇮🇷',
        emojiU='U+1F1EE U+1F1F7',
        flag=1,
    )
    session.add(iran)

    tehran_state = State(
        id=3945,
        name='Tehran',
        country_code='IR',
        fips_code=26,
        iso2=23,
        latitude="35.72484160",
        longitude="51.38165300",
        type='province',
        flag=1,
    )
    iran.states.append(tehran_state)

    tehran_city = City(
        id=135129,
        name='Tehran',
        state_id=3945,
        state_code="23",
        country_code='IR',
        latitude="35.72484160",
        longitude="51.38165300",
    )
    iran.cities.append(tehran_city)

    try:
        session.commit()
    except:
        session.rollback()
