import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import {
  Database,
  AlertTriangle,
  CheckCircle2,
  Clock,
  RefreshCw,
  Loader2,
  Inbox,
  AlertCircle,
} from 'lucide-react';
import { getDashboardStats } from '../api';
import type { DashboardStats } from '../types';
import StatsCard from '../components/StatsCard';
import RiskBadge from '../components/RiskBadge';

const RISK_COLORS: Record<string, string> = {
  critical: '#dc2626',
  high: '#ea580c',
  medium: '#ca8a04',
  low: '#16a34a',
};

const RISK_LABELS: Record<string, string> = {
  critical: '严重',
  high: '高危',
  medium: '中危',
  low: '低危',
};

const SOURCE_COLORS = [
  '#06b6d4',
  '#8b5cf6',
  '#f59e0b',
  '#10b981',
  '#ef4444',
  '#3b82f6',
  '#ec4899',
  '#6366f1',
  '#14b8a6',
  '#f97316',
];

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return '刚刚';
  if (diffMins < 60) return `${diffMins}分钟前`;
  if (diffHours < 24) return `${diffHours}小时前`;
  if (diffDays < 7) return `${diffDays}天前`;

  return d.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

const CustomPieTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 shadow-lg">
        <p className="text-xs text-slate-300">{data.name}</p>
        <p className="text-sm font-bold" style={{ color: data.payload.fill }}>
          {data.value} 条
        </p>
      </div>
    );
  }
  return null;
};

const CustomBarTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 shadow-lg">
        <p className="text-xs text-slate-300">{label}</p>
        <p className="text-sm font-bold text-cyan-400">{payload[0].value} 条</p>
      </div>
    );
  }
  return null;
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = useCallback(async (showRefreshing: boolean = false) => {
    try {
      if (showRefreshing) setRefreshing(true);
      setError(null);
      const data = await getDashboardStats();
      setStats(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '获取数据失败';
      setError(msg);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  // Auto-refresh every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => fetchStats(true), 30000);
    return () => clearInterval(interval);
  }, [fetchStats]);

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-10 h-10 text-cyan-500 animate-spin" />
          <p className="text-slate-400 text-sm">正在加载仪表盘数据...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4 text-center max-w-md">
          <div className="p-4 rounded-full bg-red-500/10">
            <AlertCircle className="w-12 h-12 text-red-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">数据加载失败</h3>
            <p className="text-sm text-slate-400">{error}</p>
          </div>
          <button
            onClick={() => {
              setLoading(true);
              fetchStats();
            }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg
              bg-cyan-500/15 text-cyan-400 border border-cyan-500/30
              hover:bg-cyan-500/25 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>重新加载</span>
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (!stats || stats.total_items === 0) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-xl md:text-2xl font-bold text-white">仪表盘</h1>
          <button
            onClick={() => fetchStats(true)}
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
              text-slate-400 hover:text-white hover:bg-slate-700/50
              transition-colors text-sm"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>刷新</span>
          </button>
        </div>

        <div className="flex items-center justify-center h-80">
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="p-4 rounded-full bg-slate-700/50">
              <Inbox className="w-12 h-12 text-slate-500" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white mb-1">暂无数据</h3>
              <p className="text-sm text-slate-400">系统尚未收录任何情报数据，请先录入情报信息</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Data state
  const riskData = Object.entries(stats.risk_distribution).map(([key, value]) => ({
    name: RISK_LABELS[key] || key,
    value,
    fill: RISK_COLORS[key] || '#64748b',
  }));

  const sourceData = Object.entries(stats.source_distribution)
    .map(([key, value], index) => ({
      name: key,
      value,
      fill: SOURCE_COLORS[index % SOURCE_COLORS.length],
    }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-xl md:text-2xl font-bold text-white">仪表盘</h1>
        <button
          onClick={() => fetchStats(true)}
          disabled={refreshing}
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg
            text-slate-400 hover:text-white hover:bg-slate-700/50
            transition-colors text-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          <span>{refreshing ? '刷新中...' : '刷新'}</span>
        </button>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
          <button
            onClick={() => fetchStats(true)}
            className="ml-auto text-red-400 hover:text-red-300 underline text-xs"
          >
            重试
          </button>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
        <StatsCard
          icon={Database}
          label="总情报数"
          value={stats.total_items}
          accentColor="bg-cyan-500"
          iconBg="bg-cyan-500/15 text-cyan-400"
        />
        <StatsCard
          icon={AlertTriangle}
          label="高危预警"
          value={stats.critical_alerts}
          accentColor="bg-red-500"
          iconBg="bg-red-500/15 text-red-400"
        />
        <StatsCard
          icon={CheckCircle2}
          label="已分析"
          value={stats.analyzed_count}
          accentColor="bg-emerald-500"
          iconBg="bg-emerald-500/15 text-emerald-400"
        />
        <StatsCard
          icon={Clock}
          label="待处理"
          value={stats.pending_count}
          accentColor="bg-amber-500"
          iconBg="bg-amber-500/15 text-amber-400"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
        {/* Risk Distribution Pie */}
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-4 md:p-6">
          <h2 className="text-base font-semibold text-white mb-4">风险等级分布</h2>
          {riskData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="transparent"
                >
                  {riskData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip content={<CustomPieTooltip />} />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(value: string) => (
                    <span className="text-slate-400 text-xs">{value}</span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-500 text-sm">
              暂无风险分布数据
            </div>
          )}
        </div>

        {/* Source Distribution Bar */}
        <div className="rounded-xl border border-slate-700 bg-slate-800 p-4 md:p-6">
          <h2 className="text-base font-semibold text-white mb-4">来源分布 TOP10</h2>
          {sourceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={sourceData}
                layout="vertical"
                margin={{ top: 0, right: 10, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis
                  type="number"
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  axisLine={{ stroke: '#334155' }}
                  tickLine={false}
                />
                <YAxis
                  type="category"
                  dataKey="name"
                  tick={{ fill: '#94a3b8', fontSize: 11 }}
                  axisLine={false}
                  tickLine={false}
                  width={80}
                />
                <Tooltip content={<CustomBarTooltip />} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={24}>
                  {sourceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-500 text-sm">
              暂无来源分布数据
            </div>
          )}
        </div>
      </div>

      {/* Recent Intelligence List */}
      <div className="rounded-xl border border-slate-700 bg-slate-800 overflow-hidden">
        <div className="flex items-center justify-between px-4 md:px-6 py-4 border-b border-slate-700">
          <h2 className="text-base font-semibold text-white">最近情报</h2>
          <button
            onClick={() => navigate('/intelligence')}
            className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            查看全部 &rarr;
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700/50">
                <th className="text-left px-4 md:px-6 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  来源类型
                </th>
                <th className="text-left px-4 md:px-6 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  来源名称
                </th>
                <th className="text-left px-4 md:px-6 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  风险等级
                </th>
                <th className="text-left px-4 md:px-6 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  状态
                </th>
                <th className="text-left px-4 md:px-6 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">
                  时间
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/30">
              {stats.recent_items.map((item) => (
                <tr
                  key={item.id}
                  onClick={() => navigate(`/intelligence/${item.id}`)}
                  className="hover:bg-slate-700/30 cursor-pointer transition-colors"
                >
                  <td className="px-4 md:px-6 py-3">
                    <span className="text-slate-300 text-xs">{item.source_type}</span>
                  </td>
                  <td className="px-4 md:px-6 py-3">
                    <span className="text-slate-400 text-xs">{item.source_name}</span>
                  </td>
                  <td className="px-4 md:px-6 py-3">
                    <RiskBadge level={item.risk_level} size="sm" />
                  </td>
                  <td className="px-4 md:px-6 py-3">
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
                      {item.status === 'analyzed' ? '已分析' : item.status === 'processing' ? '分析中' : '待处理'}
                    </span>
                  </td>
                  <td className="px-4 md:px-6 py-3">
                    <span className="text-slate-500 text-xs whitespace-nowrap">
                      {formatDate(item.ingested_at)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}