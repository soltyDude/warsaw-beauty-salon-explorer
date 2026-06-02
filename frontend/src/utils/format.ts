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
