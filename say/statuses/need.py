class NeedStatuses:

    product_en = {
        '0': 'Not paid',
        '1': 'Partialy paid',
        '2': 'Completely paid',
        '3': 'Purchased',
        '4': 'Delivered to NGO',
        '5': 'Delivered to child',
    }

    service_en = {
        '0': 'Not paid',
        '1': 'Partially paid',
        '2': 'Completely paid',
        '3': 'Money sent to NGO',
        '4': 'Servcice delivered to child',
    }

    product_fa = {
        '0': 'پرداخت نشده',
        '1': 'جزء از کل',
        '2': 'تمام هزینه %s پرداخت شده است',
        '3': '%s خریداری شده است و به زودی توسط دیجی‌کالا به انجمن می‌رسد',
        '4': 'تحویل به انجمن',
        '5': '%s به دست %s رسید',
    }

    service_fa = {
        '0': 'پرداخت نشده',
        '1': 'جزء از کل',
        '2': 'تمام هزینه %s پرداخت شده است',
        '3': 'مبلغ %s تومان به حساب انجمن واریز شده است تا هزینه %s پرداخت شود',
        '4': 'هزینه %s برای %s تمام و کمال پرداخت شد',
    }

    statuses = dict(
        product_en = product_en,
        product_fa = product_fa,
        service_en = service_en,
        service_fa = service_fa,
    )

    @classmethod
    def get(cls, status, type_name, locale):
        key = f'{type_name}_{locale}'
        return cls.statuses[key][str(status)]

