import { useEffect, useState, useCallback } from 'react';
import {
  Globe,
  Rss,
  MessageSquare,
  Github,
  Loader2,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  Play,
  TestTube,
  Radio,
  Key,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { getSources, collectFromSources, testSource, getSettings, updateSetting } from '../api';
import type { SourceInfo, CollectResponse } from '../types';

const SOURCE_ICONS: Record<string, React.ElementType> = {
  web_search: Globe,
  rss_feed: Rss,
  hackernews: MessageSquare,
  github_advisory: Github,
};

const SOURCE_COLORS: Record<string, string> = {
  web_search: 'text-blue-400 bg-blue-500/15',
  rss_feed: 'text-orange-400 bg-orange-500/15',
  hackernews: 'text-amber-400 bg-amber-500/15',
  github_advisory: 'text-purple-400 bg-purple-500/15',
};

export default function DataSourcePage() {
  const [sources, setSources] = useState<SourceInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [collecting, setCollecting] = useState(false);
  const [testingSource, setTestingSource] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [collectResult, setCollectResult] = useState<CollectResponse | null>(null);
  const [selectedSources, setSelectedSources] = useState<Set<string>>(new Set());
  const [expandedSource, setExpandedSource] = useState<string | null>(null);
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [savingKey, setSavingKey] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const [sourcesData, settingsData] = await Promise.all([
        getSources(),
        getSettings(),
      ]);
      setSources(sourcesData.sources);

      const keys: Record<string, string> = {};
      if (settingsData.settings?.tavily_api_key?.value) {
        keys.tavily_api_key = settingsData.settings.tavily_api_key.value;
      }
      if (settingsData.settings?.github_token?.value) {
        keys.github_token = settingsData.settings.github_token.value;
      }
      setApiKeys(keys);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '加载数据源失败';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCollect = async () => {
    try {
      setCollecting(true);
      setError(null);
      setCollectResult(null);

      const sourceIds = selectedSources.size > 0 ? Array.from(selectedSources) : undefined;
      const result = await collectFromSources(sourceIds, 20);
      setCollectResult(result);
      setSuccess(result.message);
      setTimeout(() => setSuccess(null), 5000);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '采集失败';
      setError(msg);
    } finally {
      setCollecting(false);
    }
  };

  const handleTest = async (sourceId: string) => {
    try {
      setTestingSource(sourceId);
      setError(null);
      const result = await testSource(sourceId);
      if (result.success) {
        setSuccess(`${sourceId}: ${result.message}`);
      } else {
        setError(`${sourceId}: ${result.message}`);
      }
      setTimeout(() => { setSuccess(null); setError(null); }, 4000);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '测试失败';
      setError(msg);
    } finally {
      setTestingSource(null);
    }
  };

  const handleSaveApiKey = async (keyName: string, value: string) => {
    try {
      setSavingKey(keyName);
      await updateSetting(keyName, value);
      setSuccess(`${keyName} 已保存`);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '保存失败';
      setError(msg);
    } finally {
      setSavingKey(null);
    }
  };

  const toggleSource = (id: string) => {
    const next = new Set(selectedSources);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedSources(next);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
          <p className="text-slate-400 text-sm">正在加载数据源...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/15">
            <Radio className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-white">数据源管理</h1>
            <p className="text-sm text-slate-400">从公开渠道采集黑灰产威胁情报</p>
          </div>
        </div>
        <button
          onClick={fetchData}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
            text-slate-400 hover:text-white hover:bg-slate-700/50
            transition-colors text-sm"
        >
          <RefreshCw className="w-4 h-4" />
          <span>刷新</span>
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
          <button onClick={() => setError(null)} className="ml-auto text-red-400 hover:text-red-300">✕</button>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{success}</span>
          <button onClick={() => setSuccess(null)} className="ml-auto text-emerald-400 hover:text-emerald-300">✕</button>
        </div>
      )}

      {collectResult && (
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-4">
          <h3 className="text-sm font-semibold text-white mb-3">采集结果</h3>
          <div className="grid grid-cols-3 gap-4 mb-3">
            <div className="text-center">
              <div className="text-2xl font-bold text-cyan-400">{collectResult.total_collected}</div>
              <div className="text-xs text-slate-500">总采集</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-emerald-400">{collectResult.total_new}</div>
              <div className="text-xs text-slate-500">新增</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-amber-400">{collectResult.total_duplicates}</div>
              <div className="text-xs text-slate-500">重复</div>
            </div>
          </div>
          {Object.entries(collectResult.source_stats).length > 0 && (
            <div className="space-y-1">
              {Object.entries(collectResult.source_stats).map(([id, stats]) => (
                <div key={id} className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">{id}</span>
                  <span className="text-slate-500">
                    采集 {stats.collected} / 新增 {stats.new} / 重复 {stats.duplicates}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <div className="space-y-3">
        {sources.map((source) => {
          const Icon = SOURCE_ICONS[source.id] || Globe;
          const colorClass = SOURCE_COLORS[source.id] || 'text-slate-400 bg-slate-500/15';
          const isSelected = selectedSources.has(source.id);
          const isExpanded = expandedSource === source.id;
          const needsKey = source.requires_api_key;
          const hasKey = source.api_key_name ? !!apiKeys[source.api_key_name] : true;

          return (
            <div
              key={source.id}
              className={`rounded-xl border bg-slate-800 transition-colors ${
                isSelected ? 'border-cyan-500/50 bg-cyan-500/5' : 'border-slate-700'
              }`}
            >
              <div
                className="flex items-center gap-3 p-4 cursor-pointer"
                onClick={() => toggleSource(source.id)}
              >
                <div className={`p-2 rounded-lg ${colorClass}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-semibold text-white">{source.name}</h3>
                    {needsKey && (
                      <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium ${
                        hasKey ? 'bg-emerald-500/15 text-emerald-400' : 'bg-amber-500/15 text-amber-400'
                      }`}>
                        <Key className="w-3 h-3" />
                        {hasKey ? '已配置' : '需配置'}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{source.description}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={(e) => { e.stopPropagation(); handleTest(source.id); }}
                    disabled={testingSource === source.id}
                    className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs
                      text-slate-400 hover:text-white hover:bg-slate-700/50
                      transition-colors disabled:opacity-50"
                  >
                    {testingSource === source.id ? (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    ) : (
                      <TestTube className="w-3 h-3" />
                    )}
                    测试
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); setExpandedSource(isExpanded ? null : source.id); }}
                    className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {isExpanded && source.api_key_name && (
                <div className="px-4 pb-4 border-t border-slate-700/50 pt-3">
                  <div className="flex items-center gap-2 mb-2">
                    <Key className="w-3.5 h-3.5 text-slate-400" />
                    <span className="text-xs font-medium text-slate-300">
                      {source.api_key_name === 'tavily_api_key' ? 'Tavily API Key' : 'GitHub Token'}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <input
                      type="password"
                      value={apiKeys[source.api_key_name] || ''}
                      onChange={(e) => setApiKeys(prev => ({ ...prev, [source.api_key_name!]: e.target.value }))}
                      placeholder={source.api_key_name === 'tavily_api_key' ? 'tvly-...' : 'ghp_...'}
                      className="flex-1 px-3 py-1.5 rounded-lg bg-slate-700/50 border border-slate-600
                        text-sm text-slate-200 placeholder-slate-500
                        focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30"
                    />
                    <button
                      onClick={() => handleSaveApiKey(source.api_key_name!, apiKeys[source.api_key_name!] || '')}
                      disabled={savingKey === source.api_key_name}
                      className="px-3 py-1.5 rounded-lg bg-cyan-500/15 text-cyan-400 border border-cyan-500/30
                        hover:bg-cyan-500/25 transition-colors text-xs disabled:opacity-50"
                    >
                      {savingKey === source.api_key_name ? <Loader2 className="w-3 h-3 animate-spin" /> : '保存'}
                    </button>
                  </div>
                  {source.api_key_name === 'tavily_api_key' && (
                    <p className="text-[10px] text-slate-600 mt-1.5">
                      免费注册: <a href="https://tavily.com" target="_blank" rel="noopener noreferrer" className="text-cyan-500/70 hover:text-cyan-400">https://tavily.com</a> (免费1000次/月)
                    </p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleCollect}
          disabled={collecting}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg
            bg-cyan-500/15 text-cyan-400 border border-cyan-500/30
            hover:bg-cyan-500/25 transition-colors disabled:opacity-50"
        >
          {collecting ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          <span>{collecting ? '采集中...' : `开始采集${selectedSources.size > 0 ? ` (${selectedSources.size}个源)` : ' (全部)'}`}</span>
        </button>
        {selectedSources.size > 0 && (
          <button
            onClick={() => setSelectedSources(new Set())}
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            清除选择
          </button>
        )}
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
        <h3 className="text-sm font-medium text-slate-300 mb-2">数据源说明</h3>
        <ul className="text-xs text-slate-400 space-y-1.5 list-disc list-inside">
          <li><strong className="text-slate-300">Web搜索</strong> - 通过 Tavily API 搜索公开威胁情报，需配置 API Key</li>
          <li><strong className="text-slate-300">RSS订阅</strong> - 从安全客、FreeBuf、KrebsOnSecurity 等安全资讯网站采集，无需 API Key</li>
          <li><strong className="text-slate-300">HackerNews</strong> - 采集安全相关的技术新闻和讨论，无需 API Key</li>
          <li><strong className="text-slate-300">GitHub安全公告</strong> - 采集开源生态安全漏洞和恶意包信息，无需 API Key（配置Token可提升速率）</li>
          <li>所有数据均来自公开渠道，不涉及非法数据获取</li>
          <li>采集的情报会自动进入分析流程（清洗→分类→实体提取→深度分析）</li>
        </ul>
      </div>
    </div>
  );
}
