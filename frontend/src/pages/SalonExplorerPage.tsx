
import { RefreshCw, Search, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchDistricts,
  fetchSalonDetail,
  fetchSalons,
  fetchStats,
  updateSalon
} from "../api/salons";
import SalonDetailPanel from "../components/SalonDetail";
import SalonList from "../components/SalonList";
import SalonMap from "../components/SalonMap";
import type { SalonDetail, SalonListItem, SalonUpdatePayload, SalonStats} from "../types/salon";



export default function SalonExplorerPage() {
  const [salons, setSalons] = useState<SalonListItem[]>([]);
  const [districts, setDistricts] = useState<string[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<SalonDetail | null>(null);
  const [district, setDistrict] = useState("");
  const [service, setService] = useState("");
  const [query, setQuery] = useState("");
  const [listLoading, setListLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [sortBy, setSortBy] = useState("nameAsc");
  const [stats, setStats] = useState<SalonStats | null>(null);
  const [listError, setListError] = useState<string | null>(null);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const loadList = useCallback(async () => {
    setListLoading(true);
    setListError(null);
    try {
      const [salonData, districtData, statsData] = await Promise.all([
        fetchSalons(district || undefined),
        fetchDistricts(),
        fetchStats()
      ]);
      setSalons(salonData);
      setDistricts(districtData);
      setStats(statsData);
    } catch (error) {
      setListError(error instanceof Error ? error.message : "Failed to load salons");
    } finally {
      setListLoading(false);
    }
  }, [district]);

  useEffect(() => {
    void loadList();
  }, [loadList]);

  const visibleSalons = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase();

    const filtered = salons.filter((salon) => {
      const matchesQuery =
        !normalizedQuery ||
        salon.name.toLocaleLowerCase().includes(normalizedQuery);

      const matchesService =
        !service ||
        salon.services?.toLocaleLowerCase().includes(service.toLocaleLowerCase());

      return matchesQuery && matchesService;
    });

    return filtered.sort((a, b) => {
      switch (sortBy) {
        case "nameDesc":
          return b.name.localeCompare(a.name);

        case "district":
          return (a.district ?? "").localeCompare(b.district ?? "");

        case "completenessDesc":
          return getCompletenessScore(b) - getCompletenessScore(a);

        case "completenessAsc":
          return getCompletenessScore(a) - getCompletenessScore(b);

        default:
          return a.name.localeCompare(b.name);
      }
    });
  }, [query, service, sortBy, salons]);

  const serviceOptions = useMemo(() => {
    const values = new Set<string>();

    salons.forEach((salon) => {
      salon.services
        ?.split(";")
        .map((s) => s.trim())
        .filter(Boolean)
        .forEach((s) => values.add(s));
    });

    return Array.from(values).sort();
  }, [salons]);




  useEffect(() => {
    if (visibleSalons.length === 0) {
      setSelectedId(null);
      setDetail(null);
      return;
    }
    if (!selectedId || !visibleSalons.some((salon) => salon.id === selectedId)) {
      setSelectedId(visibleSalons[0].id);
    }
  }, [selectedId, visibleSalons]);

  useEffect(() => {
    if (!selectedId) {
      return;
    }
    let cancelled = false;
    setDetailLoading(true);
    setDetailError(null);
    fetchSalonDetail(selectedId)
      .then((salon) => {
        if (!cancelled) {
          setDetail(salon);
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setDetailError(error instanceof Error ? error.message : "Failed to load salon details");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setDetailLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  async function handleSave(payload: SalonUpdatePayload) {
    if (!detail) {
      return;
    }
    setSaving(true);
    setSaveMessage(null);
    setDetailError(null);
    try {
      const updated = await updateSalon(detail.id, payload);
      setDetail(updated);
      setSalons((current) =>
        current.map((salon) =>
          salon.id === updated.id
            ? {
                id: updated.id,
                name: updated.name,
                district: updated.district,
                rating: updated.rating,
                priceRange: updated.priceRange,
                services: updated.services,
                latitude: updated.latitude,
                longitude: updated.longitude,
                phone: updated.phone,
                website: updated.website,
                reviewsCount: updated.reviewsCount,
                openingHours: updated.openingHours,
              }
            : salon
        )
      );
      setSaveMessage("Saved");
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : "Failed to save changes");
    } finally {
      setSaving(false);
    }
  }

  function clearFilters() {
    setDistrict("");
    setQuery("");
    setService("");
    setSortBy("nameAsc");
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">OpenStreetMap dataset</p>
          <h1>Warsaw Beauty Salon Explorer</h1>
        </div>
        <button className="icon-button" type="button" onClick={() => void loadList()} title="Refresh data">
          <RefreshCw size={19} aria-hidden="true" />
        </button>
      </header>

      {stats && (
        <section className="stats-bar">
          <div className="stat-card">
            <strong>{stats.totalSalons.toLocaleString()}</strong>
            <span>Salons</span>
          </div>

          <div className="stat-card">
            <strong>{stats.districts}</strong>
            <span>Districts</span>
          </div>

          <div className="stat-card">
            <strong>{stats.withPhone}</strong>
            <span>Phone numbers</span>
          </div>

          <div className="stat-card">
            <strong>{stats.withWebsite}</strong>
            <span>Websites</span>
          </div>
        </section>
      )}

      <section className="toolbar" aria-label="Salon filters">
        <label className="search-box">
          <Search size={18} aria-hidden="true" />
          <input
            placeholder="Search by name"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>
        <label className="select-box">
          <span>District</span>

          <select
            value={district}
            onChange={(event) => setDistrict(event.target.value)}
          >
            <option value="">All</option>

            {districts.map((districtName) => (
              <option key={districtName} value={districtName}>
                {districtName}
              </option>
            ))}
          </select>
        </label>

        <label className="select-box">
          <span>Service</span>

          <select
            value={service}
            onChange={(event) => setService(event.target.value)}
          >
            <option value="">All</option>

            {serviceOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>

        <label className="select-box">
          <span>Sort</span>

          <select
            value={sortBy}
            onChange={(event) => setSortBy(event.target.value)}
          >
            <option value="nameAsc">Name A-Z</option>
            <option value="nameDesc">Name Z-A</option>
            <option value="district">District</option>
            <option value="completenessDesc">Most complete first</option>
            <option value="completenessAsc">Least complete first</option>
          </select>
        </label>


        <button className="icon-button" type="button" onClick={clearFilters} title="Clear filters">
          <X size={18} aria-hidden="true" />
        </button>
        <div className="result-count">{visibleSalons.length} salons</div>
      </section>

      {listError ? <div className="error-banner">{listError}</div> : null}

      <div className="workspace-grid">
        <section className="list-panel" aria-label="Salon list">
          {listLoading ? (
            <div className="empty-state">Loading salons...</div>
          ) : (
            <SalonList salons={visibleSalons} selectedId={selectedId} onSelect={setSelectedId} />
          )}
        </section>

        <section className="map-and-detail">
          <SalonMap salons={visibleSalons} detail={detail} onSelect={setSelectedId} />
          <SalonDetailPanel
            detail={detail}
            districts={districts}
            loading={detailLoading}
            saving={saving}
            saveMessage={saveMessage}
            error={detailError}
            onSave={handleSave}
          />
        </section>
      </div>
    </main>
  );
}
