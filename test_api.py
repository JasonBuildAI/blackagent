import asyncio
import httpx

BASE_URL = 'http://localhost:8001'

async def test_api():
    async with httpx.AsyncClient(timeout=60) as client:
        print('=' * 60)
        print('黑灰产情报分析Agent - 全链路测试')
        print('=' * 60)

        # 1. Test health
        print('\n[1] 健康检查...')
        try:
            r = await client.get(f'{BASE_URL}/health')
            print(f'    状态: {r.status_code} - {r.json()}')
            assert r.status_code == 200, 'Health check failed'
        except Exception as e:
            print(f'    ❌ 错误: {e}')
            return

        # 2. Test settings
        print('\n[2] 系统设置...')
        try:
            r = await client.get(f'{BASE_URL}/api/settings')
            data = r.json()
            print(f'    状态: {r.status_code}')
            print(f'    设置项: {list(data["settings"].keys())}')
            assert r.status_code == 200
        except Exception as e:
            print(f'    ❌ 错误: {e}')

        # 3. Test stats
        print('\n[3] 仪表盘统计...')
        try:
            r = await client.get(f'{BASE_URL}/api/intelligence/stats')
            stats = r.json()
            print(f'    总情报数: {stats["total_items"]}')
            print(f'    严重告警: {stats["critical_alerts"]}')
            print(f'    已分析: {stats["analyzed_count"]}')
            print(f'    待处理: {stats["pending_count"]}')
            print(f'    风险分布: {stats["risk_distribution"]}')
            print(f'    来源分布: {stats["source_distribution"]}')
            print(f'    类别分布: {stats.get("category_distribution", {})}')
            assert r.status_code == 200
        except Exception as e:
            print(f'    ❌ 错误: {e}')

        # 4. Test list
        print('\n[4] 情报列表...')
        try:
            r = await client.get(f'{BASE_URL}/api/intelligence?page=1&page_size=5')
            data = r.json()
            print(f'    总数: {data["total"]}, 当前页: {len(data["items"])} 条')
            for item in data['items'][:3]:
                iid = item['id'][:8]
                src = item['source_type']
                risk = item['risk_level']
                st = item['status']
                print(f'    - ID={iid}... 来源={src} 风险={risk} 状态={st}')
            assert r.status_code == 200
        except Exception as e:
            print(f'    ❌ 错误: {e}')
            return

        # 5. Test ingest
        print('\n[5] 数据摄入...')
        try:
            r = await client.post(f'{BASE_URL}/api/intelligence/ingest', json={'count': 5})
            data = r.json()
            print(f'    生成: {data["total_generated"]}, 新增: {data["new_items"]}, 重复: {data["duplicates"]}')
            print(f'    消息: {data["message"]}')
            assert r.status_code == 200
        except Exception as e:
            print(f'    ❌ 错误: {e}')

        # 6. Test single analysis
        print('\n[6] 单条情报分析...')
        try:
            r = await client.get(f'{BASE_URL}/api/intelligence?page=1&page_size=1')
            items = r.json()['items']
            if items:
                item_id = items[0]['id']
                print(f'    分析情报: {item_id[:8]}...')
                ar = await client.post(f'{BASE_URL}/api/analysis/{item_id}')
                if ar.status_code == 200:
                    report = ar.json()
                    print(f'    ✅ 分析完成!')
                    print(f'    摘要: {report["summary"][:80]}...')
                    print(f'    风险评分: {report["risk_score"]}')
                    print(f'    作弊场景: {(report.get("cheat_scenario") or "")[:60]}...')
                    print(f'    恶意模式: {(report.get("malicious_pattern") or "")[:60]}...')
                    print(f'    技术链条: {(report.get("tech_chain") or "")[:60]}...')
                    print(f'    建议措施: {(report.get("recommendations") or "")[:60]}...')
                else:
                    print(f'    ❌ 分析失败: {ar.status_code} - {ar.text[:200]}')
            else:
                print('    ⚠️ 没有可分析的情报')
        except Exception as e:
            print(f'    ❌ 错误: {e}')

        # 7. Test get report
        print('\n[7] 获取分析报告...')
        try:
            r = await client.get(f'{BASE_URL}/api/intelligence?page=1&page_size=1&status=analyzed')
            items = r.json()['items']
            if items:
                item_id = items[0]['id']
                rr = await client.get(f'{BASE_URL}/api/analysis/{item_id}')
                if rr.status_code == 200:
                    report = rr.json()
                    print(f'    ✅ 报告获取成功')
                    print(f'    风险评分: {report["risk_score"]}')
                else:
                    print(f'    ❌ 报告获取失败: {rr.status_code}')
            else:
                print('    ⚠️ 没有已分析的情报')
        except Exception as e:
            print(f'    ❌ 错误: {e}')

        # 8. Test intelligence detail with entities
        print('\n[8] 情报详情(含实体)...')
        try:
            r = await client.get(f'{BASE_URL}/api/intelligence?page=1&page_size=1&status=analyzed')
            items = r.json()['items']
            if items:
                item_id = items[0]['id']
                dr = await client.get(f'{BASE_URL}/api/intelligence/{item_id}')
                if dr.status_code == 200:
                    detail = dr.json()
                    entities = detail.get('entities', [])
                    print(f'    ✅ 详情获取成功')
                    print(f'    实体数量: {len(entities)}')
                    for e in entities[:5]:
                        etype = e['entity_type']
                        eval_ = e['entity_value']
                        econf = e['confidence']
                        print(f'    - [{etype}] {eval_} (置信度: {econf})')
                else:
                    print(f'    ❌ 详情获取失败: {dr.status_code}')
            else:
                print('    ⚠️ 没有已分析的情报')
        except Exception as e:
            print(f'    ❌ 错误: {e}')

        # 9. Test batch analysis
        print('\n[9] 批量分析...')
        try:
            r = await client.get(f'{BASE_URL}/api/intelligence?page=1&page_size=3&status=pending')
            items = r.json()['items']
            if items:
                ids = [item['id'] for item in items]
                br = await client.post(f'{BASE_URL}/api/analysis/batch', json={'intelligence_ids': ids})
                if br.status_code == 200:
                    result = br.json()
                    print(f'    ✅ 批量分析完成')
                    print(f'    总数: {result["total"]}, 已分析: {result["analyzed"]}, 跳过: {result["skipped"]}')
                    if result['errors']:
                        print(f'    错误: {result["errors"][:3]}')
                else:
                    print(f'    ❌ 批量分析失败: {br.status_code}')
            else:
                print('    ⚠️ 没有待分析的情报')
        except Exception as e:
            print(f'    ❌ 错误: {e}')

        # 10. Test LLM config
        print('\n[10] LLM 配置...')
        try:
            r = await client.get(f'{BASE_URL}/api/settings/llm')
            config = r.json()
            print(f'    API Base: {config["api_base"]}')
            print(f'    Model: {config["model"]}')
            print(f'    启用状态: {config["enabled"]}')
            assert r.status_code == 200
        except Exception as e:
            print(f'    ❌ 错误: {e}')

        print('\n' + '=' * 60)
        print('全链路测试完成!')
        print('=' * 60)

if __name__ == '__main__':
    asyncio.run(test_api())
