import type { ContractChangeOutput } from '../types';

interface ResultsPanelProps {
  result: ContractChangeOutput;
  onReset: () => void;
}

export function ResultsPanel({ result, onReset }: ResultsPanelProps) {
  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-slate-900">Resultado del análisis</h2>
        <button
          type="button"
          onClick={onReset}
          className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
        >
          Nuevo análisis
        </button>
      </div>

      <div className="rounded-xl border border-indigo-100 bg-indigo-50/40 p-6">
        <h3 className="text-sm font-medium tracking-wide text-indigo-700 uppercase">
          Resumen ejecutivo
        </h3>
        <p className="mt-3 leading-relaxed text-slate-800">
          {result.summary_of_the_change}
        </p>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-sm font-medium text-slate-700">Secciones modificadas</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {result.sections_changed.map((section) => (
            <span
              key={section}
              className="rounded-full bg-slate-100 px-3 py-1 text-sm text-slate-700"
            >
              {section}
            </span>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-sm font-medium text-slate-700">Temas afectados</h3>
        <div className="mt-3 flex flex-wrap gap-2">
          {result.topics_touched.map((topic) => (
            <span
              key={topic}
              className="rounded-full bg-indigo-100 px-3 py-1 text-sm text-indigo-800"
            >
              {topic}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
