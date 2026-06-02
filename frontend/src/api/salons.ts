import type {
  SalonDetail,
  SalonListItem,
  SalonStats,
  SalonUpdatePayload
} from "../types/salon";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export async function fetchSalons(district?: string): Promise<SalonListItem[]> {
  const query = district ? `?district=${encodeURIComponent(district)}` : "";
  return request<SalonListItem[]>(`/api/salons${query}`);
}

export async function fetchDistricts(): Promise<string[]> {
  return request<string[]>("/api/districts");
}

export async function fetchSalonDetail(id: number): Promise<SalonDetail> {
  return request<SalonDetail>(`/api/salons/${id}`);
}

export async function updateSalon(id: number, payload: SalonUpdatePayload): Promise<SalonDetail> {
  return request<SalonDetail>(`/api/salons/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const message = await readError(response);
    throw new Error(message || `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

async function readError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.message === "string") {
      return body.message;
    }
  } catch {
    return response.statusText;
  }
  return response.statusText;
}

export async function fetchStats(): Promise<SalonStats> {
  return request<SalonStats>("/api/stats");
}


