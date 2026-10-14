'use client';

import { useState } from 'react';

import Sidebar from './Sidebar';
import Topbar from './Topbar';

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">Skip to main content</a>
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      {sidebarOpen && (
        <button className="sidebar-overlay" type="button" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />
      )}
      <div className="app-content">
        <Topbar onMenu={() => setSidebarOpen(true)} />
        <main id="main-content" className="app-main" aria-label="Main content">
          <div className="app-main-inner">{children}</div>
        </main>
      </div>
    </div>
  );
}
