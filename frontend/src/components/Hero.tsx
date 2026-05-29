const STEPS = [
  {
    step: '1',
    title: 'Transcripción',
    description: 'GPT-4o Vision lee las imágenes del contrato original y la enmienda.',
  },
  {
    step: '2',
    title: 'Alineación',
    description: 'Un agente mapea las cláusulas entre ambos documentos.',
  },
  {
    step: '3',
    title: 'Extracción',
    description: 'Se identifican secciones modificadas y temas legales afectados.',
  },
  {
    step: '4',
    title: 'Reporte',
    description: 'Recibes un resumen ejecutivo estructurado en español.',
  },
];

export function Hero() {
  return (
    <header className="mx-auto max-w-3xl text-center">
      <p className="mb-3 text-sm font-medium tracking-wide text-indigo-600 uppercase">
        LegalTech · Compliance automatizado
      </p>
      <h1 className="text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
        LegalMove AI
      </h1>
      <p className="mt-4 text-lg leading-relaxed text-slate-600">
        Compara contratos originales con sus enmiendas o adendas. El equipo de
        Compliance dedica más de 40 horas semanales a esta tarea manual; este
        sistema automatiza la extracción de cambios con agentes de IA.
      </p>

      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        {STEPS.map((item) => (
          <div
            key={item.step}
            className="rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm"
          >
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
              {item.step}
            </span>
            <h2 className="mt-3 font-medium text-slate-900">{item.title}</h2>
            <p className="mt-1 text-sm leading-relaxed text-slate-500">
              {item.description}
            </p>
          </div>
        ))}
      </div>
    </header>
  );
}
