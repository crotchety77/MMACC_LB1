import React from 'react';
import { Users, Box, Shuffle, Award, CheckCircle2, AlertCircle } from 'lucide-react';
import type { AnalysisSummary } from '../types/api';

interface DashboardOverviewProps {
  summary: AnalysisSummary;
  allAgree: boolean;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({ summary, allAgree }) => {
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
      gap: '16px',
      marginBottom: '24px',
    }}>
      {/* Эксперты */}
      <div className="glass-card" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
            Эксперты
          </span>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'rgba(99, 102, 241, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Users size={18} color="var(--accent-primary)" />
          </div>
        </div>
        <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-primary)' }}>
          {summary.num_experts}
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Количество экспертных оценок
        </p>
      </div>

      {/* Объекты */}
      <div className="glass-card" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
            Объекты (проекты)
          </span>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'rgba(59, 130, 246, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Box size={18} color="var(--accent-blue)" />
          </div>
        </div>
        <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-primary)' }}>
          {summary.num_objects}
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          Ранжируемых альтернатив
        </p>
      </div>

      {/* Уникальных мнений */}
      <div className="glass-card" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
            Уникальных ранжирований
          </span>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'rgba(245, 158, 11, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Shuffle size={18} color="var(--accent-amber)" />
          </div>
        </div>
        <div style={{ fontSize: '1.85rem', fontWeight: 800, color: 'var(--text-primary)' }}>
          {summary.unique_rankings_count} / {summary.num_experts}
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          {summary.unique_rankings_count === summary.num_experts ? 'Все мнения различаются' : 'Есть совпадающие мнения'}
        </p>
      </div>

      {/* Медиана Кемени */}
      <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid var(--accent-primary)' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
            Медиана Кемени
          </span>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'rgba(16, 185, 129, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <Award size={18} color="var(--accent-emerald)" />
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#34d399' }}>
            Σ = {summary.best_kemeny_distance}
          </div>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            ({summary.best_kemeny_orders.length} оптим.)
          </span>
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {summary.best_kemeny_orders[0]?.join(' > ')}
        </p>
      </div>

      {/* Согласованность методов */}
      <div className="glass-card" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 600 }}>
            Согласованность подходов
          </span>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: allAgree ? 'rgba(16, 185, 129, 0.15)' : 'rgba(244, 63, 94, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            {allAgree ? (
              <CheckCircle2 size={18} color="var(--accent-emerald)" />
            ) : (
              <AlertCircle size={18} color="var(--accent-rose)" />
            )}
          </div>
        </div>
        <div style={{ fontSize: '1.25rem', fontWeight: 700, color: allAgree ? '#34d399' : '#fb7185' }}>
          {allAgree ? 'Полное совпадение' : 'Разные оптимумы'}
        </div>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
          {allAgree ? 'Все 3 метода дают один результат' : 'Задача назначений или эксперты дают разный оптимум'}
        </p>
      </div>
    </div>
  );
};
