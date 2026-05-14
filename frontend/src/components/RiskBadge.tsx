import type { RiskLevel } from '../types';
import { AlertTriangle, AlertCircle, AlertOctagon, ShieldCheck, HelpCircle } from 'lucide-react';

interface RiskBadgeProps {
  level: RiskLevel | null;
  size?: 'sm' | 'md' | 'lg';
}

const riskConfig: Record<RiskLevel, {
  bg: string;
  text: string;
  border: string;
  label: string;
  icon: typeof AlertTriangle;
  pulse: boolean;
}> = {
  critical: {
    bg: 'bg-red-500/15',
    text: 'text-red-400',
    border: 'border-red-500/40',
    label: '严重',
    icon: AlertOctagon,
    pulse: true,
  },
  high: {
    bg: 'bg-orange-500/15',
    text: 'text-orange-400',
    border: 'border-orange-500/40',
    label: '高危',
    icon: AlertTriangle,
    pulse: false,
  },
  medium: {
    bg: 'bg-yellow-500/15',
    text: 'text-yellow-400',
    border: 'border-yellow-500/40',
    label: '中危',
    icon: AlertCircle,
    pulse: false,
  },
  low: {
    bg: 'bg-emerald-500/15',
    text: 'text-emerald-400',
    border: 'border-emerald-500/40',
    label: '低危',
    icon: ShieldCheck,
    pulse: false,
  },
};

const unknownConfig = {
  bg: 'bg-slate-500/15',
  text: 'text-slate-400',
  border: 'border-slate-500/40',
  label: '未知',
  icon: HelpCircle,
  pulse: false,
};

const sizeClasses: Record<string, string> = {
  sm: 'px-1.5 py-0.5 text-[10px] gap-0.5',
  md: 'px-2 py-0.5 text-xs gap-1',
  lg: 'px-3 py-1 text-sm gap-1.5',
};

const iconSize: Record<string, string> = {
  sm: 'w-2.5 h-2.5',
  md: 'w-3 h-3',
  lg: 'w-3.5 h-3.5',
};

export default function RiskBadge({ level, size = 'md' }: RiskBadgeProps) {
  if (!level) {
    const { bg, text, border, label, pulse, icon: Icon } = unknownConfig;
    return (
      <span
        className={`
          inline-flex items-center rounded-md border font-medium whitespace-nowrap
          ${bg} ${text} ${border} ${sizeClasses[size]}
          ${pulse ? 'animate-pulse-slow' : ''}
        `}
      >
        <Icon className={iconSize[size]} />
        {label}
      </span>
    );
  }

  const config = riskConfig[level];
  if (!config) {
    const { bg, text, border, label, pulse, icon: Icon } = unknownConfig;
    return (
      <span
        className={`
          inline-flex items-center rounded-md border font-medium whitespace-nowrap
          ${bg} ${text} ${border} ${sizeClasses[size]}
          ${pulse ? 'animate-pulse-slow' : ''}
        `}
      >
        <Icon className={iconSize[size]} />
        {label}
      </span>
    );
  }

  const { bg, text, border, label, pulse, icon: Icon } = config;

  return (
    <span
      className={`
        inline-flex items-center rounded-md border font-medium whitespace-nowrap
        ${bg} ${text} ${border} ${sizeClasses[size]}
        ${pulse ? 'animate-pulse-slow' : ''}
      `}
    >
      <Icon className={iconSize[size]} />
      {label}
    </span>
  );
}