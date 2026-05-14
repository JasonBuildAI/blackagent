import { useEffect, useState, useRef } from 'react';
import type { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  icon: LucideIcon;
  label: string;
  value: number;
  accentColor: string;
  iconBg: string;
  prefix?: string;
  suffix?: string;
}

function useAnimatedValue(targetValue: number, duration: number = 600): number {
  const [displayValue, setDisplayValue] = useState(0);
  const prevTargetRef = useRef(0);
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const startValueRef = useRef(0);

  useEffect(() => {
    if (targetValue === prevTargetRef.current) {
      return;
    }

    prevTargetRef.current = targetValue;

    const startValue = startValueRef.current;
    const diff = targetValue - startValue;

    const animate = (timestamp: number) => {
      if (startTimeRef.current === null) {
        startTimeRef.current = timestamp;
      }

      const elapsed = timestamp - startTimeRef.current;
      const progress = Math.min(elapsed / duration, 1);

      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(startValue + diff * eased);

      setDisplayValue(current);

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animate);
      } else {
        startValueRef.current = targetValue;
        startTimeRef.current = null;
      }
    };

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    startTimeRef.current = null;
    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [targetValue, duration]);

  return displayValue;
}

export default function StatsCard({
  icon: Icon,
  label,
  value,
  accentColor,
  iconBg,
  prefix = '',
  suffix = '',
}: StatsCardProps) {
  const animatedValue = useAnimatedValue(value);

  return (
    <div
      className="
        relative overflow-hidden rounded-xl border border-slate-700
        bg-slate-800 p-4 md:p-5
        hover:border-slate-600 hover:shadow-lg
        transition-all duration-300
      "
    >
      {/* Subtle top accent line */}
      <div className={`absolute top-0 left-0 right-0 h-0.5 ${accentColor}`} />

      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <p className="text-xs md:text-sm text-slate-400 font-medium truncate">{label}</p>
          <p className={`mt-1 text-2xl md:text-3xl font-bold ${accentColor.replace('bg-', 'text-').replace('-500', '-400')}`}>
            {prefix}{animatedValue.toLocaleString()}{suffix}
          </p>
        </div>
        <div className={`flex-shrink-0 p-2.5 rounded-lg ${iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
}