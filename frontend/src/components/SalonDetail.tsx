import { ExternalLink, Globe, MapPin, Pencil, Phone, Save, Star, X } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";
import type { SalonDetail, SalonUpdatePayload } from "../types/salon";
import { displayRating, displayReviews, displayValue } from "../utils/format";

interface SalonDetailProps {
  detail: SalonDetail | null;
  districts: string[];
  loading: boolean;
  saving: boolean;
  saveMessage: string | null;
  error: string | null;
  onSave: (payload: SalonUpdatePayload) => Promise<void>;
}

export default function SalonDetailPanel({
  detail,
  districts,
  loading,
  saving,
  saveMessage,
  error,
  onSave
}: SalonDetailProps) {
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<FormState>(() => toFormState(detail));

  useEffect(() => {
    setForm(toFormState(detail));
    setEditing(false);
  }, [detail?.id]);

  const districtOptions = useMemo(() => {
    const values = new Set(districts);
    if (detail?.district) {
      values.add(detail.district);
    }
    return Array.from(values).sort();
  }, [detail?.district, districts]);

  if (loading) {
    return <div className="detail-panel muted-panel">Loading salon details...</div>;
  }

  if (error) {
    return <div className="detail-panel error-panel">{error}</div>;
  }

  if (!detail) {
    return <div className="detail-panel muted-panel">Select a salon to view details.</div>;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSave({
      name: form.name.trim(),
      address: form.address.trim(),
      district: form.district.trim(),
      phone: form.phone.trim(),
      website: form.website.trim(),
      services: form.services.trim(),
      priceRange: form.priceRange.trim(),
      rating: form.rating === "" ? undefined : Number(form.rating),
      reviewsCount: form.reviewsCount === "" ? undefined : Number(form.reviewsCount)
    });
    setEditing(false);
  }

  return (
    <section className="detail-panel" aria-label="Salon details">
      <div className="detail-heading">
        <div>
          <p className="eyebrow">{displayValue(detail.district)}</p>
          <h2>{detail.name}</h2>
        </div>
        {editing ? (
          <button className="icon-button" type="button" onClick={() => setEditing(false)} title="Cancel edit">
            <X size={18} aria-hidden="true" />
          </button>
        ) : (
          <button className="action-button" type="button" onClick={() => setEditing(true)} title="Edit salon">
            <Pencil size={17} aria-hidden="true" />
            Edit
          </button>
        )}
      </div>

      {editing ? (
        <form className="edit-form" onSubmit={handleSubmit}>
          <label>
            Name
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
          </label>
          <label>
            Address
            <input value={form.address} onChange={(event) => setForm({ ...form, address: event.target.value })} />
          </label>
          <label>
            District
            <select value={form.district} onChange={(event) => setForm({ ...form, district: event.target.value })}>
              <option value="">Unknown</option>
              {districtOptions.map((district) => (
                <option key={district} value={district}>
                  {district}
                </option>
              ))}
            </select>
          </label>
          <label>
            Phone
            <input value={form.phone} onChange={(event) => setForm({ ...form, phone: event.target.value })} />
          </label>
          <label>
            Website
            <input value={form.website} onChange={(event) => setForm({ ...form, website: event.target.value })} />
          </label>
          <label>
            Services
            <textarea value={form.services} onChange={(event) => setForm({ ...form, services: event.target.value })} />
          </label>
          <div className="form-grid">
            <label>
              Price
              <input
                value={form.priceRange}
                onChange={(event) => setForm({ ...form, priceRange: event.target.value })}
              />
            </label>
            <label>
              Rating
              <input
                max="5"
                min="0"
                step="0.1"
                type="number"
                value={form.rating}
                onChange={(event) => setForm({ ...form, rating: event.target.value })}
              />
            </label>
            <label>
              Reviews
              <input
                min="0"
                step="1"
                type="number"
                value={form.reviewsCount}
                onChange={(event) => setForm({ ...form, reviewsCount: event.target.value })}
              />
            </label>
          </div>
          <button className="save-button" type="submit" disabled={saving} title="Save changes">
            <Save size={17} aria-hidden="true" />
            {saving ? "Saving..." : "Save"}
          </button>
        </form>
      ) : (
        <>
          <div className="quick-stats">
            <span>
              <Star size={16} aria-hidden="true" />
              {displayRating(detail.rating)}
            </span>
            <span>{displayReviews(detail.reviewsCount)}</span>
            <span>{displayValue(detail.priceRange)}</span>
          </div>

          <dl className="detail-list">
            <div>
              <dt>
                <MapPin size={16} aria-hidden="true" />
                Address
              </dt>
              <dd>{displayValue(detail.address)}</dd>
            </div>
            <div>
              <dt>
                <Phone size={16} aria-hidden="true" />
                Phone
              </dt>
              <dd>{displayValue(detail.phone)}</dd>
            </div>
            <div>
              <dt>
                <Globe size={16} aria-hidden="true" />
                Website
              </dt>
              <dd>
                {detail.website ? (
                  <a href={detail.website} target="_blank" rel="noreferrer">
                    {detail.website}
                  </a>
                ) : (
                  "Unknown"
                )}
              </dd>
            </div>
            <div>
              <dt>Services</dt>
              <dd>{displayValue(detail.services)}</dd>
            </div>
            <div>
              <dt>Opening hours</dt>
              <dd>{displayValue(detail.openingHours)}</dd>
            </div>
            <div>
              <dt>Coordinates</dt>
              <dd>
                {detail.latitude && detail.longitude
                  ? `${detail.latitude.toFixed(5)}, ${detail.longitude.toFixed(5)}`
                  : "Unknown"}
              </dd>
            </div>
            <div>
              <dt>Source</dt>
              <dd>
                {detail.sourceUrl ? (
                  <a href={detail.sourceUrl} target="_blank" rel="noreferrer">
                    OpenStreetMap <ExternalLink size={14} aria-hidden="true" />
                  </a>
                ) : (
                  displayValue(detail.source)
                )}
              </dd>
            </div>
          </dl>
        </>
      )}

      {saveMessage ? <p className="save-message">{saveMessage}</p> : null}
    </section>
  );
}

interface FormState {
  name: string;
  address: string;
  district: string;
  phone: string;
  website: string;
  services: string;
  priceRange: string;
  rating: string;
  reviewsCount: string;
}

function toFormState(detail: SalonDetail | null): FormState {
  return {
    name: detail?.name ?? "",
    address: detail?.address ?? "",
    district: detail?.district ?? "",
    phone: detail?.phone ?? "",
    website: detail?.website ?? "",
    services: detail?.services ?? "",
    priceRange: detail?.priceRange ?? "",
    rating: detail?.rating?.toString() ?? "",
    reviewsCount: detail?.reviewsCount?.toString() ?? ""
  };
}
