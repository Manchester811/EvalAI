'use client';

import { Bell, ChevronDown, Menu, Search } from 'lucide-react';
import { FormEvent, useState } from 'react';

type TopbarProps = { onMenu: () => void };

export default function Topbar({ onMenu }: TopbarProps) {
  const [query, setQuery] = useState('');
  const [openMenu, setOpenMenu] = useState<'notifications' | 'profile' | null>(null);

  const submitSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setOpenMenu(null);
  };

  return (
    <header className="topbar" aria-label="Topbar">
      <button className="icon-button mobile-menu-button" type="button" aria-label="Open navigation" onClick={onMenu}>
        <Menu size={21} aria-hidden="true" />
      </button>
      <form className="search-form" role="search" onSubmit={submitSearch}>
        <label className="sr-only" htmlFor="global-search">Search students, exams, or evaluations</label>
        <Search className="search-icon" size={17} aria-hidden="true" />
        <input
          id="global-search"
          className="search-input"
          name="search"
          type="search"
          autoComplete="off"
          placeholder="Search students, exams, or evaluations…"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button className="search-submit" type="submit">Search</button>
      </form>
      <div className="topbar-actions">
        <button
          className="icon-button notification-button"
          type="button"
          aria-label="Notifications, 3 unread"
          aria-haspopup="true"
          aria-expanded={openMenu === 'notifications'}
          onClick={() => setOpenMenu(openMenu === 'notifications' ? null : 'notifications')}
        >
          <Bell size={20} aria-hidden="true" />
          <span className="notification-dot" aria-hidden="true" />
          <span className="notification-count">3 unread notifications</span>
        </button>
        <button
          className="profile-trigger"
          type="button"
          aria-label="Open profile menu"
          aria-haspopup="menu"
          aria-expanded={openMenu === 'profile'}
          onClick={() => setOpenMenu(openMenu === 'profile' ? null : 'profile')}
        >
          <span className="profile-avatar" aria-hidden="true">RJ</span>
          <ChevronDown size={15} aria-hidden="true" />
        </button>
      </div>
      {openMenu === 'notifications' && (
        <div className="topbar-menu" role="status" aria-live="polite">
          <h3>Notifications</h3>
          <div className="topbar-menu-item">3 evaluations are ready for review.</div>
          <div className="topbar-menu-item">Your latest export is ready to download.</div>
        </div>
      )}
      {openMenu === 'profile' && (
        <div className="topbar-menu" role="menu">
          <h3>Account</h3>
          <button className="topbar-menu-item" type="button" role="menuitem">View profile</button>
          <button className="topbar-menu-item" type="button" role="menuitem">Account settings</button>
        </div>
      )}
    </header>
  );
}
