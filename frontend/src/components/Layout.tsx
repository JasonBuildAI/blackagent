import { useState, type ReactNode } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FileSearch,
  ChevronLeft,
  ChevronRight,
  Shield,
  Menu,
  X,
  Settings,
} from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

const navItems = [
  {
    to: '/',
    label: '仪表盘',
    icon: LayoutDashboard,
  },
  {
    to: '/intelligence',
    label: '情报列表',
    icon: FileSearch,
  },
  {
    to: '/settings',
    label: '系统设置',
    icon: Settings,
  },
];

export default function Layout({ children }: LayoutProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const sidebarWidth = collapsed ? 'w-16' : 'w-56';

  return (
    <div className="flex h-screen overflow-hidden bg-slate-900">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-50
          ${sidebarWidth}
          flex flex-col
          bg-slate-800 border-r border-slate-700
          transition-all duration-300 ease-in-out
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Logo / Header */}
        <div className="flex items-center h-14 px-3 border-b border-slate-700">
          <div className="flex items-center gap-2.5 min-w-0">
            <Shield className="w-6 h-6 text-cyan-500 flex-shrink-0" />
            {!collapsed && (
              <span className="text-sm font-semibold text-white truncate whitespace-nowrap">
                黑灰产情报分析系统
              </span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-3 px-2 space-y-1 overflow-y-auto scrollbar-thin">
          {navItems.map((item) => {
            const isActive = location.pathname === item.to || 
              (item.to !== '/' && location.pathname.startsWith(item.to));
            const Icon = item.icon;

            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setMobileOpen(false)}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-lg
                  transition-all duration-200 group
                  ${isActive
                    ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-white hover:bg-slate-700/50 border border-transparent'
                  }
                `}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-cyan-400' : ''}`} />
                {!collapsed && (
                  <span className="text-sm font-medium truncate">{item.label}</span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Collapse toggle (desktop) */}
        <div className="hidden lg:block border-t border-slate-700 p-2">
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="w-full flex items-center justify-center py-2 rounded-lg
              text-slate-500 hover:text-slate-300 hover:bg-slate-700/50
              transition-colors duration-200"
          >
            {collapsed ? (
              <ChevronRight className="w-4 h-4" />
            ) : (
              <ChevronLeft className="w-4 h-4" />
            )}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top header */}
        <header className="flex items-center h-14 px-4 bg-slate-800/50 border-b border-slate-700 flex-shrink-0">
          {/* Mobile menu button */}
          <button
            onClick={() => setMobileOpen(true)}
            className="lg:hidden p-1.5 mr-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/50 transition-colors"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="flex-1" />

          {/* System status indicator */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-700/50 border border-slate-600/50">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-xs text-slate-400">系统运行中</span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto scrollbar-thin p-4 md:p-6">
          <div className="animate-fade-in">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}