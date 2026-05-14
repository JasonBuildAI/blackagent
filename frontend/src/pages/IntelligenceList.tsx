import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  Inbox,
  Trash2,
  Zap,
  CheckSquare,
  Square,
  RefreshCw,
} from 'lucide-react';
import { getIntelligenceList, analyzeIntelligence, batchAnalyze, deleteIntelligence } from '../api';
import type { IntelligenceItem } from '../types';
import RiskBadge from '../components/RiskBadge';

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function truncateText(text: string, maxLen: number = 60): string {
  if (text.length <= maxLen) return text;
  return text.slice(0, maxLen) + '...';
}

const PAGE_SIZE = 20;

export default function IntelligenceList() {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [items, setItems] = useState<IntelligenceItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [sourceType, setSourceType] = useState(searchParams.get('source_type') || '');
  const [riskLevel, setRiskLevel] = useState(searchParams.get('risk_level') || '');
  const [status, setStatus] = useState(searchParams.get('status') || '');
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);

  // Selection
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [batchLoading, setBatchLoading] = useState(false);

  // Action loading per row
  const [analyzingIds, setAnalyzingIds] = useState<Set<string>>(new Set());
  const [deletingIds, setDeletingIds] = useState<Set<string>>(new Set());

  const fetchList = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const params: Record<string, string | number> = {
        page,
        page_size: PAGE_SIZE,
      };
      if (sourceType) params.source_type = sourceType;
      if (riskLevel) params.risk_level = riskLevel;
      if (status) params.status = status;
      if (search) params.search = search;

      const data = await getIntelligenceList(params);
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '获取数据失败';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [page, sourceType, riskLevel, status, search]);

  useEffect(() => {
    fetchList();
  }, [fetchList]);

  // Update URL params
  useEffect(() => {
    const params: Record<string, string> = {};
    if (sourceType) params.source_type = sourceType;
    if (riskLevel) params.risk_level = riskLevel;
    if (status) params.status = status;
    if (search) params.search = search;
    if (page > 1) params.page = String(page);
    setSearchParams(params, { replace: true });
  }, [sourceType, riskLevel, status, search, page, setSearchParams]);

  const totalPages = Math.ceil(total / PAGE_SIZE);

  const handleFilterChange = () => {
    setPage(1);
    setSelectedIds(new Set());
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === items.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(items.map((i) => i.id)));
    }
  };

  const toggleSelect = (id: string) => {
    const next = new Set(selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedIds(next);
  };

  const handleAnalyze = async (id: string) => {
    try {
      setAnalyzingIds((prev) => new Set(prev).add(id));
      await analyzeIntelligence(id);
      await fetchList();
    } catch (err) {
      const msg = err instanceof Error ? err.message : '分析失败';
      alert(msg);
    } finally {
      setAnalyzingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const handleBatchAnalyze = async () => {
    if (selectedIds.size === 0) return;
    try {
      setBatchLoading(true);
      await batchAnalyze(Array.from(selectedIds));
      setSelectedIds(new Set());
      await fetchList();
    } catch (err) {
      const msg = err instanceof Error ? err.message : '批量分析失败';
      alert(msg);
    } finally {
      setBatchLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除该情报吗？此操作不可撤销。')) return;
    try {
      setDeletingIds((prev) => new Set(prev).add(id));
      await deleteIntelligence(id);
      await fetchList();
    } catch (err) {
      const msg = err instanceof Error ? err.message : '删除失败';
      alert(msg);
    } finally {
      setDeletingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    }
  };

  const sourceTypes = ['im', 'group', 'public_account', 'forum'];

  // Loading state
  if (loading && items.length === 0) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
          <p className="text-slate-400 text-sm">正在加载情报列表...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 md:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h1 className="text-xl md:text-2xl font-bold text-white">情报列表</h1>
        <div className="flex items-center gap-2">
          {selectedIds.size > 0 && (
            <button
              onClick={handleBatchAnalyze}
              disabled={batchLoading}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs
                bg-cyan-500/15 text-cyan-400 border border-cyan-500/30
                hover:bg-cyan-500/25 transition-colors disabled:opacity-50"
            >
              {batchLoading ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Zap className="w-3.5 h-3.5" />
              )}
              <span>批量分析 ({selectedIds.size})</span>
            </button>
          )}
          <button
            onClick={fetchList}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs
              text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>刷新</span>
          </button>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
          <button onClick={fetchList} className="ml-auto text-red-400 hover:text-red-300 underline text-xs">
            重试
          </button>
        </div>
      )}

      {/* Filter bar */}
      <div className="rounded-xl border border-slate-700 bg-slate-800 p-3 md:p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 flex flex-col sm:flex-row gap-2">
            {/* Source type filter */}
            <select
              value={sourceType}
              onChange={(e) => {
                setSourceType(e.target.value);
                handleFilterChange();
              }}
              className="px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
                text-sm text-slate-300 focus:outline-none focus:border-cyan-500/50
                transition-colors appearance-none cursor-pointer"
            >
              <option value="">所有来源类型</option>
              {sourceTypes.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>

            {/* Risk level filter */}
            <select
              value={riskLevel}
              onChange={(e) => {
                setRiskLevel(e.target.value);
                handleFilterChange();
              }}
              className="px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
                text-sm text-slate-300 focus:outline-none focus:border-cyan-500/50
                transition-colors appearance-none cursor-pointer"
            >
              <option value="">所有风险等级</option>
              <option value="critical">严重</option>
              <option value="high">高危</option>
              <option value="medium">中危</option>
              <option value="low">低危</option>
            </select>

            {/* Status filter */}
            <select
              value={status}
              onChange={(e) => {
                setStatus(e.target.value);
                handleFilterChange();
              }}
              className="px-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
                text-sm text-slate-300 focus:outline-none focus:border-cyan-500/50
                transition-colors appearance-none cursor-pointer"
            >
              <option value="">所有状态</option>
              <option value="pending">待处理</option>
              <option value="processing">分析中</option>
              <option value="analyzed">已分析</option>
            </select>
          </div>

          {/* Search */}
          <div className="relative flex-shrink-0 sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleFilterChange();
                }
              }}
              placeholder="搜索关键词..."
              className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-700/50 border border-slate-600
                text-sm text-slate-300 placeholder-slate-500
                focus:outline-none focus:border-cyan-500/50 transition-colors"
            />
          </div>
        </div>
      </div>

      {/* Table or Empty */}
      {items.length === 0 ? (
        <div className="flex items-center justify-center h-64">
          <div className="flex flex-col items-center gap-3 text-center">
            <div className="p-3 rounded-full bg-slate-700/50">
              <Inbox className="w-10 h-10 text-slate-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-300">暂无情报数据</p>
              <p className="text-xs text-slate-500 mt-0.5">
                {(sourceType || riskLevel || status || search)
                  ? '没有匹配当前筛选条件的结果，请调整筛选条件'
                  : '系统尚未录入任何情报信息'}
              </p>
            </div>
            {(sourceType || riskLevel || status || search) && (
              <button
                onClick={() => {
                  setSourceType('');
                  setRiskLevel('');
                  setStatus('');
                  setSearch('');
                  setPage(1);
                }}
                className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                清除筛选条件
              </button>
            )}
          </div>
        </div>
      ) : (
        <>
          {/* Table */}
          <div className="rounded-xl border border-slate-700 bg-slate-800 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700/50">
                    <th className="w-10 px-2 py-3">
                      <button
                        onClick={toggleSelectAll}
                        className="p-0.5 rounded hover:bg-slate-700/50 transition-colors"
                      >
                        {selectedIds.size === items.length && items.length > 0 ? (
                          <CheckSquare className="w-4 h-4 text-cyan-400" />
                        ) : (
                          <Square className="w-4 h-4 text-slate-500" />
                        )}
                      </button>
                    </th>
                    <th className="text-left px-3 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                      来源类型
                    </th>
                    <th className="text-left px-3 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                      来源名称
                    </th>
                    <th className="text-left px-3 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                      内容预览
                    </th>
                    <th className="text-left px-3 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                      风险等级
                    </th>
                    <th className="text-left px-3 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                      状态
                    </th>
                    <th className="text-left px-3 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                      时间
                    </th>
                    <th className="text-left px-3 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/30">
                  {items.map((item) => (
                    <tr
                      key={item.id}
                      className="hover:bg-slate-700/20 transition-colors group"
                    >
                      <td className="px-2 py-3">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleSelect(item.id);
                          }}
                          className="p-0.5 rounded hover:bg-slate-700/50 transition-colors"
                        >
                          {selectedIds.has(item.id) ? (
                            <CheckSquare className="w-4 h-4 text-cyan-400" />
                          ) : (
                            <Square className="w-4 h-4 text-slate-600 group-hover:text-slate-400" />
                          )}
                        </button>
                      </td>
                      <td
                        className="px-3 py-3 cursor-pointer"
                        onClick={() => navigate(`/intelligence/${item.id}`)}
                      >
                        <span className="text-slate-300 text-xs">{item.source_type}</span>
                      </td>
                      <td
                        className="px-3 py-3 cursor-pointer"
                        onClick={() => navigate(`/intelligence/${item.id}`)}
                      >
                        <span className="text-slate-400 text-xs">{item.source_name}</span>
                      </td>
                      <td
                        className="px-3 py-3 max-w-xs cursor-pointer"
                        onClick={() => navigate(`/intelligence/${item.id}`)}
                      >
                        <span className="text-slate-400 text-xs line-clamp-2">
                          {truncateText(item.cleaned_content || item.raw_content)}
                        </span>
                      </td>
                      <td
                        className="px-3 py-3 cursor-pointer"
                        onClick={() => navigate(`/intelligence/${item.id}`)}
                      >
                        <RiskBadge level={item.risk_level} size="sm" />
                      </td>
                      <td
                        className="px-3 py-3 cursor-pointer"
                        onClick={() => navigate(`/intelligence/${item.id}`)}
                      >
                        <span
                          className={`
                            inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium
                            ${item.status === 'analyzed'
                              ? 'bg-emerald-500/15 text-emerald-400'
                              : item.status === 'processing'
                              ? 'bg-blue-500/15 text-blue-400'
                              : 'bg-slate-500/15 text-slate-400'
                            }
                          `}
                        >
                          {item.status === 'analyzed'
                            ? '已分析'
                            : item.status === 'processing'
                            ? '分析中'
                            : '待处理'}
                        </span>
                      </td>
                      <td
                        className="px-3 py-3 cursor-pointer"
                        onClick={() => navigate(`/intelligence/${item.id}`)}
                      >
                        <span className="text-slate-500 text-xs whitespace-nowrap">
                          {formatDate(item.ingested_at)}
                        </span>
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex items-center gap-1.5">
                          {item.status === 'analyzed' ? (
                            <button
                              onClick={() => navigate(`/analysis/${item.id}`)}
                              className="inline-flex items-center gap-1 px-2 py-1 rounded text-[10px]
                                bg-cyan-500/15 text-cyan-400 border border-cyan-500/30
                                hover:bg-cyan-500/25 transition-colors"
                            >
                              查看报告
                            </button>
                          ) : (
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleAnalyze(item.id);
                              }}
                              disabled={analyzingIds.has(item.id) || item.status === 'processing'}
                              className="inline-flex items-center gap-1 px-2 py-1 rounded text-[10px]
                                bg-amber-500/15 text-amber-400 border border-amber-500/30
                                hover:bg-amber-500/25 transition-colors disabled:opacity-50"
                            >
                              {analyzingIds.has(item.id) ? (
                                <Loader2 className="w-3 h-3 animate-spin" />
                              ) : (
                                <Zap className="w-3 h-3" />
                              )}
                              <span>分析</span>
                            </button>
                          )}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDelete(item.id);
                            }}
                            disabled={deletingIds.has(item.id)}
                            className="inline-flex items-center gap-1 px-2 py-1 rounded text-[10px]
                              text-slate-500 hover:text-red-400 hover:bg-red-500/10
                              transition-colors disabled:opacity-50"
                          >
                            {deletingIds.has(item.id) ? (
                              <Loader2 className="w-3 h-3 animate-spin" />
                            ) : (
                              <Trash2 className="w-3 h-3" />
                            )}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-500 text-xs">
              共 {total} 条记录，第 {page}/{totalPages || 1} 页
            </span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page <= 1}
                className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/50
                  transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter((p) => {
                  if (totalPages <= 7) return true;
                  if (p === 1 || p === totalPages) return true;
                  if (Math.abs(p - page) <= 1) return true;
                  return false;
                })
                .reduce<(number | 'ellipsis')[]>((acc, p, idx, arr) => {
                  if (idx > 0) {
                    const prev = arr[idx - 1];
                    if (p - prev > 1) {
                      acc.push('ellipsis');
                    }
                  }
                  acc.push(p);
                  return acc;
                }, [])
                .map((p, idx) =>
                  p === 'ellipsis' ? (
                    <span key={`ellipsis-${idx}`} className="px-2 text-slate-600">...</span>
                  ) : (
                    <button
                      key={p}
                      onClick={() => setPage(p)}
                      className={`
                        min-w-[32px] h-8 rounded-lg text-xs font-medium
                        transition-colors
                        ${p === page
                          ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                          : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                        }
                      `}
                    >
                      {p}
                    </button>
                  )
                )}

              <button
                onClick={() => setPage(Math.min(totalPages || 1, page + 1))}
                disabled={page >= totalPages || totalPages === 0}
                className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/50
                  transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}