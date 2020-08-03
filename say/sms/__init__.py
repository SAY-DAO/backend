from .meli_payamak import MeliPayamak
from ..config import config

sms_provider = MeliPayamak(
    config['MELI_PAYAMAK_USERNAME'],
    config['MELI_PAYAMAK_PASSWORD'],
    config['MELI_PAYAMAK_FROM'],
)
