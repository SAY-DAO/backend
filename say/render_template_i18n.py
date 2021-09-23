import os
from datetime import datetime

from flask import render_template

from say.formatters import expose_datetime
from say.formatters import int_formatter
from say.locale import ChangeLocaleTo
from say.locale import get_locale


def render_template_i18n(path, *args, locale=None, date_with_year=True, **kwargs):

    if not locale:
        return render_template(path, *args, int_formatter=int_formatter, **kwargs)

    # locale is str or Locale object, so we need to make sure it is str
    locale = str(locale) or get_locale()
    with ChangeLocaleTo(locale):
        locale_path = os.path.join(locale, path)
        for k, v in kwargs.items():
            if isinstance(v, datetime):
                kwargs[k] = expose_datetime(
                    v,
                    locale=locale,
                    with_year=date_with_year,
                )

        return render_template(
            locale_path, *args, int_formatter=int_formatter, **kwargs
        )
