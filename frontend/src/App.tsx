import React, { useEffect, useState } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardOverview } from './components/DashboardOverview';
import { DataInputSection } from './components/DataInputSection';
import { RankingCharts } from './components/RankingCharts';
import { InteractiveMatrix } from './components/InteractiveMatrix';
import { KemenyComparison } from './components/KemenyComparison';
import { ExpertGraph } from './components/ExpertGraph';
import { fetchHealth, fetchExamples, analyzeText, analyzeFile } from './api/client';
import type { AnalyzeResponse, ExamplesResponse } from './types/api';
import { AlertCircle, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [examples, setExamples] = useState<ExamplesResponse | null>(null);
  const [analysisData, setAnalysisData] = useState<AnalyzeResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Инициализация при монтировании
  useEffect(() => {
    const init = async () => {
      try {
        await fetchHealth();
        setApiStatus('connected');
      } catch (e) {
        setApiStatus('error');
      }

      try {
        const ex = await fetchExamples();
        setExamples(ex);
      } catch (e) {
        console.warn('Could not load examples', e);
      }

      // Выполняем первоначальный анализ данных по умолчанию
      try {
        setIsLoading(true);
        const initialRes = await analyzeText('a5 a1 a2 a3 a4\na4 a3 a2 a1 a5\na3 a5 a4 a2 a1\na3 a4 a5 a1 a2\na5 a1 a2 a3 a4\na4 a2 a5 a1 a3');
        setAnalysisData(initialRes);
        setApiStatus('connected');
      } catch (err: any) {
        setError(err.message || 'Ошибка подключения к серверу API');
      } finally {
        setIsLoading(false);
      }
    };

    init();
  }, []);

  const handleAnalyzeText = async (text: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await analyzeText(text);
      setAnalysisData(res);
      setApiStatus('connected');
    } catch (err: any) {
      setError(err.message || 'Не удалось выполнить анализ');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAnalyzeFile = async (file: File) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await analyzeFile(file);
      setAnalysisData(res);
      setApiStatus('connected');
    } catch (err: any) {
      setError(err.message || 'Не удалось обработать загруженный файл');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar apiStatus={apiStatus} />

      <main style={{ maxWidth: '1280px', margin: '0 auto', width: '100%', padding: '28px 24px', flex: 1 }}>
        {/* Баннер ошибки API */}
        {apiStatus === 'error' && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: '10px',
            padding: '14px 18px',
            marginBottom: '24px',
            color: '#fca5a5',
          }}>
            <AlertCircle size={20} color="#ef4444" />
            <div>
              <strong style={{ color: '#fff' }}>Сервер FastAPI недоступен.</strong> Убедитесь, что backend запущен командой:{' '}
              <code style={{ background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px' }}>
                uvicorn api.main:app --reload
              </code>
            </div>
          </div>
        )}

        {/* Секция ввода данных */}
        <DataInputSection
          examples={examples}
          onAnalyzeText={handleAnalyzeText}
          onAnalyzeFile={handleAnalyzeFile}
          isLoading={isLoading}
          error={error}
        />

        {/* Результаты анализа */}
        {analysisData ? (
          <div className="animate-fade-in">
            {/* KPI Дашборд */}
            <DashboardOverview
              summary={analysisData.summary}
              allAgree={analysisData.comparison.all_methods_agree}
            />

            {/* Итоговые ранжирования (горизонтальный bar chart) */}
            <RankingCharts
              rankings={analysisData.rankings}
              kemenyBruteforce={analysisData.kemeny.bruteforce_method}
            />

            {/* Сравнение трёх методов Кемени */}
            <KemenyComparison
              expertMethod={analysisData.kemeny.expert_method}
              assignmentMethod={analysisData.kemeny.assignment_method}
              bruteforceMethod={analysisData.kemeny.bruteforce_method}
              comparison={analysisData.comparison}
            />

            {/* Граф экспертов */}
            <ExpertGraph graph={analysisData.graph} />

            {/* Интерактивные матрицы (Heatmap) */}
            <InteractiveMatrix
              matrices={analysisData.matrices}
              binaryRelations={analysisData.binary_relations}
              diffMatrices={analysisData.diff_matrices}
            />
          </div>
        ) : isLoading ? (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '60px',
            color: 'var(--text-secondary)',
          }}>
            <RefreshCw size={36} className="animate-spin" color="var(--accent-primary)" style={{ marginBottom: '16px' }} />
            <div style={{ fontSize: '1.1rem', fontWeight: 600 }}>Вычисление математических методов...</div>
          </div>
        ) : null}
      </main>

      <footer style={{
        textAlign: 'center',
        padding: '24px',
        borderTop: '1px solid var(--border-subtle)',
        color: 'var(--text-muted)',
        fontSize: '0.8rem',
      }}>
        ММАСС • Лабораторная работа №1 «Методы экспертных оценок» • Python Core + FastAPI + React
      </footer>
    </div>
  );
};

export default App;
