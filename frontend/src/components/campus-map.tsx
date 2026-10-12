
"use client";

import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  useMap,
} from "react-leaflet";
import { latLngBounds } from "leaflet";

type LocationPoint = {
  id: number;
  location_name: string;
  latitude: number;
  longitude: number;
  location_type: string;
};

type CampusMapProps = {
  center: [number, number];
  zoom: number;
  locations: LocationPoint[];
};

function MapViewport({
  center,
  zoom,
  locations,
}: CampusMapProps) {
  const map = useMap();

  useEffect(() => {
    const validLocations = locations
      .map((location) => ({
        ...location,
        latitude: Number(location.latitude),
        longitude: Number(location.longitude),
      }))
      .filter(
        (location) =>
          Number.isFinite(location.latitude) &&
          Number.isFinite(location.longitude) &&
          location.latitude >= -90 &&
          location.latitude <= 90 &&
          location.longitude >= -180 &&
          location.longitude <= 180
      );

    if (validLocations.length === 0) {
      map.setView(center, zoom, { animate: true });
      return;
    }

    if (validLocations.length === 1) {
      const location = validLocations[0];

      map.setView(
        [location.latitude, location.longitude],
        Math.min(Math.max(zoom, 16), 19),
        { animate: true }
      );

      return;
    }

    const bounds = latLngBounds(
      validLocations.map(
        (location) =>
          [location.latitude, location.longitude] as [number, number]
      )
    );

    map.fitBounds(bounds, {
  padding: [60, 60],
  maxZoom: 18,
  animate: false,
});
  }, [map, center, zoom, locations]);

  return null;
}

export default function CampusMap({
  center,
  zoom,
  locations,
}: CampusMapProps) {
  const validLocations = locations
    .map((location) => ({
      ...location,
      latitude: Number(location.latitude),
      longitude: Number(location.longitude),
    }))
    .filter(
      (location) =>
        Number.isFinite(location.latitude) &&
        Number.isFinite(location.longitude) &&
        location.latitude >= -90 &&
        location.latitude <= 90 &&
        location.longitude >= -180 &&
        location.longitude <= 180
    );

  return (
    <div
      style={{
        height: 420,
        width: "100%",
        borderRadius: 18,
        overflow: "hidden",
        border: "1px solid var(--border)",
      }}
    >
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom
        className="cg-map"
        style={{ height: "100%", width: "100%" }}
      >
        
<TileLayer
  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
  maxZoom={19}
  eventHandlers={{
    tileerror: () => {
      console.error("Campus map tile failed to load.");
    },
  }}
/>


        <MapViewport
          center={center}
          zoom={zoom}
          locations={locations}
        />

        {validLocations.map((location) => (
          <CircleMarker
            key={location.id}
            center={[location.latitude, location.longitude]}
            radius={9}
            pathOptions={{
              color: "#1d4ed8",
              fillColor: "#2563eb",
              fillOpacity: 0.85,
              weight: 2,
            }}
          >
            <Popup>
              <strong>{location.location_name}</strong>
              <br />
              {location.location_type}
              <br />
              {location.latitude}, {location.longitude}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
