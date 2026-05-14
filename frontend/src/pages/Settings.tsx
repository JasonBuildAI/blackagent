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
} from 'lucide-react';
import { getSettings, getLLMConfig, updateSetting, testLLMConnection } from '../api';
import type { SettingsResponse, LLMConfig } from '../types';

interface SettingFieldProps {
  icon: React.ElementType;
  label: string;
  description: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: string;
  disabled?: boolean;
  isLoading?: boolean;
}

function SettingField({
  icon: Icon,
  label,
  description,
  value,
  onChange,
  placeholder,
  type = 'text',
  disabled,
  isLoading,
}: SettingFieldProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Icon className="w-4 h-4 text-slate-400" />
        <label className="text-sm font-medium text-slate-200">{label}</label>
      </div>
      <p className="text-xs text-slate-500">{description}</p>
      <div className="relative">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          className="w-full px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
            text-sm text-slate-200 placeholder-slate-500
            focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30
            transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        />
        {isLoading && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 animate-spin" />
        )}
      </div>
    </div>
  );
}

export default function Settings() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [llmConfig, setLLMConfig] = useState<LLMConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form values
  const [apiKey, setApiKey] = useState('');
  const [apiBase, setApiBase] = useState('');
  const [model, setModel] = useState('');

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [settingsData, llmData] = await Promise.all([
        getSettings(),
        getLLMConfig(),
      ]);

      setSettings(settingsData);
      setLLMConfig(llmData);

      // Initialize form values
      if (settingsData.settings) {
        setApiKey(settingsData.settings.llm_api_key?.value || '');
        setApiBase(settingsData.settings.llm_api_base?.value || 'https://api.openai.com/v1');
        setModel(settingsData.settings.llm_model?.value || 'gpt-4o-mini');
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

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      // Save all settings
      await Promise.all([
        updateSetting('llm_api_key', apiKey),
        updateSetting('llm_api_base', apiBase),
        updateSetting('llm_model', model),
      ]);

      // Refresh data
      await fetchData();
      setSuccess('设置已保存成功');

      // Clear success message after 3 seconds
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

      // First save the settings
      await Promise.all([
        updateSetting('llm_api_key', apiKey),
        updateSetting('llm_api_base', apiBase),
        updateSetting('llm_model', model),
      ]);

      // Then test the connection
      const result = await testLLMConnection();

      if (result.success) {
        setSuccess(result.message);
        // Refresh LLM config
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
      {/* Header */}
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

      {/* Status Card */}
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

      {/* Alert Messages */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-400 hover:text-red-300"
          >
            ✕
          </button>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm">
          <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
          <span>{success}</span>
          <button
            onClick={() => setSuccess(null)}
            className="ml-auto text-emerald-400 hover:text-emerald-300"
          >
            ✕
          </button>
        </div>
      )}

      {/* Settings Form */}
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-6 space-y-6">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          <Key className="w-5 h-5 text-cyan-400" />
          LLM 配置
        </h2>

        <div className="space-y-6">
          <SettingField
            icon={Key}
            label="API Key"
            description="你的 OpenAI 兼容 API 密钥。支持 OpenAI、Azure、DeepSeek 等。"
            value={apiKey}
            onChange={setApiKey}
            placeholder="sk-..."
            type="password"
            isLoading={loading}
          />

          <SettingField
            icon={Globe}
            label="API Base URL"
            description="API 基础地址。默认使用 OpenAI 官方 API。"
            value={apiBase}
            onChange={setApiBase}
            placeholder="https://api.openai.com/v1"
            isLoading={loading}
          />

          <SettingField
            icon={Bot}
            label="模型名称"
            description="要使用的模型名称。例如：gpt-4o-mini、gpt-4o、deepseek-chat"
            value={model}
            onChange={setModel}
            placeholder="gpt-4o-mini"
            isLoading={loading}
          />
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
            {saving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            <span>{saving ? '保存中...' : '保存设置'}</span>
          </button>

          <button
            onClick={handleTest}
            disabled={testing || !apiKey.trim()}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg
              bg-slate-700/50 text-slate-300 border border-slate-600
              hover:bg-slate-700 transition-colors disabled:opacity-50"
          >
            {testing ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <TestTube className="w-4 h-4" />
            )}
            <span>{testing ? '测试中...' : '测试连接'}</span>
          </button>
        </div>
      </div>

      {/* Help Card */}
      <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
        <h3 className="text-sm font-medium text-slate-300 mb-2">配置说明</h3>
        <ul className="text-xs text-slate-400 space-y-1.5 list-disc list-inside">
          <li>API Key 是访问大模型服务的凭证，请妥善保管</li>
          <li>支持 OpenAI、Azure OpenAI、DeepSeek、Moonshot 等兼容 OpenAI API 格式的服务</li>
          <li>如果不配置 API Key，系统将使用内置的规则引擎进行分析</li>
          <li>配置更改后，新的分析请求会使用新的配置</li>
          <li>可以使用 "测试连接" 按钮验证配置是否正确</li>
        </ul>
      </div>
    </div>
  );
}
