import React, { useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { BarChart3, TrendingUp } from 'lucide-react';
import type { RankingsData, KemenyMethodResult } from '../types/api';

interface RankingChartsProps {
  rankings: RankingsData;
  kemenyBruteforce: KemenyMethodResult;
}

export const RankingCharts: React.FC<RankingChartsProps> = ({
  rankings,
  kemenyBruteforce,
}) => {
  const [activeTab, setActiveTab] = useState<'average' | 'median' | 'kemeny'>('average');

  // Подготовка данных для графика
  const getData = () => {
    if (activeTab === 'average') {
      return rankings.average.map(item => ({
        name: item.object,
        rankValue: item.value,
        place: item.place,
        displayValue: `Средний ранг: ${item.value.toFixed(2)}`,
      }));
    } else if (activeTab === 'median') {
      return rankings.median.map(item => ({
        name: item.object,
        rankValue: item.value,
        place: item.place,
        displayValue: `Медиана рангов: ${item.value.toFixed(2)}`,
      }));
    } else {
      // Истинная медиана Кемени (первое оптимальное ранжирование)
      const bestOrder = kemenyBruteforce.solutions[0]?.order || [];
      return bestOrder.map((obj, idx) => ({
        name: obj,
        rankValue: idx + 1,
        place: idx + 1,
        displayValue: `Позиция в медиане Кемени: ${idx + 1}`,
      }));
    }
  };

  const chartData = getData();

  // Палитра градиента от лучшего (1 место) к худшим
  const colors = [
    '#6366f1',
    '#8b5cf6',
    '#3b82f6',
    '#06b6d4',
    '#10b981',
    '#f59e0b',
    '#f43f5e',
  ];

  return (
    <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px',
        flexWrap: 'wrap',
        gap: '12px',
      }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={20} color="var(--accent-primary)" />
            Итоговые ранжирования объектов
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Горизонтальная диаграмма рангов (чем меньше числовое значение ранга — тем объект предпочтительнее)
          </p>
        </div>

        {/* Табы переключения методов */}
        <div style={{
          display: 'flex',
          background: 'rgba(255, 255, 255, 0.05)',
          padding: '4px',
          borderRadius: '10px',
          border: '1px solid var(--border-subtle)',
        }}>
          <button
            onClick={() => setActiveTab('average')}
            style={{
              padding: '6px 14px',
              fontSize: '0.8rem',
              fontWeight: 600,
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'average' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'average' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            По среднему
          </button>
          <button
            onClick={() => setActiveTab('median')}
            style={{
              padding: '6px 14px',
              fontSize: '0.8rem',
              fontWeight: 600,
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'median' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'median' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            По медиане
          </button>
          <button
            onClick={() => setActiveTab('kemeny')}
            style={{
              padding: '6px 14px',
              fontSize: '0.8rem',
              fontWeight: 600,
              borderRadius: '7px',
              border: 'none',
              background: activeTab === 'kemeny' ? 'var(--accent-primary)' : 'transparent',
              color: activeTab === 'kemeny' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            Медиана Кемени
          </button>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 2fr) minmax(240px, 1fr)', gap: '24px', alignItems: 'center' }}>
        {/* Горизонтальный Bar Chart */}
        <div style={{ height: '280px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
            >
              <XAxis
                type="number"
                stroke="#64748b"
                tick={{ fill: '#94a3b8', fontSize: 12 }}
                domain={[0, 'dataMax + 1']}
              />
              <YAxis
                type="category"
                dataKey="name"
                stroke="#64748b"
                tick={{ fill: '#f8fafc', fontSize: 13, fontWeight: 700 }}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div style={{
                        background: 'rgba(15, 23, 42, 0.95)',
                        border: '1px solid rgba(255, 255, 255, 0.15)',
                        borderRadius: '8px',
                        padding: '10px 14px',
                        boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
                      }}>
                        <div style={{ fontWeight: 800, fontSize: '0.9rem', color: '#fff', marginBottom: '4px' }}>
                          Объект: {data.name}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#a5b4fc' }}>
                          Место: {data.place}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                          {data.displayValue}
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="rankValue" radius={[0, 6, 6, 0]}>
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={colors[index % colors.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Таблица итогового порядка */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          padding: '16px',
        }}>
          <div style={{
            fontSize: '0.85rem',
            fontWeight: 700,
            color: 'var(--text-secondary)',
            marginBottom: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
          }}>
            <TrendingUp size={16} color="var(--accent-primary)" />
            Порядок предпочтения альтернатив
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {chartData.map((item, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '8px 12px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  borderRadius: '6px',
                  borderLeft: `4px solid ${colors[idx % colors.length]}`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <span style={{
                    width: '22px',
                    height: '22px',
                    borderRadius: '50%',
                    background: 'rgba(255, 255, 255, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                  }}>
                    {item.place}
                  </span>
                  <span style={{ fontWeight: 800, color: '#fff', fontSize: '0.9rem' }}>
                    {item.name}
                  </span>
                </div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  {item.rankValue.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
