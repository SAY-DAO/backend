from requests import request


BASE_URL = 'https://sayapp.company'
API_URL = f'{BASE_URL}/api/v2'

PANEL_LOGIN = f'{API_URL}/panel/auth/login'
ACTIVE_CHILDREN_URL = f'{API_URL}/child/actives'
GET_FAMILIES = f'{API_URL}/family/all'
GET_INVITATION = f'{API_URL}/invitations/'
GET_CHILD = f'{API_URL}/child/childId=%s&confirm=1'
GET_CHILD_BY_TOKEN = f'{BASE_URL}/search-result?token=%s'


def login(user, passwd):
    res = request(
        'POST',
        PANEL_LOGIN,
        data=dict(
            username=user,
            password=passwd,
        ),
    )

    if res.status_code != 200:
        print('invalid username or password')
        exit(-1)

    return res.json()['access_token']


def get_child(id):
    res = request(
        'GET',
        GET_CHILD % id,
        headers=dict(authorization=auth),
    )
    return res.json()


def get_invitation(family_id):
    res = request(
        'POST',
        GET_INVITATION,
        headers=dict(authorization=auth),
        data=dict(family_id=family_id),
    )
    return res.json()


def get_families():
    ugly_list = request(
        'GET',
        GET_FAMILIES,
        headers=dict(authorization=auth),
    ).json()

    families = [
        dict(child_id=f['ChildId'], id=f['FamilyId']) for _, f in ugly_list.items()
    ]
    return families


print('admin username: ')
user = input()

print('admin password: ')
passwd = input()

print()

auth = login(user, passwd)

res = request('GET', ACTIVE_CHILDREN_URL, headers=dict(Authorization=auth))

if res.status_code == 401 or res.status_code == 403:
    print('Invalid auth token')
    exit()


active_children_ids = set()
for child in res.json():
    active_children_ids.add(child['id'])

print(
    'id',
    'generatedCode',
    'sayName',
    'link',
    sep=',',
)

for family in get_families():
    child = get_child(family['child_id'])
    try:
        if child['id'] not in active_children_ids:
            continue

        inv = get_invitation(family['id'])
        print(
            child['id'],
            child['generatedCode'],
            child['sayName'],
            GET_CHILD_BY_TOKEN % inv['token'],
            sep=',',
        )

    except:
        continue
