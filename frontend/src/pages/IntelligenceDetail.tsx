import { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Loader2,
  AlertCircle,
  Zap,
  FileText,
  Calendar,
  Globe,
  Hash,
  Shield,
  Tag,
  Clock,
  CheckCircle2,
  XCircle,
  ExternalLink,
} from 'lucide-react';
import { getIntelligenceDetail, analyzeIntelligence } from '../api';
import type { IntelligenceItem, Entity } from '../types';
import RiskBadge from '../components/RiskBadge';
import EntityTag from '../components/EntityTag';

function formatFullDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

export default function IntelligenceDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [item, setItem] = useState<IntelligenceItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [viewMode, setViewMode] = useState<'cleaned' | 'raw'>('cleaned');

  const fetchDetail = useCallback(async () => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getIntelligenceDetail(id);
      setItem(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '获取情报详情失败';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchDetail();
  }, [fetchDetail]);

  const handleAnalyze = async () => {
    if (!item) return;
    try {
      setAnalyzing(true);
      await analyzeIntelligence(item.id);
      navigate(`/analysis/${item.id}`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '分析失败';
      alert(msg);
    } finally {
      setAnalyzing(false);
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
          <p className="text-slate-400 text-sm">正在加载情报详情...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !item) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4 text-center max-w-md">
          <div className="p-4 rounded-full bg-red-500/10">
            <AlertCircle className="w-12 h-12 text-red-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">
              {error ? '加载失败' : '情报不存在'}
            </h3>
            <p className="text-sm text-slate-400">{error || '未找到该情报记录'}</p>
          </div>
          <button
            onClick={() => navigate('/intelligence')}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg
              bg-slate-700/50 text-slate-300 border border-slate-600
              hover:bg-slate-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>返回列表</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6 max-w-5xl">
      {/* Back + Actions */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/intelligence')}
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white
            transition-colors text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>返回列表</span>
        </button>

        <div className="flex items-center gap-2">
          {item.status === 'analyzed' ? (
            <button
              onClick={() => navigate(`/analysis/${item.id}`)}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm
                bg-cyan-500/15 text-cyan-400 border border-cyan-500/30
                hover:bg-cyan-500/25 transition-colors"
            >
              <ExternalLink className="w-4 h-4" />
              <span>查看分析报告</span>
            </button>
          ) : (
            <button
              onClick={handleAnalyze}
              disabled={analyzing || item.status === 'processing'}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm
                bg-amber-500/15 text-amber-400 border border-amber-500/30
                hover:bg-amber-500/25 transition-colors disabled:opacity-50"
            >
              {analyzing ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Zap className="w-4 h-4" />
              )}
              <span>{analyzing ? '分析中...' : item.status === 'processing' ? '分析中' : '执行分析'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Title */}
      <h1 className="text-xl md:text-2xl font-bold text-white">
        情报详情 #{item.id}
      </h1>

      {/* Metadata Card */}
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-4 md:p-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
              <Globe className="w-3.5 h-3.5" />
              <span>来源类型</span>
            </div>
            <p className="text-sm text-slate-200 font-medium">{item.source_type}</p>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
              <Hash className="w-3.5 h-3.5" />
              <span>来源名称</span>
            </div>
            <p className="text-sm text-slate-200 font-medium">{item.source_name}</p>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
              <Shield className="w-3.5 h-3.5" />
              <span>风险等级</span>
            </div>
            <RiskBadge level={item.risk_level} size="md" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
              <Tag className="w-3.5 h-3.5" />
              <span>风险分类</span>
            </div>
            <p className="text-sm text-slate-200">
              {item.risk_category || <span className="text-slate-500">未分类</span>}
            </p>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
              <Clock className="w-3.5 h-3.5" />
              <span>状态</span>
            </div>
            <span
              className={`
                inline-flex items-center gap-1 text-sm font-medium
                ${item.status === 'analyzed'
                  ? 'text-emerald-400'
                  : item.status === 'processing'
                  ? 'text-blue-400'
                  : 'text-slate-400'
                }
              `}
            >
              {item.status === 'analyzed' ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : item.status === 'processing' ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Clock className="w-4 h-4" />
              )}
              {item.status === 'analyzed' ? '已分析' : item.status === 'processing' ? '分析中' : '待处理'}
            </span>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>收录时间</span>
            </div>
            <p className="text-sm text-slate-400">{formatFullDate(item.ingested_at)}</p>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>发布时间</span>
            </div>
            <p className="text-sm text-slate-400">{formatFullDate(item.published_at)}</p>
          </div>
          <div>
            <div className="flex items-center gap-1.5 text-slate-500 text-xs mb-1">
              <XCircle className="w-3.5 h-3.5" />
              <span>是否重复</span>
            </div>
            <p className="text-sm">
              {item.is_duplicate ? (
                <span className="text-yellow-400">是</span>
              ) : (
                <span className="text-slate-400">否</span>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="rounded-xl border border-slate-700 bg-slate-800 overflow-hidden">
        <div className="flex items-center border-b border-slate-700">
          <button
            onClick={() => setViewMode('cleaned')}
            className={`
              flex-1 px-4 py-3 text-sm font-medium transition-colors
              ${viewMode === 'cleaned'
                ? 'text-cyan-400 border-b-2 border-cyan-500 bg-slate-700/20'
                : 'text-slate-400 hover:text-slate-200'
              }
            `}
          >
            清洗后内容
          </button>
          <button
            onClick={() => setViewMode('raw')}
            className={`
              flex-1 px-4 py-3 text-sm font-medium transition-colors
              ${viewMode === 'raw'
                ? 'text-cyan-400 border-b-2 border-cyan-500 bg-slate-700/20'
                : 'text-slate-400 hover:text-slate-200'
              }
            `}
          >
            原始内容
          </button>
        </div>
        <div className="p-4 md:p-6">
          {viewMode === 'cleaned' ? (
            item.cleaned_content ? (
              <pre className="text-sm text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">
                {item.cleaned_content}
              </pre>
            ) : (
              <div className="flex items-center justify-center py-8 text-slate-500 text-sm">
                暂无清洗后内容
              </div>
            )
          ) : (
            <pre className="text-sm text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">
              {item.raw_content}
            </pre>
          )}
        </div>
      </div>

      {/* Entities section */}
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-4 md:p-6">
        <div className="flex items-center gap-2 mb-3">
          <FileText className="w-4 h-4 text-slate-400" />
          <h3 className="text-sm font-semibold text-white">关联实体</h3>
          {item.entities && item.entities.length > 0 && (
            <span className="text-xs text-slate-500 ml-1">({item.entities.length})</span>
          )}
        </div>
        {item.entities && item.entities.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {item.entities.map((entity) => (
              <EntityTag
                key={entity.id}
                entityType={entity.entity_type}
                value={entity.entity_value}
                confidence={entity.confidence}
              />
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500">
            {item.status === 'analyzed'
              ? '分析完成但未提取到实体信息。'
              : '实体数据将在分析完成后在此展示。请点击"执行分析"按钮对情报进行分析。'}
          </p>
        )}
      </div>
    </div>
  );
}