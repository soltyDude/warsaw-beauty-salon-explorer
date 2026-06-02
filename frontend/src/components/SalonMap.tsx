import type { SalonDetail, SalonListItem } from "../types/salon";

const BOUNDS = {
  south: 52.097,
  west: 20.851,
  north: 52.368,
  east: 21.271
};

interface SalonMapProps {
  salons: SalonListItem[];
  detail: SalonDetail | null;
  onSelect: (id: number) => void;
}

export default function SalonMap({ salons, detail, onSelect }: SalonMapProps) {
  const visible = salons.slice(0, 260);

  return (
    <div className="map-panel" aria-label="Salon coordinate plot">
      <div className="map-grid" />
      {visible.map((salon) => {
        const active = salon.id === detail?.id;
        const position = positionFromSalon(active && detail ? detail : salon);
        if (!position) {
          return null;
        }
        return (
          <button
            key={salon.id}
            className={`map-pin ${active ? "is-active" : ""}`}
            style={{ left: `${position.x}%`, top: `${position.y}%` }}
            type="button"
            title={salon.name}
            onClick={() => onSelect(salon.id)}
          />
        );
      })}
      {detail && positionFromSalon(detail) ? (
        <div
          className="map-label"
          style={{
            left: `${positionFromSalon(detail)!.x}%`,
            top: `${positionFromSalon(detail)!.y}%`
          }}
        >
          {detail.district ?? "Unknown"}
        </div>
      ) : null}
    </div>
  );
}

function positionFromSalon(salon: Pick<SalonDetail, "latitude" | "longitude"> | null) {
  if (!salon || salon.latitude === null || salon.longitude === null) {
    return null;
  }
  const x = ((salon.longitude - BOUNDS.west) / (BOUNDS.east - BOUNDS.west)) * 100;
  const y = 100 - ((salon.latitude - BOUNDS.south) / (BOUNDS.north - BOUNDS.south)) * 100;
  return {
    x: Math.min(98, Math.max(2, x)),
    y: Math.min(98, Math.max(2, y))
  };
}
