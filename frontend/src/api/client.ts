import type { ContractChangeOutput } from '../types';

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function analyzeContracts(
  original: File,
  amendment: File,
): Promise<ContractChangeOutput> {
  const formData = new FormData();
  formData.append('original', original);
  formData.append('amendment', amendment);

  const response = await fetch('/api/analyze', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    let message = 'Error al analizar los contratos.';
    try {
      const body = await response.json();
      if (typeof body.detail === 'string') {
        message = body.detail;
      } else if (Array.isArray(body.detail)) {
        message = body.detail.map((d: { msg?: string }) => d.msg).filter(Boolean).join(' ');
      }
    } catch {
      // use default message
    }
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<ContractChangeOutput>;
}
