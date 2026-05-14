import asyncio
import httpx

async def test():
    async with httpx.AsyncClient(timeout=180) as client:
        BASE = 'http://localhost:8001'

        print('从 GitHub 安全公告采集情报...')
        r = await client.post(
            f'{BASE}/api/sources/collect',
            json={'source_ids': ['github_advisory'], 'max_items_per_source': 10},
            timeout=180,
        )
        if r.status_code == 200:
            data = r.json()
            tc = data['total_collected']
            tn = data['total_new']
            td = data['total_duplicates']
            print(f'采集完成! 总采集={tc}, 新增={tn}, 重复={td}')
            for sid, stats in data.get('source_stats', {}).items():
                print(f'  {sid}: 采集={stats["collected"]}, 新增={stats["new"]}, 重复={stats["duplicates"]}')
        else:
            print(f'采集失败: {r.status_code} - {r.text[:300]}')

        r = await client.get(f'{BASE}/api/intelligence/stats')
        stats = r.json()
        ti = stats['total_items']
        pc = stats['pending_count']
        sd = stats['source_distribution']
        print(f'\n仪表盘统计: 总数={ti}, 待处理={pc}, 来源分布={sd}')

        r = await client.get(f'{BASE}/api/intelligence?page=1&page_size=1&status=pending')
        items = r.json()['items']
        if items:
            item_id = items[0]['id']
            src = items[0]['source_name']
            print(f'\n分析情报: {item_id[:8]}... (来源: {src})')
            ar = await client.post(f'{BASE}/api/analysis/{item_id}', timeout=60)
            if ar.status_code == 200:
                report = ar.json()
                rs = report['risk_score']
                sm = report['summary'][:100]
                print(f'分析完成! 风险评分={rs}')
                print(f'摘要: {sm}...')
            else:
                print(f'分析失败: {ar.status_code}')

asyncio.run(test())
