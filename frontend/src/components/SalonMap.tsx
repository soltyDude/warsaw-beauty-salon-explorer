import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import type { SalonDetail, SalonListItem } from "../types/salon";

interface SalonMapProps {
  salons: SalonListItem[];
  detail: SalonDetail | null;
  onSelect: (id: number) => void;
}

const WARSAW_CENTER: [number, number] = [52.2297, 21.0122];

export default function SalonMap({
  salons,
  detail,
  onSelect
}: SalonMapProps) {
  const visible = salons
    .filter(
      (salon) =>
        salon.latitude !== null &&
        salon.longitude !== null
    )
    .slice(0, 500);

  return (
    <div className="map-panel">
      <MapContainer
        center={WARSAW_CENTER}
        zoom={11}
        scrollWheelZoom
        style={{
          height: "100%",
          width: "100%"
        }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {visible.map((salon) => (
          <Marker
            key={salon.id}
            position={[
              salon.latitude!,
              salon.longitude!
            ]}
            eventHandlers={{
              click: () => onSelect(salon.id)
            }}
          >
            <Popup>
              <strong>{salon.name}</strong>
              <br />
              {salon.district}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}