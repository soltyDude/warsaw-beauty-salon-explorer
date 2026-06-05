import { MapPin, Star } from "lucide-react";
import type { SalonListItem } from "../types/salon";
import {
  displayRating,
  displayValue,
  getCompletenessScore
} from "../utils/format";

interface SalonListProps {
  salons: SalonListItem[];
  selectedId: number | null;
  onSelect: (id: number) => void;
}

export default function SalonList({ salons, selectedId, onSelect }: SalonListProps) {
  if (salons.length === 0) {
    return <div className="empty-state">No salons match the current filters.</div>;
  }

  return (
    <ul className="salon-list">
      {salons.map((salon) => (
        <li key={salon.id}>
          <button
            className={`salon-row ${selectedId === salon.id ? "is-selected" : ""}`}
            type="button"
            onClick={() => onSelect(salon.id)}
            title={`Open ${salon.name}`}
          >
            <span className="salon-row-main">
              <strong>{salon.name}</strong>

              <span className="completeness-badge">
                {getCompletenessScore(salon)}/10 filled
              </span>

              {salon.services ? (
                <span className="service-tag">
                  {salon.services.split(";")[0].trim()}
                </span>
              ) : null}

              <span className="salon-row-meta">
                <MapPin size={15} aria-hidden="true" />
                {displayValue(salon.district)}
              </span>
            </span>
            <span className="salon-row-side">
              <span>
                <Star size={15} aria-hidden="true" />
                {displayRating(salon.rating)}
              </span>
              <span>
                {salon.reviewsCount
                  ? `${salon.reviewsCount} reviews`
                  : "No reviews"}
              </span>
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
