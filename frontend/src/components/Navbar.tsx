import React from 'react';
import { GitBranch, Layers } from 'lucide-react';

interface NavbarProps {
  apiStatus: 'checking' | 'connected' | 'error';
}

export const Navbar: React.FC<NavbarProps> = ({ apiStatus }) => {
  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(10, 13, 20, 0.85)',
      backdropFilter: 'blur(12px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'var(--accent-gradient)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 15px rgba(99, 102, 241, 0.35)',
        }}>
          <Layers size={22} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', margin: 0 }}>
              MMACC <span className="text-gradient">LB1</span>
            </h1>
            <span className="badge badge-indigo">FastAPI + React</span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>
            Методы экспертных оценок • Медиана Кемени
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          borderRadius: '9999px',
          background: 'rgba(255, 255, 255, 0.04)',
          border: '1px solid var(--border-subtle)',
          fontSize: '0.8rem',
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            backgroundColor: apiStatus === 'connected' ? '#10b981' : apiStatus === 'checking' ? '#f59e0b' : '#ef4444',
            boxShadow: apiStatus === 'connected' ? '0 0 10px #10b981' : 'none',
          }} />
          <span style={{ color: 'var(--text-secondary)' }}>
            API: {apiStatus === 'connected' ? 'Онлайн' : apiStatus === 'checking' ? 'Проверка...' : 'Ошибка'}
          </span>
        </div>

        <a
          href="https://github.com/crotchety77/MMACC_LB1"
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-secondary"
          style={{ textDecoration: 'none', padding: '8px 14px', fontSize: '0.825rem' }}
        >
          <GitBranch size={16} />
          GitHub
        </a>
      </div>
    </header>
  );
};
