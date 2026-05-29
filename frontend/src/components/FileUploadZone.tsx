import { useCallback, useRef, useState } from 'react';

const ACCEPTED = '.jpg,.jpeg,.png';

interface FileUploadZoneProps {
  label: string;
  description: string;
  variant: 'original' | 'amendment';
  file: File | null;
  onFileChange: (file: File | null) => void;
  disabled?: boolean;
}

export function FileUploadZone({
  label,
  description,
  variant,
  file,
  onFileChange,
  disabled = false,
}: FileUploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  const isAmendment = variant === 'amendment';

  const handleFiles = useCallback(
    (files: FileList | null) => {
      if (!files?.length) return;
      onFileChange(files[0]);
    },
    [onFileChange],
  );

  const borderClass = isAmendment
    ? 'border-dashed border-amber-300'
    : 'border-solid border-indigo-200';

  const activeBorder = isDragging
    ? isAmendment
      ? 'border-amber-500 bg-amber-50/50'
      : 'border-indigo-500 bg-indigo-50/50'
    : borderClass;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <h3 className="font-medium text-slate-900">{label}</h3>
        {isAmendment && (
          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
            Enmienda
          </span>
        )}
      </div>
      <p className="text-sm text-slate-500">{description}</p>

      <div
        role="button"
        tabIndex={disabled ? -1 : 0}
        onKeyDown={(e) => {
          if (!disabled && (e.key === 'Enter' || e.key === ' ')) {
            e.preventDefault();
            inputRef.current?.click();
          }
        }}
        onClick={() => !disabled && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          if (!disabled) handleFiles(e.dataTransfer.files);
        }}
        className={`relative flex min-h-[160px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 bg-white p-6 transition-colors ${activeBorder} ${disabled ? 'cursor-not-allowed opacity-60' : 'hover:border-indigo-300'}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          className="hidden"
          disabled={disabled}
          onChange={(e) => handleFiles(e.target.files)}
        />

        {file ? (
          <div className="flex flex-col items-center gap-2 text-center">
            <DocumentIcon className="h-10 w-10 text-indigo-500" />
            <p className="max-w-full truncate px-2 text-sm font-medium text-slate-800">
              {file.name}
            </p>
            <p className="text-xs text-slate-500">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onFileChange(null);
                if (inputRef.current) inputRef.current.value = '';
              }}
              className="mt-1 text-xs text-slate-500 underline hover:text-slate-800"
              disabled={disabled}
            >
              Quitar archivo
            </button>
          </div>
        ) : (
          <>
            <DocumentIcon
              className={`h-10 w-10 ${isAmendment ? 'text-amber-500' : 'text-indigo-400'}`}
            />
            <p className="mt-3 text-sm font-medium text-slate-700">
              Arrastra una imagen o haz clic para seleccionar
            </p>
            <p className="mt-1 text-xs text-slate-400">JPG, JPEG o PNG · máx. 10 MB</p>
          </>
        )}
      </div>
    </div>
  );
}

function DocumentIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
      />
    </svg>
  );
}
