export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-slate-200 bg-white py-16 shadow-sm">
      <div
        className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-200 border-t-indigo-600"
        role="status"
        aria-label="Cargando"
      />
      <p className="mt-6 text-base font-medium text-slate-800">
        Analizando contratos…
      </p>
      <p className="mt-2 max-w-sm text-center text-sm text-slate-500">
        Transcripción, alineación y extracción con GPT-4o. Esto puede tardar
        unos 20 segundos.
      </p>
    </div>
  );
}
