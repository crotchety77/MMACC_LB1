import React, { useState } from 'react';
import { Share2, Crown, Eye } from 'lucide-react';
import type { ExpertGraphData, ExpertGraphNode, ExpertGraphEdge } from '../types/api';

interface ExpertGraphProps {
  graph: ExpertGraphData;
}

export const ExpertGraph: React.FC<ExpertGraphProps> = ({ graph }) => {
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [hoveredNode, setHoveredNode] = useState<ExpertGraphNode | null>(null);
  const [hoveredEdge, setHoveredEdge] = useState<ExpertGraphEdge | null>(null);

  // Центр и радиус кругового расположения вершин графа
  const width = 640;
  const height = 480;
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = 170;

  const nodeCount = graph.nodes.length;
  // Рассчитываем координаты вершин
  const nodePositions = new Map<string, { x: number; y: number }>();
  graph.nodes.forEach((node, idx) => {
    const angle = (idx * 2 * Math.PI) / nodeCount - Math.PI / 2;
    const x = centerX + radius * Math.cos(angle);
    const y = centerY + radius * Math.sin(angle);
    nodePositions.set(node.id, { x, y });
  });

  return (
    <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
        flexWrap: 'wrap',
        gap: '12px',
      }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Share2 size={20} color="var(--accent-primary)" />
            Граф близости экспертов (Расстояния Кемени)
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Вершины — эксперты, рёбра — реальные попарные расстояния Кемени $d(E_i, E_j)$. Толстые и яркие связи обозначают высокое согласие.
          </p>
        </div>

        {selectedNode && (
          <button
            onClick={() => setSelectedNode(null)}
            className="btn btn-secondary"
            style={{ padding: '4px 12px', fontSize: '0.75rem' }}
          >
            Сбросить выделение
          </button>
        )}
      </div>

      <div style={{
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        background: 'rgba(10, 13, 20, 0.4)',
        borderRadius: '12px',
        border: '1px solid var(--border-subtle)',
        padding: '16px',
      }}>
        <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: 'visible' }}>
          <defs>
            <radialGradient id="nodeGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#6366f1" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="medianGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#10b981" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
            </radialGradient>
          </defs>

          {/* Отрисовка рёбер */}
          {graph.edges.map((edge, idx) => {
            const posA = nodePositions.get(edge.source);
            const posB = nodePositions.get(edge.target);
            if (!posA || !posB) return null;

            const isRelatedToSelected = selectedNode ? (edge.source === selectedNode || edge.target === selectedNode) : true;
            const isHovered = hoveredEdge === edge;

            // Цветовая гамма ребра: чем меньше расстояние (выше similarity), тем ярче бирюзовый/индиго
            const strokeColor = edge.distance === 0
              ? '#10b981' // Идеальное совпадение
              : isHovered
              ? '#38bdf8'
              : isRelatedToSelected
              ? `rgba(99, 102, 241, ${0.15 + edge.similarity * 0.7})`
              : 'rgba(255, 255, 255, 0.05)';

            const strokeWidth = isHovered ? 4 : isRelatedToSelected ? 1 + edge.similarity * 3.5 : 1;

            return (
              <g key={`edge-${idx}`}>
                <line
                  x1={posA.x}
                  y1={posA.y}
                  x2={posB.x}
                  y2={posB.y}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  strokeLinecap="round"
                  style={{ cursor: 'pointer', transition: 'stroke 0.2s, stroke-width 0.2s' }}
                  onMouseEnter={() => setHoveredEdge(edge)}
                  onMouseLeave={() => setHoveredEdge(null)}
                />
                {/* Метка расстояния по центру ребра при ховере */}
                {isHovered && (
                  <g transform={`translate(${(posA.x + posB.x) / 2}, ${(posA.y + posB.y) / 2})`}>
                    <rect
                      x="-28"
                      y="-14"
                      width="56"
                      height="28"
                      rx="6"
                      fill="#0f172a"
                      stroke="#38bdf8"
                      strokeWidth="1.5"
                    />
                    <text
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill="#38bdf8"
                      fontSize="12"
                      fontWeight="bold"
                    >
                      d = {edge.distance}
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* Отрисовка вершин (экспертов) */}
          {graph.nodes.map((node) => {
            const pos = nodePositions.get(node.id);
            if (!pos) return null;

            const isSelected = selectedNode === node.id;
            const isHovered = hoveredNode?.id === node.id;
            const isMedian = node.is_median;

            return (
              <g
                key={node.id}
                transform={`translate(${pos.x}, ${pos.y})`}
                style={{ cursor: 'pointer' }}
                onClick={() => setSelectedNode(isSelected ? null : node.id)}
                onMouseEnter={() => setHoveredNode(node)}
                onMouseLeave={() => setHoveredNode(null)}
              >
                {/* Фоновое свечение */}
                <circle
                  r={isMedian ? (isHovered ? 40 : 36) : (isHovered ? 32 : 28)}
                  fill={isMedian ? 'url(#medianGlow)' : 'url(#nodeGlow)'}
                />

                {/* Основной круг вершины */}
                <circle
                  r={isHovered ? 25 : 22}
                  fill={isSelected ? '#6366f1' : isMedian ? '#065f46' : '#1e293b'}
                  stroke={isMedian ? '#34d399' : isSelected || isHovered ? '#a5b4fc' : '#475569'}
                  strokeWidth={isMedian ? 2.5 : isSelected || isHovered ? 3 : 1.5}
                  style={{ transition: 'all 0.2s ease' }}
                />

                {/* Текст эксперта */}
                <text
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="#ffffff"
                  fontSize="13"
                  fontWeight="800"
                >
                  {node.id}
                </text>

                {/* Иконка медианы */}
                {isMedian && (
                  <g transform="translate(10, -22)">
                    <circle r="9" fill="#10b981" />
                    <text
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fill="#ffffff"
                      fontSize="10"
                      fontWeight="bold"
                    >
                      ★
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>

        {/* Плавающая панель информации о выбранном или наведённом эксперте */}
        {(hoveredNode || selectedNode) && (
          <div style={{
            marginTop: '12px',
            width: '100%',
            maxWidth: '560px',
            background: 'rgba(15, 23, 42, 0.95)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            borderRadius: '10px',
            padding: '12px 18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
          }}>
            {(() => {
              const activeNode = hoveredNode || graph.nodes.find(n => n.id === selectedNode);
              if (!activeNode) return null;
              return (
                <>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                      <span style={{ fontWeight: 800, fontSize: '1rem', color: '#fff' }}>
                        {activeNode.label}
                      </span>
                      {activeNode.is_median && (
                        <span className="badge badge-emerald" style={{ padding: '2px 8px', fontSize: '0.7rem' }}>
                          <Crown size={12} /> Медиана Кемени
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#a5b4fc', fontFamily: 'monospace' }}>
                      Ранжировка: {activeNode.ranking_str}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Сумма расстояний S(D)
                    </div>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: activeNode.is_median ? '#34d399' : '#fff' }}>
                      {activeNode.sum_distance}
                    </div>
                  </div>
                </>
              );
            })()}
          </div>
        )}

        {/* Тултип ребра при наведении */}
        {hoveredEdge && (
          <div style={{
            marginTop: '8px',
            fontSize: '0.85rem',
            color: 'var(--text-secondary)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <Eye size={14} color="#38bdf8" />
            <span>
              Расстояние Кемени между <strong style={{ color: '#fff' }}>{hoveredEdge.source}</strong> и{' '}
              <strong style={{ color: '#fff' }}>{hoveredEdge.target}</strong>:{' '}
              <strong style={{ color: '#38bdf8' }}>{hoveredEdge.distance}</strong> (Сходство: {(hoveredEdge.similarity * 100).toFixed(0)}%)
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
