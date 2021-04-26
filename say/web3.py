from web3 import Web3

from say.config import configs


w3 = Web3(Web3.HTTPProvider(configs.INFURA_URL))
