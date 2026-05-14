import asyncio
import httpx

BASE_URL = 'http://localhost:8001'

async def test_api():
    async with httpx.AsyncClient(timeout=120) as client:
        print('=' * 60)
        print('黑灰产情报分析Agent - 全链路测试（含真实数据源）')
        print('=' * 60)

        # 1. Health
        print('\n[1] 健康检查...')
        r = await client.get(f'{BASE_URL}/health')
        print(f'    状态: {r.status_code} - {r.json()}')
        assert r.status_code == 200

        # 2. Settings (with new keys)
        print('\n[2] 系统设置（含新数据源配置项）...')
        r = await client.get(f'{BASE_URL}/api/settings')
        data = r.json()
        keys = list(data['settings'].keys())
        print(f'    设置项: {keys}')
        assert 'tavily_api_key' in keys, 'Missing tavily_api_key'
        assert 'github_token' in keys, 'Missing github_token'
        print('    ✅ 新增 tavily_api_key 和 github_token 配置项')

        # 3. Sources list
        print('\n[3] 数据源列表...')
        r = await client.get(f'{BASE_URL}/api/sources')
        sources = r.json()['sources']
        print(f'    可用数据源: {len(sources)} 个')
        for s in sources:
            print(f'    - {s["id"]}: {s["description"]} (需API Key: {s["requires_api_key"]})')
        assert len(sources) >= 4, 'Should have at least 4 sources'
        source_ids = [s['id'] for s in sources]
        assert 'web_search' in source_ids
        assert 'rss_feed' in source_ids
        assert 'hackernews' in source_ids
        assert 'github_advisory' in source_ids

        # 4. Test HackerNews source (no API key needed)
        print('\n[4] 测试 HackerNews 数据源...')
        r = await client.post(f'{BASE_URL}/api/sources/hackernews/test')
        result = r.json()
        print(f'    成功: {result["success"]}, 消息: {result["message"]}')
        if result['success']:
            print(f'    ✅ HackerNews 连接正常，获取到 {result["items_count"]} 条数据')

        # 5. Test GitHub Advisory source (no API key needed)
        print('\n[5] 测试 GitHub 安全公告数据源...')
        r = await client.post(f'{BASE_URL}/api/sources/github_advisory/test')
        result = r.json()
        print(f'    成功: {result["success"]}, 消息: {result["message"]}')
        if result['success']:
            print(f'    ✅ GitHub 安全公告连接正常，获取到 {result["items_count"]} 条数据')

        # 6. Test RSS Feed source (no API key needed)
        print('\n[6] 测试 RSS Feed 数据源...')
        r = await client.post(f'{BASE_URL}/api/sources/rss_feed/test')
        result = r.json()
        print(f'    成功: {result["success"]}, 消息: {result["message"]}')
        if result['success']:
            print(f'    ✅ RSS Feed 连接正常，获取到 {result["items_count"]} 条数据')

        # 7. Test Web Search source (needs API key)
        print('\n[7] 测试 Web Search 数据源（需 API Key）...')
        r = await client.post(f'{BASE_URL}/api/sources/web_search/test')
        result = r.json()
        print(f'    成功: {result["success"]}, 消息: {result["message"]}')
        if not result['success']:
            print('    ⚠️ Web Search 需要 Tavily API Key，可在设置页面配置')

        # 8. Collect from free sources (HackerNews + GitHub + RSS)
        print('\n[8] 从免费数据源采集情报...')
        r = await client.post(
            f'{BASE_URL}/api/sources/collect',
            json={
                'source_ids': ['hackernews', 'github_advisory'],
                'max_items_per_source': 10,
            },
            timeout=60,
        )
        if r.status_code == 200:
            data = r.json()
            print(f'    ✅ 采集完成!')
            print(f'    总采集: {data["total_collected"]}, 新增: {data["total_new"]}, 重复: {data["total_duplicates"]}')
            for sid, stats in data.get('source_stats', {}).items():
                print(f'    - {sid}: 采集={stats["collected"]}, 新增={stats["new"]}, 重复={stats["duplicates"]}')
        else:
            print(f'    ❌ 采集失败: {r.status_code} - {r.text[:200]}')

        # 9. Stats after collection
        print('\n[9] 采集后仪表盘统计...')
        r = await client.get(f'{BASE_URL}/api/intelligence/stats')
        stats = r.json()
        print(f'    总情报数: {stats["total_items"]}')
        print(f'    已分析: {stats["analyzed_count"]}')
        print(f'    待处理: {stats["pending_count"]}')
        print(f'    来源分布: {stats["source_distribution"]}')
        print(f'    类别分布: {stats.get("category_distribution", {})}')

        # 10. Analyze a real collected item
        print('\n[10] 分析真实采集的情报...')
        r = await client.get(f'{BASE_URL}/api/intelligence?page=1&page_size=1&status=pending')
        items = r.json()['items']
        if items:
            item_id = items[0]['id']
            src = items[0]['source_type']
            src_name = items[0]['source_name']
            print(f'    分析情报: {item_id[:8]}... (来源: {src}/{src_name})')
            ar = await client.post(f'{BASE_URL}/api/analysis/{item_id}', timeout=60)
            if ar.status_code == 200:
                report = ar.json()
                print(f'    ✅ 分析完成!')
                print(f'    摘要: {report["summary"][:80]}...')
                print(f'    风险评分: {report["risk_score"]}')
                print(f'    作弊场景: {(report.get("cheat_scenario") or "")[:60]}...')
                print(f'    恶意模式: {(report.get("malicious_pattern") or "")[:60]}...')
            else:
                print(f'    ❌ 分析失败: {ar.status_code}')
        else:
            print('    ⚠️ 没有待分析的情报')

        # 11. Intelligence detail with entities
        print('\n[11] 情报详情(含实体)...')
        r = await client.get(f'{BASE_URL}/api/intelligence?page=1&page_size=1&status=analyzed')
        items = r.json()['items']
        if items:
            item_id = items[0]['id']
            dr = await client.get(f'{BASE_URL}/api/intelligence/{item_id}')
            if dr.status_code == 200:
                detail = dr.json()
                entities = detail.get('entities', [])
                print(f'    ✅ 详情获取成功')
                print(f'    来源: {detail["source_type"]}/{detail["source_name"]}')
                print(f'    实体数量: {len(entities)}')
                for e in entities[:5]:
                    print(f'    - [{e["entity_type"]}] {e["entity_value"]} (置信度: {e["confidence"]})')
        else:
            print('    ⚠️ 没有已分析的情报')

        print('\n' + '=' * 60)
        print('全链路测试完成!')
        print('=' * 60)

if __name__ == '__main__':
    asyncio.run(test_api())
