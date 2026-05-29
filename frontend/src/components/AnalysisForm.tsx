import { FileUploadZone } from './FileUploadZone';

interface AnalysisFormProps {
  originalFile: File | null;
  amendmentFile: File | null;
  onOriginalChange: (file: File | null) => void;
  onAmendmentChange: (file: File | null) => void;
  onSubmit: () => void;
  disabled?: boolean;
}

export function AnalysisForm({
  originalFile,
  amendmentFile,
  onOriginalChange,
  onAmendmentChange,
  onSubmit,
  disabled = false,
}: AnalysisFormProps) {
  const canSubmit = Boolean(originalFile && amendmentFile) && !disabled;

  return (
    <section className="space-y-8">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">Cargar documentos</h2>
        <p className="mt-2 text-sm text-slate-500">
          Sube las imágenes escaneadas por separado para identificar claramente cada
          tipo de documento.
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-2">
        <FileUploadZone
          label="Contrato original"
          description="Imagen del contrato base antes de cualquier modificación."
          variant="original"
          file={originalFile}
          onFileChange={onOriginalChange}
          disabled={disabled}
        />
        <FileUploadZone
          label="Enmienda / adenda"
          description="Imagen del documento que modifica o complementa el contrato."
          variant="amendment"
          file={amendmentFile}
          onFileChange={onAmendmentChange}
          disabled={disabled}
        />
      </div>

      <button
        type="button"
        onClick={onSubmit}
        disabled={!canSubmit}
        className="w-full rounded-xl bg-indigo-600 px-6 py-3.5 text-base font-medium text-white shadow-sm transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none sm:w-auto sm:min-w-[220px]"
      >
        Analizar cambios
      </button>
    </section>
  );
}
