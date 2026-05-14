import httpx

BASE = 'http://localhost:8001'
with httpx.Client() as c:
    r = c.get(f'{BASE}/api/settings/providers')
    data = r.json()
    print('服务商数量:', len(data['providers']))
    for p in data['providers']:
        print(f'  {p["id"]}: {p["name"]} ({len(p["models"])}个模型)')
        for m in p['models'][:2]:
            print(f'    - {m["id"]}: {m["name"]}')
        if len(p['models']) > 2:
            print(f'    ... 还有 {len(p["models"])-2} 个模型')
