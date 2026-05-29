import { useState } from 'react';
import { analyzeContracts } from './api/client';
import { AnalysisForm } from './components/AnalysisForm';
import { Hero } from './components/Hero';
import { LoadingState } from './components/LoadingState';
import { ResultsPanel } from './components/ResultsPanel';
import type { ContractChangeOutput } from './types';

type AppState = 'idle' | 'loading' | 'success' | 'error';

function App() {
  const [originalFile, setOriginalFile] = useState<File | null>(null);
  const [amendmentFile, setAmendmentFile] = useState<File | null>(null);
  const [appState, setAppState] = useState<AppState>('idle');
  const [result, setResult] = useState<ContractChangeOutput | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!originalFile || !amendmentFile) return;

    setAppState('loading');
    setErrorMessage(null);
    setResult(null);

    try {
      const data = await analyzeContracts(originalFile, amendmentFile);
      setResult(data);
      setAppState('success');
    } catch (err) {
      setAppState('error');
      setErrorMessage(
        err instanceof Error ? err.message : 'Ocurrió un error inesperado.',
      );
    }
  };

  const handleReset = () => {
    setOriginalFile(null);
    setAmendmentFile(null);
    setResult(null);
    setErrorMessage(null);
    setAppState('idle');
  };

  const isLoading = appState === 'loading';

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 sm:py-16">
        <Hero />

        <main className="mt-16 space-y-10">
          {errorMessage && (
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
            >
              {errorMessage}
            </div>
          )}

          {appState === 'success' && result ? (
            <ResultsPanel result={result} onReset={handleReset} />
          ) : (
            <>
              {isLoading ? (
                <LoadingState />
              ) : (
                <AnalysisForm
                  originalFile={originalFile}
                  amendmentFile={amendmentFile}
                  onOriginalChange={setOriginalFile}
                  onAmendmentChange={setAmendmentFile}
                  onSubmit={handleAnalyze}
                  disabled={isLoading}
                />
              )}
            </>
          )}
        </main>

        <footer className="mt-20 border-t border-slate-200 pt-8 text-center text-xs text-slate-400">
          LegalMove AI Agent · Henry AI Engineering
        </footer>
      </div>
    </div>
  );
}

export default App;
