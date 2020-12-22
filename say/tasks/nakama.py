from datetime import datetime, timedelta

from say.celery import celery
from say.config import configs
from say.orm import obj_to_dict, safe_commit


@celery.task(base=celery.DBTask, bind=True)
def update_nakama_txs(self):
    from say.models.nakama import NakamaTx

    tx_ids = self.session.query(NakamaTx.id).filter(
        NakamaTx.is_confirmed == False,
        NakamaTx.created > datetime.utcnow() - timedelta(days=configs.ORPHAN_NAKAMA_TX_RANGE)
    )
    for tx_id in tx_ids:
        update_nakama_tx.delay(tx_id[0])

    return list(tx_ids)


@celery.task(base=celery.DBTask, bind=True)
def update_nakama_tx(self, tx_id):
    from say.models.nakama import NakamaTx

    tx = self.session.query(NakamaTx).get(tx_id)
    tx.update()
    safe_commit(self.session)
    return obj_to_dict(tx)
