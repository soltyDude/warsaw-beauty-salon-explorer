export interface SalonListItem {
  id: number;
  name: string;
  district: string | null;
  rating: number | null;
  priceRange: string | null;
  services: string | null;
  latitude: number | null;
  longitude: number | null;
}

export interface SalonDetail extends SalonListItem {
  address: string | null;
  phone: string | null;
  website: string | null;
  services: string | null;
  reviewsCount: number | null;
  latitude: number | null;
  longitude: number | null;
  source: string | null;
  sourceUrl: string | null;
  osmType: string | null;
  osmId: number | null;
  openingHours: string | null;
}

export interface SalonStats {
  totalSalons: number;
  districts: number;
  withPhone: number;
  withWebsite: number;
  withServices: number;
}

export type SalonUpdatePayload = Partial<
  Pick<
    SalonDetail,
    | "name"
    | "address"
    | "district"
    | "phone"
    | "website"
    | "services"
    | "priceRange"
    | "rating"
    | "reviewsCount"
  >
>;


