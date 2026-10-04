import React, { useState } from 'react';
import { Grid, Eye, Info } from 'lucide-react';
import type { MatrixData } from '../types/api';

interface InteractiveMatrixProps {
  matrices: {
    transformed: MatrixData;
    preferences: MatrixData;
    distance: MatrixData;
    loss: MatrixData;
    assignment: MatrixData;
  };
  binaryRelations: Record<string, MatrixData>;
  diffMatrices: Record<string, MatrixData>;
}

export const InteractiveMatrix: React.FC<InteractiveMatrixProps> = ({
  matrices,
  binaryRelations,
  diffMatrices,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('transformed');
  const [selectedSubKey, setSelectedSubKey] = useState<string>('');
  const [hoveredCell, setHoveredCell] = useState<{ row: number; col: number } | null>(null);

  // Определяем активную матрицу
  let currentMatrix: MatrixData;
  if (selectedCategory === 'binary_relations') {
    const keys = Object.keys(binaryRelations);
    const key = selectedSubKey && binaryRelations[selectedSubKey] ? selectedSubKey : keys[0];
    currentMatrix = binaryRelations[key] || matrices.transformed;
  } else if (selectedCategory === 'diff_matrices') {
    const keys = Object.keys(diffMatrices);
    const key = selectedSubKey && diffMatrices[selectedSubKey] ? selectedSubKey : keys[0];
    currentMatrix = diffMatrices[key] || matrices.transformed;
  } else {
    currentMatrix = (matrices as Record<string, MatrixData>)[selectedCategory] || matrices.transformed;
  }

  // Расчёт min и max значений для динамического heatmap
  const allValues = currentMatrix.data.flat();
  const minVal = Math.min(...allValues);
  const maxVal = Math.max(...allValues);
  const isBinary = (minVal === 0 && maxVal === 1);

  // Вычисление цвета ячейки
  const getCellColor = (val: number, isHoveredRow: boolean, isHoveredCol: boolean, isHovered: boolean) => {
    let baseColor = 'transparent';
    if (isBinary) {
      baseColor = val === 1 ? 'rgba(99, 102, 241, 0.45)' : 'rgba(255, 255, 255, 0.03)';
    } else {
      const ratio = maxVal > minVal ? (val - minVal) / (maxVal - minVal) : 0;
      // Для матрицы расстояний или рангов: чем больше значение, тем теплее/насыщеннее
      baseColor = `rgba(99, 102, 241, ${0.1 + ratio * 0.65})`;
    }

    if (isHovered) {
      return '#818cf8'; // Яркая подсветка текущей ячейки
    }
    if (isHoveredRow || isHoveredCol) {
      return 'rgba(255, 255, 255, 0.12)'; // Подсветка перекрестья строки и столбца
    }
    return baseColor;
  };

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
            <Grid size={20} color="var(--accent-primary)" />
            Интерактивные матрицы (Heatmap)
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Наведите на ячейку для подсветки строки, столбца и отображения точного значения
          </p>
        </div>

        {/* Переключатель категорий матриц */}
        <div style={{
          display: 'flex',
          background: 'rgba(255, 255, 255, 0.05)',
          padding: '4px',
          borderRadius: '10px',
          border: '1px solid var(--border-subtle)',
          flexWrap: 'wrap',
          gap: '4px',
        }}>
          {[
            { id: 'transformed', label: 'Эксперт × Объект' },
            { id: 'preferences', label: 'Векторы π^(k)' },
            { id: 'distance', label: 'Расстояния (D)' },
            { id: 'loss', label: 'Потери (r_ij)' },
            { id: 'assignment', label: 'Назначения (X)' },
            { id: 'binary_relations', label: 'Бинарные отношения' },
            { id: 'diff_matrices', label: 'Разности |A - B|' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => {
                setSelectedCategory(tab.id);
                setSelectedSubKey('');
              }}
              style={{
                padding: '6px 12px',
                fontSize: '0.75rem',
                fontWeight: 600,
                borderRadius: '7px',
                border: 'none',
                background: selectedCategory === tab.id ? 'var(--accent-primary)' : 'transparent',
                color: selectedCategory === tab.id ? '#fff' : 'var(--text-secondary)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Подвыбор (для бинарных отношений и разностей) */}
      {(selectedCategory === 'binary_relations' || selectedCategory === 'diff_matrices') && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Выберите срез:</span>
          <select
            value={selectedSubKey}
            onChange={(e) => setSelectedSubKey(e.target.value)}
            style={{
              background: 'var(--bg-input)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '6px',
              padding: '6px 12px',
              fontSize: '0.8rem',
              outline: 'none',
            }}
          >
            {selectedCategory === 'binary_relations'
              ? Object.keys(binaryRelations).map(k => (
                  <option key={k} value={k}>Матрица эксперта {k}</option>
                ))
              : Object.keys(diffMatrices).map(k => (
                  <option key={k} value={k}>Пара {k}</option>
                ))}
          </select>
        </div>
      )}

      {/* Описание активной матрицы */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '8px',
        padding: '10px 14px',
        marginBottom: '16px',
        fontSize: '0.85rem',
      }}>
        <Info size={16} color="var(--accent-blue)" />
        <span style={{ fontWeight: 700, color: '#fff' }}>{currentMatrix.name}:</span>
        <span style={{ color: 'var(--text-secondary)' }}>{currentMatrix.description}</span>
      </div>

      {/* Таблица Heatmap */}
      <div style={{ overflowX: 'auto', paddingBottom: '10px' }}>
        <table style={{
          borderCollapse: 'separate',
          borderSpacing: '4px',
          width: '100%',
          textAlign: 'center',
        }}>
          <thead>
            <tr>
              <th style={{
                padding: '10px',
                fontSize: '0.8rem',
                color: 'var(--text-muted)',
                fontWeight: 600,
              }}>
                Строка \ Столбец
              </th>
              {currentMatrix.cols.map((colName, colIdx) => (
                <th
                  key={colIdx}
                  style={{
                    padding: '10px',
                    fontSize: '0.85rem',
                    fontWeight: 700,
                    color: hoveredCell?.col === colIdx ? 'var(--accent-primary)' : 'var(--text-secondary)',
                    transition: 'color 0.15s ease',
                  }}
                >
                  {colName}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentMatrix.rows.map((rowName, rowIdx) => (
              <tr key={rowIdx}>
                <td style={{
                  padding: '10px 14px',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  color: hoveredCell?.row === rowIdx ? 'var(--accent-primary)' : 'var(--text-primary)',
                  textAlign: 'right',
                  whiteSpace: 'nowrap',
                  transition: 'color 0.15s ease',
                }}>
                  {rowName}
                </td>
                {currentMatrix.cols.map((_, colIdx) => {
                  const val = currentMatrix.data[rowIdx][colIdx];
                  const isHovered = hoveredCell?.row === rowIdx && hoveredCell?.col === colIdx;
                  const isRowHover = hoveredCell?.row === rowIdx;
                  const isColHover = hoveredCell?.col === colIdx;

                  return (
                    <td
                      key={colIdx}
                      onMouseEnter={() => setHoveredCell({ row: rowIdx, col: colIdx })}
                      onMouseLeave={() => setHoveredCell(null)}
                      style={{
                        padding: '12px 14px',
                        background: getCellColor(val, isRowHover, isColHover, isHovered),
                        borderRadius: '6px',
                        color: isHovered ? '#0a0d14' : '#fff',
                        fontWeight: isHovered ? 800 : 600,
                        fontSize: '0.9rem',
                        cursor: 'pointer',
                        transition: 'background-color 0.15s ease, transform 0.15s ease',
                        transform: isHovered ? 'scale(1.08)' : 'scale(1)',
                        boxShadow: isHovered ? '0 4px 14px rgba(99, 102, 241, 0.4)' : 'none',
                        userSelect: 'none',
                      }}
                    >
                      {Number.isInteger(val) ? val : val.toFixed(2)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Тултип информации о выбранной ячейке */}
      {hoveredCell && (
        <div style={{
          marginTop: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          fontSize: '0.85rem',
          color: 'var(--text-secondary)',
          background: 'rgba(99, 102, 241, 0.08)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          padding: '8px 14px',
          borderRadius: '6px',
        }}>
          <Eye size={16} color="var(--accent-primary)" />
          <span>
            Строка: <strong style={{ color: '#fff' }}>{currentMatrix.rows[hoveredCell.row]}</strong>
          </span>
          <span>•</span>
          <span>
            Столбец: <strong style={{ color: '#fff' }}>{currentMatrix.cols[hoveredCell.col]}</strong>
          </span>
          <span>•</span>
          <span>
            Значение: <strong style={{ color: '#34d399', fontSize: '1rem' }}>
              {currentMatrix.data[hoveredCell.row][hoveredCell.col]}
            </strong>
          </span>
        </div>
      )}
    </div>
  );
};
