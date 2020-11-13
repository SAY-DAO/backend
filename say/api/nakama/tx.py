import web3
from eth_utils import is_hexstr
from flask_restful import Resource
from say.decorators import json
from say.models import session
from say.models.nakama.nakama_tx import NakamaTx
from say.orm import safe_commit

from .. import api, swag_from


class SubmitTx(Resource):

    @json
    @swag_from('../docs/nakama/submit_tx.yml')
    def post(self, tx_hash):
        if not is_hexstr(tx_hash):
            return dict(message='Invalid tx hash'), 400

        tx_hash = tx_hash.lower()
        tx = session.query(NakamaTx).get(tx_hash)
    
        if tx:
            return dict(message='Tx Exists'), 400
        
        tx = NakamaTx(id=tx_hash)
        session.add(tx)
        try:
            tx.update()
        except web3.exceptions.TransactionNotFound:
            print(f'Tx {tx_hash} not mined yet')
            
        safe_commit(session)
        return tx

api.add_resource(SubmitTx, '/api/v2/nakama/<string:tx_hash>')
