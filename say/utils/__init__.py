def surname(gender):
    surname = ''

    if gender is False:
        surname = 'سرکار خانم'
    else:
        surname = 'جناب اقای'

    return surname


def clean_input(input: str):
    return input.strip()
