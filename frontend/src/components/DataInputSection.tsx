import React, { useState, useRef } from 'react';
import { Upload, Play, FileText, Sparkles, RefreshCw, Plus, Trash2, ArrowLeft, ArrowRight } from 'lucide-react';
import type { ExamplesResponse } from '../types/api';

interface DataInputSectionProps {
  examples: ExamplesResponse | null;
  onAnalyzeText: (text: string) => Promise<void>;
  onAnalyzeFile: (file: File) => Promise<void>;
  isLoading: boolean;
  error: string | null;
}

export const DataInputSection: React.FC<DataInputSectionProps> = ({
  examples,
  onAnalyzeText,
  onAnalyzeFile,
  isLoading,
  error,
}) => {
  const [inputText, setInputText] = useState<string>(
    examples?.examples['default']?.content || 'a5 a1 a2 a3 a4\na4 a3 a2 a1 a5\na3 a5 a4 a2 a1\na3 a4 a5 a1 a2\na5 a1 a2 a3 a4\na4 a2 a5 a1 a3'
  );
  const [mode, setMode] = useState<'text' | 'visual'>('text');
  const [dragActive, setDragActive] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Для визуального редактора парсим строки
  const parseLines = (text: string): string[][] => {
    return text
      .split('\n')
      .map(line => line.trim().split(/\s+/).filter(Boolean))
      .filter(arr => arr.length > 0);
  };

  const [visualRankings, setVisualRankings] = useState<string[][]>(() => parseLines(inputText));

  const handleModeSwitch = (newMode: 'text' | 'visual') => {
    if (newMode === 'visual') {
      setVisualRankings(parseLines(inputText));
    } else {
      setInputText(visualRankings.map(r => r.join(' ')).join('\n'));
    }
    setMode(newMode);
  };

  const handleApplyExample = (key: string) => {
    if (examples?.examples[key]) {
      const content = examples.examples[key].content;
      setInputText(content);
      setVisualRankings(parseLines(content));
    }
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onAnalyzeFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onAnalyzeFile(e.target.files[0]);
    }
  };

  const handleRun = () => {
    const textToSubmit = mode === 'visual'
      ? visualRankings.map(r => r.join(' ')).join('\n')
      : inputText;
    onAnalyzeText(textToSubmit);
  };

  // Визуальный редактор: перемещение элементов в строке эксперта
  const moveItem = (expertIdx: number, itemIdx: number, direction: 'left' | 'right') => {
    const newRankings = visualRankings.map((row, rIdx) => {
      if (rIdx !== expertIdx) return row;
      const copy = [...row];
      const targetIdx = direction === 'left' ? itemIdx - 1 : itemIdx + 1;
      if (targetIdx < 0 || targetIdx >= copy.length) return copy;
      const temp = copy[itemIdx];
      copy[itemIdx] = copy[targetIdx];
      copy[targetIdx] = temp;
      return copy;
    });
    setVisualRankings(newRankings);
    setInputText(newRankings.map(r => r.join(' ')).join('\n'));
  };

  const addExpert = () => {
    const objects = visualRankings[0] ? [...visualRankings[0]] : ['a1', 'a2', 'a3', 'a4', 'a5'];
    const newRankings = [...visualRankings, objects];
    setVisualRankings(newRankings);
    setInputText(newRankings.map(r => r.join(' ')).join('\n'));
  };

  const removeExpert = (index: number) => {
    if (visualRankings.length <= 1) return;
    const newRankings = visualRankings.filter((_, idx) => idx !== index);
    setVisualRankings(newRankings);
    setInputText(newRankings.map(r => r.join(' ')).join('\n'));
  };

  return (
    <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={20} color="var(--accent-primary)" />
            Входные данные экспертного опроса
          </h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Каждая строка содержит ранжирование объектов экспертом (слева направо от лучшего к худшему)
          </p>
        </div>

        {/* Переключатель режимов */}
        <div style={{
          display: 'flex',
          background: 'rgba(255, 255, 255, 0.05)',
          padding: '4px',
          borderRadius: '10px',
          border: '1px solid var(--border-subtle)',
        }}>
          <button
            onClick={() => handleModeSwitch('text')}
            style={{
              padding: '6px 14px',
              fontSize: '0.8rem',
              fontWeight: 600,
              borderRadius: '7px',
              border: 'none',
              background: mode === 'text' ? 'var(--accent-primary)' : 'transparent',
              color: mode === 'text' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            Текстовый режим
          </button>
          <button
            onClick={() => handleModeSwitch('visual')}
            style={{
              padding: '6px 14px',
              fontSize: '0.8rem',
              fontWeight: 600,
              borderRadius: '7px',
              border: 'none',
              background: mode === 'visual' ? 'var(--accent-primary)' : 'transparent',
              color: mode === 'visual' ? '#fff' : 'var(--text-secondary)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            Визуальный редактор
          </button>
        </div>
      </div>

      {/* Быстрые пресеты */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Загрузить пресет:</span>
        <button
          onClick={() => handleApplyExample('default')}
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '0.75rem' }}
        >
          <Sparkles size={14} color="var(--accent-primary)" />
          Вариант 1 (input.txt, 6 экспертов)
        </button>
        <button
          onClick={() => handleApplyExample('v2')}
          className="btn btn-secondary"
          style={{ padding: '6px 12px', fontSize: '0.75rem' }}
        >
          <Sparkles size={14} color="var(--accent-amber)" />
          Вариант 2 (input_v2.txt, 5 экспертов)
        </button>

        <div style={{ marginLeft: 'auto' }}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept=".txt"
            style={{ display: 'none' }}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="btn btn-outline"
            style={{ padding: '6px 14px', fontSize: '0.75rem' }}
          >
            <Upload size={14} />
            Загрузить .txt файл
          </button>
        </div>
      </div>

      {/* Редактор */}
      {mode === 'text' ? (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleFileDrop}
          style={{ position: 'relative' }}
        >
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={6}
            style={{
              width: '100%',
              backgroundColor: 'var(--bg-input)',
              border: `1px solid ${dragActive ? 'var(--accent-primary)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-sm)',
              padding: '14px 16px',
              color: 'var(--text-primary)',
              fontSize: '0.95rem',
              fontFamily: 'monospace',
              lineHeight: '1.6',
              resize: 'vertical',
              outline: 'none',
              transition: 'border-color 0.2s ease',
            }}
            placeholder="a5 a1 a2 a3 a4&#10;a4 a3 a2 a1 a5&#10;..."
          />
          {dragActive && (
            <div style={{
              position: 'absolute',
              inset: 0,
              background: 'rgba(99, 102, 241, 0.2)',
              borderRadius: 'var(--radius-sm)',
              border: '2px dashed var(--accent-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: '1rem',
              fontWeight: 600,
            }}>
              Перетащите файл .txt сюда
            </div>
          )}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {visualRankings.map((row, expertIdx) => (
            <div
              key={expertIdx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '10px 14px',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                overflowX: 'auto',
              }}
            >
              <span style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--accent-primary)', minWidth: '70px' }}>
                Эксперт {expertIdx + 1}:
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
                {row.map((item, itemIdx) => (
                  <div
                    key={itemIdx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '4px 8px',
                      background: 'var(--bg-input)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: '6px',
                      fontSize: '0.85rem',
                    }}
                  >
                    <button
                      disabled={itemIdx === 0}
                      onClick={() => moveItem(expertIdx, itemIdx, 'left')}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: itemIdx === 0 ? 'var(--text-muted)' : 'var(--text-secondary)',
                        cursor: itemIdx === 0 ? 'default' : 'pointer',
                        display: 'flex',
                        padding: 0,
                      }}
                    >
                      <ArrowLeft size={13} />
                    </button>
                    <span style={{ fontWeight: 700, padding: '0 4px', color: '#fff' }}>{item}</span>
                    <button
                      disabled={itemIdx === row.length - 1}
                      onClick={() => moveItem(expertIdx, itemIdx, 'right')}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: itemIdx === row.length - 1 ? 'var(--text-muted)' : 'var(--text-secondary)',
                        cursor: itemIdx === row.length - 1 ? 'default' : 'pointer',
                        display: 'flex',
                        padding: 0,
                      }}
                    >
                      <ArrowRight size={13} />
                    </button>
                  </div>
                ))}
              </div>
              <button
                onClick={() => removeExpert(expertIdx)}
                className="btn btn-outline"
                style={{ padding: '6px', color: 'var(--accent-rose)', border: 'none' }}
                title="Удалить эксперта"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginTop: '6px' }}>
            <button onClick={addExpert} className="btn btn-secondary" style={{ padding: '6px 14px', fontSize: '0.8rem' }}>
              <Plus size={14} /> Добавить эксперта
            </button>
          </div>
        </div>
      )}

      {error && (
        <div style={{
          marginTop: '14px',
          padding: '10px 14px',
          background: 'rgba(244, 63, 94, 0.1)',
          border: '1px solid rgba(244, 63, 94, 0.3)',
          borderRadius: '8px',
          color: '#fb7185',
          fontSize: '0.85rem',
        }}>
          {error}
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px' }}>
        <button
          onClick={handleRun}
          disabled={isLoading}
          className="btn btn-primary"
          style={{ padding: '10px 24px', fontSize: '0.9rem' }}
        >
          {isLoading ? (
            <>
              <RefreshCw size={16} className="animate-spin" />
              Вычисление...
            </>
          ) : (
            <>
              <Play size={16} fill="currentColor" />
              Рассчитать все методы
            </>
          )}
        </button>
      </div>
    </div>
  );
};
