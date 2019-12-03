from .digikala import get_data


def surname(gender):
    surname = ''

    if gender == False:
        surname = 'سرکار خانم'
    else:
        surname = 'جناب اقای'

    return surname
