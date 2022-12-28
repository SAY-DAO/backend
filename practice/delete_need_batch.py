import requests


file = '/home/rhonin2/Downloads/delete_needs.csv'
token = 'Bearer '
url = 'https://api.sayapp.company/api/v2/need/delete/needId=%s'
need_ids = []
failed_needs = []

with open(file) as f:
    need_ids = f.read().split('\n')[1:-1]

headers = {'Authorization': token}

for id in need_ids:
    print(f'deleting {id}')
    try:
        response = requests.patch(url % id, headers=headers)
        if response.status_code == 401:
            raise Exception('Bad token')

        if response.status_code != 200:
            print(f'unable to delete {id}')
            failed_needs.append(id)
    except requests.exceptions.HTTPError:
        print(f'unable to delete {id}')
        failed_needs.append(id).append(id)

print('failed: ', failed_needs)
