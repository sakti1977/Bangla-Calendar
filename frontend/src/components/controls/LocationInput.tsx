import { useState } from 'react'
import { useLocationStore } from '../../store/locationStore'

interface SearchResult {
  name: string
  lat: number
  lon: number
}

// Quick preset list for common Bengali-speaking cities
const PRESETS: SearchResult[] = [
  { name: 'Dhaka', lat: 23.8103, lon: 90.4125 },
  { name: 'Chittagong', lat: 22.3569, lon: 91.7832 },
  { name: 'Sylhet', lat: 24.8949, lon: 91.8687 },
  { name: 'Rajshahi', lat: 24.3636, lon: 88.6241 },
  { name: 'Kolkata', lat: 22.5726, lon: 88.3639 },
  { name: 'Khulna', lat: 22.8456, lon: 89.5403 },
  { name: 'Barisal', lat: 22.7010, lon: 90.3535 },
  { name: 'Rangpur', lat: 25.7439, lon: 89.2752 },
]

export function LocationInput() {
  const { lat, lon, locationName, isCustom, setLocation, resetToRegionDefault } = useLocationStore()
  const [query, setQuery] = useState('')
  const [showDropdown, setShowDropdown] = useState(false)

  const filtered = query.length >= 2
    ? PRESETS.filter((p) => p.name.toLowerCase().includes(query.toLowerCase()))
    : []

  const handleSelect = (result: SearchResult) => {
    setLocation(result.lat, result.lon, result.name)
    setQuery('')
    setShowDropdown(false)
  }

  return (
    <div className="relative">
      <div className="flex items-center gap-1.5 rounded-lg border border-gray-300 bg-white px-2 py-1.5 text-sm">
        <svg className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <input
          type="text"
          value={query}
          onChange={(e) => { setQuery(e.target.value); setShowDropdown(true) }}
          onFocus={() => setShowDropdown(true)}
          onBlur={() => setTimeout(() => setShowDropdown(false), 150)}
          placeholder={isCustom ? locationName : 'Location…'}
          className="w-28 outline-none text-gray-700 placeholder-gray-400 bg-transparent"
        />
        {isCustom && (
          <button
            onClick={() => resetToRegionDefault('BD')}
            className="text-gray-400 hover:text-gray-600 ml-1"
            title="Reset to default"
          >
            ✕
          </button>
        )}
      </div>

      {showDropdown && filtered.length > 0 && (
        <ul className="absolute z-10 mt-1 w-full min-w-max bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
          {filtered.map((r) => (
            <li key={r.name}>
              <button
                onMouseDown={() => handleSelect(r)}
                className="w-full text-left px-3 py-2 text-sm hover:bg-orange-50 text-gray-700"
              >
                {r.name}
                <span className="text-gray-400 ml-1 text-xs">
                  {r.lat.toFixed(2)}°N {r.lon.toFixed(2)}°E
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}

      {!isCustom && (
        <p className="absolute -bottom-4 left-0 text-xs text-gray-400 whitespace-nowrap">
          {lat.toFixed(2)}°N {lon.toFixed(2)}°E
        </p>
      )}
    </div>
  )
}
