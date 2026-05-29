import React from 'react';
import type { ContractChangeOutput } from '../types';

interface ResultsPanelProps {
  result: ContractChangeOutput;
  onReset: () => void;
}

function formatText(text: string): React.ReactNode[] {
  // Split by **bold** regex
  const parts = text.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={index} className="font-semibold text-slate-900">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return part;
  });
}

function renderSummary(text: string) {
  if (!text) return null;

  // Split by newlines, trim, and ignore empty lines
  const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
  
  const elements: React.ReactNode[] = [];
  let currentList: { type: 'ul' | 'ol'; items: string[] } | null = null;
  
  const flushList = (key: number) => {
    if (currentList) {
      if (currentList.type === 'ol') {
        elements.push(
          <ol key={`list-${key}`} className="mt-3 list-decimal pl-5 space-y-2 text-slate-800">
            {currentList.items.map((item, idx) => (
              <li key={idx} className="pl-1 leading-relaxed">
                {formatText(item)}
              </li>
            ))}
          </ol>
        );
      } else {
        elements.push(
          <ul key={`list-${key}`} className="mt-3 list-disc pl-5 space-y-2 text-slate-800">
            {currentList.items.map((item, idx) => (
              <li key={idx} className="pl-1 leading-relaxed">
                {formatText(item)}
              </li>
            ))}
          </ul>
        );
      }
      currentList = null;
    }
  };

  lines.forEach((line, index) => {
    const olMatch = line.match(/^(\d+)[\.\)\-]\s*(.*)$/);
    const ulMatch = line.match(/^[\-\*\u2022]\s*(.*)$/);

    if (olMatch) {
      if (currentList && currentList.type !== 'ol') {
        flushList(index);
      }
      if (!currentList) {
        currentList = { type: 'ol', items: [] };
      }
      currentList.items.push(olMatch[2]);
    } else if (ulMatch) {
      if (currentList && currentList.type !== 'ul') {
        flushList(index);
      }
      if (!currentList) {
        currentList = { type: 'ul', items: [] };
      }
      currentList.items.push(ulMatch[2]);
    } else {
      flushList(index);
      elements.push(
        <p key={`p-${index}`} className="mt-3 leading-relaxed text-slate-800">
          {formatText(line)}
        </p>
      );
    }
  });
  
  flushList(lines.length);
  return elements;
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
        {renderSummary(result.summary_of_the_change)}
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
