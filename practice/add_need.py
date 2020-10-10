def insert(child_id):
    import pandas as pd
    from datetime import datetime
    from say.models.need_model import NeedModel
    from say.models.child_need_model import ChildNeedModel

    def cat(catt):
       if catt == 'Health':
           return 2
       elif catt == 'Growth':
           return 0
       return 1

    file = f'/home/rhonin/deleteme/DATA-ENTRY/children-data-entry/v2/001001000{child_id}/001001000{child_id}.xlsx'
    dfs = pd.read_excel(file, sheet_name='Needs')
    for i, r in dfs.iterrows():
        d = dict(r)
        print(d)
        n = NeedModel(
         createdAt=datetime.utcnow(),
         lastUpdate=datetime.utcnow(),
         name=d['Name\xa0'],
         category=cat(d['Category\xa0']),
         imageUrl='-',
         isUrgent=False,
         description=d['Description\xa0'],
         descriptionSummary=d['DescriptionSummary\xa0'],
         cost=d['Cost\xa0'],
         type=0,
        )

        cn = ChildNeedModel(id_child=child_id, need_relation=n)
        sm = sessionmaker(db)
        s = sm()
        s.add(n)
        s.add(cn)
        s.commit()
    return n
