import { useEffect, useState, useCallback } from 'react';
import {
  Settings as SettingsIcon,
  Key,
  Globe,
  Bot,
  Save,
  Loader2,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
  TestTube,
  ChevronDown,
  Sparkles,
  Radio,
} from 'lucide-react';
import { getSettings, getLLMConfig, updateSetting, testLLMConnection, getModelProviders } from '../api';
import type { SettingsResponse, LLMConfig, ProviderInfo } from '../types';

export default function Settings() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [llmConfig, setLLMConfig] = useState<LLMConfig | null>(null);
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [selectedProviderId, setSelectedProviderId] = useState('');
  const [selectedModelId, setSelectedModelId] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [customBaseUrl, setCustomBaseUrl] = useState('');
  const [showCustomUrl, setShowCustomUrl] = useState(false);

  const [tavilyKey, setTavilyKey] = useState('');
  const [githubToken, setGithubToken] = useState('');

  const selectedProvider = providers.find(p => p.id === selectedProviderId);
  const availableModels = selectedProvider?.models || [];

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [settingsData, llmData, providersData] = await Promise.all([
        getSettings(),
        getLLMConfig(),
        getModelProviders(),
      ]);

      setSettings(settingsData);
      setLLMConfig(llmData);
      setProviders(providersData.providers);

      if (settingsData.settings) {
        setApiKey(settingsData.settings.llm_api_key?.value || '');
        setTavilyKey(settingsData.settings.tavily_api_key?.value || '');
        setGithubToken(settingsData.settings.github_token?.value || '');

        const savedBase = settingsData.settings.llm_api_base?.value || '';
        const savedModel = settingsData.settings.llm_model?.value || '';

        const matchedProvider = providersData.providers.find(p => p.api_base === savedBase);
        if (matchedProvider) {
          setSelectedProviderId(matchedProvider.id);
          setSelectedModelId(savedModel);
          setShowCustomUrl(false);
        } else if (savedBase) {
          setSelectedProviderId('custom');
          setSelectedModelId(savedModel);
          setCustomBaseUrl(savedBase);
          setShowCustomUrl(true);
        } else {
          setSelectedProviderId('openai');
          setSelectedModelId('gpt-4.1-mini');
          setShowCustomUrl(false);
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : '加载设置失败';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (selectedProviderId === 'custom') {
      setShowCustomUrl(true);
    } else if (selectedProvider) {
      setShowCustomUrl(false);
      if (availableModels.length > 0 && !availableModels.find(m => m.id === selectedModelId)) {
        setSelectedModelId(availableModels[0].id);
      }
    }
  }, [selectedProviderId]);

  const getApiBase = () => {
    if (selectedProviderId === 'custom') return customBaseUrl;
    return selectedProvider?.api_base || '';
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const baseUrl = getApiBase();
      if (!baseUrl && selectedProviderId !== '') {
        setError('请选择或填写 API Base URL');
        return;
      }
      if (!selectedModelId && selectedProviderId !== 'custom') {
        setError('请选择模型');
        return;
      }

      await Promise.all([
        updateSetting('llm_api_key', apiKey),
        updateSetting('llm_api_base', baseUrl),
        updateSetting('llm_model', selectedModelId),
        updateSetting('tavily_api_key', tavilyKey),
        updateSetting('github_token', githubToken),
      ]);

      await fetchData();
      setSuccess('设置已保存成功');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '保存失败';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    if (!apiKey.trim()) {
      setError('请先输入 API Key');
      return;
    }

    try {
      setTesting(true);
      setError(null);
      setSuccess(null);

      const baseUrl = getApiBase();
      await Promise.all([
        updateSetting('llm_api_key', apiKey),
        updateSetting('llm_api_base', baseUrl),
        updateSetting('llm_model', selectedModelId),
      ]);

      const result = await testLLMConnection();

      if (result.success) {
        setSuccess(result.message);
        const config = await getLLMConfig();
        setLLMConfig(config);
      } else {
        setError(result.message);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : '测试失败';
      setError(msg);
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
          <p className="text-slate-400 text-sm">正在加载设置...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/15">
            <SettingsIcon className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-bold text-white">系统设置</h1>
            <p className="text-sm text-slate-400">配置 LLM API 和其他系统参数</p>
          </div>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
            text-slate-400 hover:text-white hover:bg-slate-700/50
            transition-colors text-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>刷新</span>
        </button>
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-800 p-4">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${llmConfig?.enabled ? 'bg-emerald-500/15' : 'bg-amber-500/15'}`}>
            <Bot className={`w-5 h-5 ${llmConfig?.enabled ? 'text-emerald-400' : 'text-amber-400'}`} />
          </div>
          <div className="flex-1">
            <h3 className="text-sm font-medium text-slate-200">LLM 服务状态</h3>
            <p className="text-xs text-slate-400">
              {llmConfig?.enabled
                ? `已启用 - ${llmConfig.model} @ ${llmConfig.api_base}`
                : '未启用 - 配置 API Key 后可启用大模型分析功能'}
            </p>
          </div>
          <div className={`px-2.5 py-1 rounded-full text-xs font-medium ${
            llmConfig?.enabled
              ? 'bg-emerald-500/15 text-emerald-400'
              : 'bg-amber-500/15 text-amber-400'
          }`}>
            {llmConfig?.enabled ? '运行中' : '未配置'}
          </div>
        </div>
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

      {/* LLM Provider Selection */}
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 space-y-6">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-cyan-400" />
          LLM 模型配置
        </h2>

        <div className="space-y-6">
          {/* Provider Selector */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-slate-400" />
              <label className="text-sm font-medium text-slate-200">模型服务商</label>
            </div>
            <p className="text-xs text-slate-500">选择 LLM 服务商，系统将自动填充 API 地址</p>
            <div className="relative">
              <select
                value={selectedProviderId}
                onChange={(e) => setSelectedProviderId(e.target.value)}
                className="w-full px-3 py-2.5 rounded-lg bg-slate-700/50 border border-slate-600
                  text-sm text-slate-200
                  focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30
                  transition-all appearance-none cursor-pointer"
              >
                <option value="">请选择服务商...</option>
                {providers.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} {p.api_base ? `(${p.api_base})` : ''}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
            </div>
            {selectedProvider && (
              <p className="text-xs text-slate-500">{selectedProvider.description}</p>
            )}
          </div>

          {/* Model Selector */}
          {selectedProviderId && selectedProviderId !== 'custom' && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-slate-400" />
                <label className="text-sm font-medium text-slate-200">模型</label>
              </div>
              <p className="text-xs text-slate-500">选择具体模型</p>
              <div className="relative">
                <select
                  value={selectedModelId}
                  onChange={(e) => setSelectedModelId(e.target.value)}
                  className="w-full px-3 py-2.5 rounded-lg bg-slate-700/50 border border-slate-600
                    text-sm text-slate-200
                    focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30
                    transition-all appearance-none cursor-pointer"
                >
                  <option value="">请选择模型...</option>
                  {availableModels.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name} - {m.description}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
              </div>
            </div>
          )}

          {/* Custom URL (for custom provider) */}
          {showCustomUrl && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Globe className="w-4 h-4 text-slate-400" />
                <label className="text-sm font-medium text-slate-200">自定义 API Base URL</label>
              </div>
              <p className="text-xs text-slate-500">输入自定义 OpenAI 兼容 API 地址</p>
              <input
                type="text"
                value={customBaseUrl}
                onChange={(e) => setCustomBaseUrl(e.target.value)}
                placeholder="https://your-api.com/v1"
                className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
                  text-sm text-slate-200 placeholder-slate-500
                  focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30
                  transition-all"
              />
            </div>
          )}

          {/* Custom Model (for custom provider) */}
          {selectedProviderId === 'custom' && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-slate-400" />
                <label className="text-sm font-medium text-slate-200">自定义模型名称</label>
              </div>
              <input
                type="text"
                value={selectedModelId}
                onChange={(e) => setSelectedModelId(e.target.value)}
                placeholder="例如: gpt-4, deepseek-chat"
                className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
                  text-sm text-slate-200 placeholder-slate-500
                  focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30
                  transition-all"
              />
            </div>
          )}

          {/* API Key */}
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-slate-400" />
              <label className="text-sm font-medium text-slate-200">API Key</label>
            </div>
            <p className="text-xs text-slate-500">对应服务商的 API 密钥</p>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="sk-... 或对应服务商的 API Key"
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
                text-sm text-slate-200 placeholder-slate-500
                focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30
                transition-all"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 pt-4 border-t border-slate-700">
          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg
              bg-cyan-500/15 text-cyan-400 border border-cyan-500/30
              hover:bg-cyan-500/25 transition-colors disabled:opacity-50"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            <span>{saving ? '保存中...' : '保存设置'}</span>
          </button>
          <button
            onClick={handleTest}
            disabled={testing || !apiKey.trim()}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg
              bg-slate-700/50 text-slate-300 border border-slate-600
              hover:bg-slate-700 transition-colors disabled:opacity-50"
          >
            {testing ? <Loader2 className="w-4 h-4 animate-spin" /> : <TestTube className="w-4 h-4" />}
            <span>{testing ? '测试中...' : '测试连接'}</span>
          </button>
        </div>
      </div>

      {/* Data Source API Keys */}
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 space-y-6">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Radio className="w-5 h-5 text-cyan-400" />
          数据源 API 配置
        </h2>
        <div className="space-y-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-slate-400" />
              <label className="text-sm font-medium text-slate-200">Tavily API Key</label>
            </div>
            <p className="text-xs text-slate-500">用于 Web 搜索采集威胁情报。免费注册: https://tavily.com (1000次/月)</p>
            <input
              type="password"
              value={tavilyKey}
              onChange={(e) => setTavilyKey(e.target.value)}
              placeholder="tvly-..."
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
                text-sm text-slate-200 placeholder-slate-500
                focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30
                transition-all"
            />
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Key className="w-4 h-4 text-slate-400" />
              <label className="text-sm font-medium text-slate-200">GitHub Token</label>
            </div>
            <p className="text-xs text-slate-500">用于提升 GitHub 安全公告 API 速率限制（可选）</p>
            <input
              type="password"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              placeholder="ghp_..."
              className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
                text-sm text-slate-200 placeholder-slate-500
                focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30
                transition-all"
            />
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
        <h3 className="text-sm font-medium text-slate-300 mb-2">配置说明</h3>
        <ul className="text-xs text-slate-400 space-y-1.5 list-disc list-inside">
          <li>选择服务商后，API Base URL 会自动填充，无需手动填写</li>
          <li>选择模型后，模型名称会自动填充</li>
          <li>只需填写对应服务商的 API Key 即可使用</li>
          <li>支持 OpenAI、DeepSeek、智谱 GLM、Kimi、通义千问、豆包、SiliconFlow 等</li>
          <li>如果不配置 API Key，系统将使用内置的规则引擎进行分析</li>
        </ul>
      </div>
    </div>
  );
}
