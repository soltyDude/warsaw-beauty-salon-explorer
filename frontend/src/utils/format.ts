export function displayValue(value: string | number | null | undefined, fallback = "Not available") {
  if (value === null || value === undefined || value === "") {
    return fallback;
  }
  return value;
}

export function displayRating(value: number | null | undefined) {
  return typeof value === "number" ? value.toFixed(1) : "No rating";
}

export function displayReviews(value: number | null | undefined) {
  return typeof value === "number" ? `${value} reviews` : "No reviews";
}

export function getCompletenessScore(salon: {
  district: string | null;
  rating: number | null;
  priceRange: string | null;
  services: string | null;
  latitude: number | null;
  longitude: number | null;
}) {
  let score = 0;

  if (salon.district) score++;
  if (salon.rating !== null) score++;
  if (salon.priceRange && salon.priceRange !== "Unknown") score++;
  if (salon.services) score++;
  if (salon.latitude !== null) score++;
  if (salon.longitude !== null) score++;

  return score;
}