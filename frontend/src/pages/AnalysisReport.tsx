import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Loader2,
  AlertCircle,
  Shield,
  Crosshair,
  Bug,
  Wrench,
  Lightbulb,
  ExternalLink,
  FileText,
  AlertTriangle,
} from 'lucide-react';
import { getAnalysisReport } from '../api';
import type { AnalysisReport as AnalysisReportType } from '../types';

function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function getRiskScoreConfig(score: number) {
  if (score >= 75) {
    return {
      color: 'text-red-400',
      bg: 'bg-red-500',
      trackBg: 'bg-red-500/20',
      border: 'border-red-500/30',
      label: '严重风险',
      icon: AlertTriangle,
    };
  }
  if (score >= 50) {
    return {
      color: 'text-orange-400',
      bg: 'bg-orange-500',
      trackBg: 'bg-orange-500/20',
      border: 'border-orange-500/30',
      label: '高风险',
      icon: AlertTriangle,
    };
  }
  if (score >= 25) {
    return {
      color: 'text-yellow-400',
      bg: 'bg-yellow-500',
      trackBg: 'bg-yellow-500/20',
      border: 'border-yellow-500/30',
      label: '中等风险',
      icon: Shield,
    };
  }
  return {
    color: 'text-emerald-400',
    bg: 'bg-emerald-500',
    trackBg: 'bg-emerald-500/20',
    border: 'border-emerald-500/30',
    label: '低风险',
    icon: Shield,
  };
}

function renderMarkdownLike(text: string | null): string {
  if (!text) return '';
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong class="text-white">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em class="text-slate-300">$1</em>')
    .replace(/`(.+?)`/g, '<code class="bg-slate-700 px-1 py-0.5 rounded text-cyan-400 text-xs font-mono">$1</code>');
}

export default function AnalysisReportPage() {
  const { intelligenceId } = useParams<{ intelligenceId: string }>();
  const navigate = useNavigate();

  const [report, setReport] = useState<AnalysisReportType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchReport = useCallback(async () => {
    if (!intelligenceId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getAnalysisReport(intelligenceId);
      setReport(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '获取分析报告失败';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [intelligenceId]);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
          <p className="text-slate-400 text-sm">正在加载分析报告...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !report) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4 text-center max-w-md">
          <div className="p-4 rounded-full bg-red-500/10">
            <AlertCircle className="w-12 h-12 text-red-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">
              {error ? '加载失败' : '报告不存在'}
            </h3>
            <p className="text-sm text-slate-400">
              {error || '该情报尚未生成分析报告，请先执行分析'}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/intelligence')}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg
                bg-slate-700/50 text-slate-300 border border-slate-600
                hover:bg-slate-700 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>返回列表</span>
            </button>
            {!error && intelligenceId && (
              <button
                onClick={() => navigate(`/intelligence/${intelligenceId}`)}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-lg
                  bg-cyan-500/15 text-cyan-400 border border-cyan-500/30
                  hover:bg-cyan-500/25 transition-colors"
              >
                <span>查看情报</span>
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  const scoreConfig = getRiskScoreConfig(report.risk_score);

  return (
    <div className="space-y-4 md:space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(`/intelligence/${report.intelligence_id}`)}
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white
            transition-colors text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>返回情报详情</span>
        </button>
        <span className="text-xs text-slate-500">
          生成时间: {formatDate(report.created_at)}
        </span>
      </div>

      <h1 className="text-xl md:text-2xl font-bold text-white">
        分析报告 #{report.id}
      </h1>

      {/* Risk Score Card */}
      <div className={`
        rounded-xl border p-4 md:p-6
        bg-slate-800 ${scoreConfig.border}
      `}>
        <div className="flex items-center gap-3 mb-4">
          <div className={`p-2 rounded-lg ${scoreConfig.trackBg}`}>
            <scoreConfig.icon className={`w-6 h-6 ${scoreConfig.color}`} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">风险评分</h2>
            <p className={`text-sm ${scoreConfig.color} font-medium`}>
              {scoreConfig.label}
            </p>
          </div>
        </div>

        {/* Score progress bar */}
        <div className="relative pt-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500">0</span>
            <span className="text-xs text-slate-500">100</span>
          </div>
          <div className={`h-3 rounded-full ${scoreConfig.trackBg} overflow-hidden`}>
            <div
              className={`h-full rounded-full ${scoreConfig.bg} transition-all duration-1000 ease-out`}
              style={{ width: `${Math.min(100, Math.max(0, report.risk_score))}%` }}
            />
          </div>
          <div className="flex justify-center mt-2">
            <span className={`text-3xl font-bold ${scoreConfig.color}`}>
              {report.risk_score}
            </span>
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-[10px] text-slate-600">低风险</span>
            <span className="text-[10px] text-slate-600">中风险</span>
            <span className="text-[10px] text-slate-600">高风险</span>
            <span className="text-[10px] text-slate-600">严重风险</span>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-4 md:p-6">
        <div className="flex items-center gap-2 mb-3">
          <FileText className="w-4 h-4 text-cyan-400" />
          <h3 className="text-base font-semibold text-white">分析摘要</h3>
        </div>
        <p className="text-sm text-slate-300 leading-relaxed">{report.summary}</p>
      </div>

      {/* Cheat Scenario */}
      {report.cheat_scenario && (
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-4 md:p-6">
          <div className="flex items-center gap-2 mb-3">
            <Crosshair className="w-4 h-4 text-orange-400" />
            <h3 className="text-base font-semibold text-white">作弊场景</h3>
          </div>
          <div
            className="text-sm text-slate-300 leading-relaxed space-y-2"
            dangerouslySetInnerHTML={{ __html: renderMarkdownLike(report.cheat_scenario) }}
          />
        </div>
      )}

      {/* Malicious Pattern */}
      {report.malicious_pattern && (
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-4 md:p-6">
          <div className="flex items-center gap-2 mb-3">
            <Bug className="w-4 h-4 text-red-400" />
            <h3 className="text-base font-semibold text-white">恶意模式</h3>
          </div>
          <div
            className="text-sm text-slate-300 leading-relaxed space-y-2"
            dangerouslySetInnerHTML={{ __html: renderMarkdownLike(report.malicious_pattern) }}
          />
        </div>
      )}

      {/* Tech Chain */}
      {report.tech_chain && (
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-4 md:p-6">
          <div className="flex items-center gap-2 mb-3">
            <Wrench className="w-4 h-4 text-purple-400" />
            <h3 className="text-base font-semibold text-white">技术链条</h3>
          </div>
          <div
            className="text-sm text-slate-300 leading-relaxed space-y-2"
            dangerouslySetInnerHTML={{ __html: renderMarkdownLike(report.tech_chain) }}
          />
        </div>
      )}

      {/* Recommendations */}
      {report.recommendations && (
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-4 md:p-6">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="w-4 h-4 text-yellow-400" />
            <h3 className="text-base font-semibold text-white">建议措施</h3>
          </div>
          <div
            className="text-sm text-slate-300 leading-relaxed space-y-2"
            dangerouslySetInnerHTML={{ __html: renderMarkdownLike(report.recommendations) }}
          />
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-end gap-3 pt-2">
        <button
          onClick={() => navigate(`/intelligence/${report.intelligence_id}`)}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm
            bg-slate-700/50 text-slate-300 border border-slate-600
            hover:bg-slate-700 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>查看情报原文</span>
        </button>
      </div>
    </div>
  );
}