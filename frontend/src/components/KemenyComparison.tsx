import React from 'react';
import { Award, CheckCircle2, AlertTriangle, GitCompare, Layers, Compass } from 'lucide-react';
import type { KemenyMethodResult, KemenyComparisonSummary } from '../types/api';

interface KemenyComparisonProps {
  expertMethod: KemenyMethodResult;
  assignmentMethod: KemenyMethodResult;
  bruteforceMethod: KemenyMethodResult;
  comparison: KemenyComparisonSummary;
}

export const KemenyComparison: React.FC<KemenyComparisonProps> = ({
  expertMethod,
  assignmentMethod,
  bruteforceMethod,
  comparison,
}) => {
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
            <GitCompare size={20} color="var(--accent-primary)" />
            Сравнение трёх методов определения медианы Кемени
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Анализ согласованности между эвристиками и точным решением на множестве всех перестановок
          </p>
        </div>

        {/* Статус согласованности */}
        <div>
          {comparison.all_methods_agree ? (
            <span className="badge badge-emerald" style={{ padding: '8px 14px', fontSize: '0.85rem' }}>
              <CheckCircle2 size={16} /> Все 3 метода полностью совпали!
            </span>
          ) : (
            <span className="badge badge-amber" style={{ padding: '8px 14px', fontSize: '0.85rem' }}>
              <AlertTriangle size={16} /> Наблюдаются различия в оптимумах
            </span>
          )}
        </div>
      </div>

      {/* 3 Карточки методов */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '20px',
        marginBottom: '24px',
      }}>
        {/* 1. Среди экспертов */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          padding: '18px',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <Compass size={18} color="var(--accent-primary)" />
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
                1. Среди мнений экспертов
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Поиск минимума в строках матрицы D
              </div>
            </div>
          </div>

          <div style={{
            background: 'var(--bg-input)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '12px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              {expertMethod.criterion_name}:
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-primary)' }}>
              S по D = {expertMethod.criterion_value}
            </div>
          </div>

          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
            Оптимальные решения ({expertMethod.solutions.length}):
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
            {expertMethod.solutions.map((sol, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '6px',
                  padding: '8px 12px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 800, color: 'var(--accent-primary)', fontSize: '0.85rem' }}>
                    {sol.expert_id}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Σ_k d = {sol.total_distance}
                  </span>
                </div>
                <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#fff' }}>
                  {sol.order_str}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 2. Задача о назначениях */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          padding: '18px',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'rgba(59, 130, 246, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <Layers size={18} color="var(--accent-blue)" />
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
                2. Задача о назначениях
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Минимизация матрицы потерь r_ij
              </div>
            </div>
          </div>

          <div style={{
            background: 'var(--bg-input)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '12px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              {assignmentMethod.criterion_name}:
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-blue)' }}>
              Σ r_ij = {assignmentMethod.criterion_value}
            </div>
          </div>

          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
            Оптимальные назначения ({assignmentMethod.solutions.length}):
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
            {assignmentMethod.solutions.map((sol, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '6px',
                  padding: '8px 12px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 700, color: 'var(--accent-blue)', fontSize: '0.8rem' }}>
                    Вариант #{idx + 1}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Σ_k d = {sol.total_distance}
                  </span>
                </div>
                <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#fff' }}>
                  {sol.order_str}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 3. Полный перебор */}
        <div style={{
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          padding: '18px',
          display: 'flex',
          flexDirection: 'column',
          borderLeft: '4px solid var(--accent-emerald)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              background: 'rgba(16, 185, 129, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}>
              <Award size={18} color="var(--accent-emerald)" />
            </div>
            <div>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#fff' }}>
                3. Полный перебор (Истинный оптимум)
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Глобальный минимум на множестве N!
              </div>
            </div>
          </div>

          <div style={{
            background: 'var(--bg-input)',
            borderRadius: '8px',
            padding: '12px',
            marginBottom: '12px',
            border: '1px solid var(--border-subtle)',
          }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
              {bruteforceMethod.criterion_name}:
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#34d399' }}>
              Σ_k d = {bruteforceMethod.criterion_value}
            </div>
          </div>

          <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '8px' }}>
            Глобальные медианы Кемени ({bruteforceMethod.solutions.length}):
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '180px', overflowY: 'auto' }}>
            {bruteforceMethod.solutions.map((sol, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(16, 185, 129, 0.05)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  borderRadius: '6px',
                  padding: '8px 12px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 700, color: '#34d399', fontSize: '0.8rem' }}>
                    Медиана #{idx + 1}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#34d399' }}>
                    min d = {sol.total_distance}
                  </span>
                </div>
                <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#fff' }}>
                  {sol.order_str}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Метрики пересечения множеств решений */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '12px',
        padding: '16px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-around',
        flexWrap: 'wrap',
        gap: '16px',
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
            Среди экспертов ∩ Полный перебор
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>
            {comparison.intersection_experts_bruteforce} совпадений
          </div>
        </div>

        <div style={{ width: '1px', height: '36px', background: 'var(--border-subtle)' }} />

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
            Назначения ∩ Полный перебор
          </div>
          <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>
            {comparison.intersection_assignment_bruteforce} совпадений
          </div>
        </div>

        <div style={{ width: '1px', height: '36px', background: 'var(--border-subtle)' }} />

        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>
            Включение: Назначения ⊆ Перебор
          </div>
          <div style={{
            fontSize: '1.25rem',
            fontWeight: 800,
            color: comparison.assignment_is_subset_of_bruteforce ? '#34d399' : '#fb7185',
          }}>
            {comparison.assignment_is_subset_of_bruteforce ? 'Истина (True)' : 'Ложь (False)'}
          </div>
        </div>
      </div>
    </div>
  );
};
