import {
  MessageSquare,
  Link,
  User,
  Wrench,
  Phone,
  Mail,
  Hash,
  DollarSign,
} from 'lucide-react';

type EntityType = 'slang_term' | 'link' | 'account' | 'tool' | 'phone' | 'email' | 'crypto_address';

interface EntityTagProps {
  entityType: EntityType;
  value: string;
  confidence: number;
  onClick?: () => void;
}

const entityConfig: Record<string, {
  bg: string;
  text: string;
  border: string;
  label: string;
  icon: typeof Hash;
}> = {
  slang_term: {
    bg: 'bg-purple-500/15',
    text: 'text-purple-400',
    border: 'border-purple-500/30',
    label: '黑话',
    icon: MessageSquare,
  },
  link: {
    bg: 'bg-blue-500/15',
    text: 'text-blue-400',
    border: 'border-blue-500/30',
    label: '链接',
    icon: Link,
  },
  account: {
    bg: 'bg-cyan-500/15',
    text: 'text-cyan-400',
    border: 'border-cyan-500/30',
    label: '账号',
    icon: User,
  },
  tool: {
    bg: 'bg-amber-500/15',
    text: 'text-amber-400',
    border: 'border-amber-500/30',
    label: '工具',
    icon: Wrench,
  },
  phone: {
    bg: 'bg-emerald-500/15',
    text: 'text-emerald-400',
    border: 'border-emerald-500/30',
    label: '手机',
    icon: Phone,
  },
  email: {
    bg: 'bg-rose-500/15',
    text: 'text-rose-400',
    border: 'border-rose-500/30',
    label: '邮箱',
    icon: Mail,
  },
  crypto_address: {
    bg: 'bg-yellow-500/15',
    text: 'text-yellow-400',
    border: 'border-yellow-500/30',
    label: '加密',
    icon: DollarSign,
  },
};

export default function EntityTag({ entityType, value, confidence, onClick }: EntityTagProps) {
  const config = entityConfig[entityType];
  if (!config) return null;

  const { bg, text, border, label, icon: Icon } = config;

  const confidencePercent = Math.round(confidence * 100);

  return (
    <span
      onClick={onClick}
      className={`
        inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs
        font-medium whitespace-nowrap select-none
        ${bg} ${text} ${border}
        ${onClick ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}
      `}
      title={`${label}: ${value} (置信度: ${confidencePercent}%)`}
    >
      <Icon className="w-3 h-3 flex-shrink-0" />
      <span className="max-w-[160px] truncate">{value}</span>
      <span
        className="ml-0.5 text-[10px] opacity-60 flex-shrink-0"
        style={{ opacity: Math.max(0.3, confidence) }}
      >
        {confidencePercent}%
      </span>
    </span>
  );
}