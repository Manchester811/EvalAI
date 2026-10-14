'use client';

import Link from 'next/link';
import { Bot, FileText, MoreHorizontal, Sparkles, X } from 'lucide-react';
import { usePathname } from 'next/navigation';

import { nav } from '@/lib/nav';

type SidebarProps = { isOpen: boolean; onClose: () => void };

export default function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className={`sidebar${isOpen ? ' sidebar-open' : ''}`} aria-label="Sidebar">
      <div className="sidebar-mobile-header">
        <span className="sr-only">Primary navigation</span>
        <button className="icon-button" type="button" aria-label="Close navigation" onClick={onClose}>
          <X size={19} aria-hidden="true" />
        </button>
      </div>
      <Link className="brand" href="/dashboard" onClick={onClose}>
        <span className="brand-mark" aria-hidden="true"><FileText size={23} strokeWidth={2.3} /></span>
        <span className="brand-copy">
          <span className="brand-name">EvalAI</span>
          <span className="brand-subtitle">AI-Powered<br />Answer Sheet Evaluator</span>
        </span>
      </Link>

      <nav className="primary-nav" aria-label="Primary navigation">
        {nav.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(`${item.href}/`));
          return (
            <Link
              key={item.label}
              className={`nav-link${isActive ? ' nav-link-active' : ''}`}
              href={item.href}
              aria-current={isActive ? 'page' : undefined}
              onClick={onClose}
            >
              <Icon size={18} strokeWidth={isActive ? 2.2 : 1.8} aria-hidden="true" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <div className="promo-card">
          <div className="promo-copy">Faster.<br /><span>Fairer.</span><br />Smarter<br /><span>Evaluation.</span></div>
          <Bot className="promo-bot" size={76} strokeWidth={1.2} aria-hidden="true" />
          <Sparkles className="promo-sparkle" size={14} aria-hidden="true" />
        </div>
        <div className="profile-card">
          <div className="profile-card-avatar" aria-hidden="true">RJ</div>
          <div className="profile-card-copy">
            <div className="profile-card-name">Rishabh Jain</div>
            <div className="profile-card-role">Faculty</div>
          </div>
          <button className="icon-button" type="button" aria-label="Open profile actions">
            <MoreHorizontal size={18} aria-hidden="true" />
          </button>
        </div>
      </div>
    </aside>
  );
}
