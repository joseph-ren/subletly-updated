import { useEffect, useState, useMemo } from 'react'

const AMENITY_OPTIONS = ['wifi', 'parking', 'pool', 'gym', 'pet-friendly']

function Header() {
  return (
    <header className="max-w-4xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-gradient-to-br from-indigo-600 to-pink-500 text-white shadow-md ring-1 ring-white/20">
            <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden>
              <path d="M4 12c0-4.418 3.582-8 8-8s8 3.582 8 8-3.582 8-8 8a8 8 0 01-8-8z" stroke="currentColor" strokeWidth="0" fill="currentColor" opacity="0.06" />
              <path d="M8.5 13.5c.5 1 1.75 2.25 3.75 2.25 2.25 0 4-1.75 4-4 0-2-1.5-3.25-3.5-3.25-1.25 0-2.25.5-2.75 1.25" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M9 9.5c.5-.5 1.25-1 2.5-1" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>

          <div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-gray-900 leading-tight">Subletly</h1>
            <p className="text-sm md:text-base text-gray-600 mt-1">Find short-term rooms and sublets — tailored to your needs.</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="inline-flex items-center px-3 py-1 rounded-full bg-yellow-50 text-yellow-800 text-sm font-medium border border-yellow-100">Beta</span>
        </div>
      </div>
    </header>
  )
}

function ListingCard({ l, accessFilters = [], hasAmenityFilters = false }) {
  const [showInfo, setShowInfo] = useState(false)

  return (
    <div className="bg-white shadow rounded-lg p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h2 className="text-lg font-semibold">{l.title}</h2>
          <div className="text-sm text-gray-500 mt-1">{l.location}</div>
        </div>

        <div className="flex-shrink-0 text-right">
          <div className="text-green-600 font-bold">${l.price}</div>
          {l.matchability != null && (
            <div className="mt-2 flex items-center justify-end gap-2">
              {(() => {
                const pct = l.matchability
                let gradient = 'from-red-500 to-red-600 text-white'
                if (pct >= 75) gradient = 'from-green-500 to-emerald-400 text-white'
                else if (pct >= 40) gradient = 'from-yellow-400 to-orange-400 text-black'
                return (
                  <div className={`inline-flex items-center px-3 py-1 rounded-full bg-gradient-to-r ${gradient} text-sm font-semibold`} aria-hidden>
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 1.343-3 3 0 1.657 1.343 3 3 3s3-1.343 3-3c0-1.657-1.343-3-3-3z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 2v2m0 16v2m8-10h-2M4 12H2m15.07-6.07l-1.414 1.414M7.344 16.657l-1.414 1.414M16.657 16.657l1.414 1.414M7.344 7.343L5.93 5.93"></path></svg>
                    {pct}%
                  </div>
                )
              })()}
              <button onClick={() => setShowInfo(true)} aria-label="Why this match" className="text-gray-500 hover:text-gray-700 p-1 rounded-full">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fillRule="evenodd" d="M18 10A8 8 0 11 2 10a8 8 0 0116 0zM9 8a1 1 0 112 0v1a1 1 0 11-2 0V8zm.25 4.75a.75.75 0 011.5 0V14a.75.75 0 01-1.5 0v-1.25z" clipRule="evenodd"/></svg>
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {(l.amenities || []).map((a, i) => (
          <span key={i} className="text-xs bg-gray-100 px-2 py-1 rounded">{a}</span>
        ))}
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {typeof l.walkable_score !== 'undefined' && (
          <span className="inline-flex items-center gap-2 text-xs bg-green-50 text-green-700 px-2 py-1 rounded" title={`Walkability: ${l.walkable_score}`}>
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d="M5 21h4V10H5z" />
              <path d="M9 7l4-4 4 4" />
            </svg>
            <span className="font-medium">Walkable</span>
            <span className="ml-1 text-xs font-mono text-gray-700">{l.walkable_score}</span>
          </span>
        )}
        {typeof l.transit_score !== 'undefined' && (
          <span className="inline-flex items-center gap-2 text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded" title={`Transit access: ${l.transit_score}`}>
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <rect x="3" y="7" width="18" height="10" rx="2" />
              <path d="M16 3v4" />
              <path d="M8 3v4" />
            </svg>
            <span className="font-medium">Transit</span>
            <span className="ml-1 text-xs font-mono text-gray-700">{l.transit_score}</span>
          </span>
        )}
        {typeof l.car_score !== 'undefined' && (
          <span className="inline-flex items-center gap-2 text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded" title={`Car mobility: ${l.car_score}`}>
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
              <path d="M3 13h18" />
              <path d="M7 13v-3a4 4 0 0 1 4-4h2a4 4 0 0 1 4 4v3" />
              <circle cx="7.5" cy="17.5" r="1.5" />
              <circle cx="16.5" cy="17.5" r="1.5" />
            </svg>
            <span className="font-medium">Car</span>
            <span className="ml-1 text-xs font-mono text-gray-700">{l.car_score}</span>
          </span>
        )}
      </div>

      {showInfo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="absolute inset-0 bg-black opacity-40" onClick={() => setShowInfo(false)} />
          <div role="dialog" aria-modal="true" className="relative bg-white rounded-lg shadow-lg max-w-md w-full p-6 z-10">
            <div className="flex items-start justify-between">
              <h3 className="text-lg font-semibold">How the match score is calculated</h3>
            </div>
            <div className="mt-4 text-sm text-gray-700">
              <p>The matchability score is a weighted percentage combining amenity match and price:</p>
              <ul className="list-disc ml-5 mt-2 text-sm">
                <li><strong>Amenities (60%)</strong> — how many of the requested amenities the listing contains.</li>
                <li className="mt-1"><strong>Price (40%)</strong> — cheaper listings score higher relative to the result set or your budget.</li>
              </ul>
              <p className="mt-3 text-xs text-gray-500">Higher is better — a 100% match means this listing is very likely to match your filters and is competitively priced.</p>
              {accessFilters && accessFilters.length > 0 && (
                (() => {
                  // compute access weight same as backend logic
                  const accessWeight = hasAmenityFilters ? 0.2 : 0.4
                  const scores = []
                  accessFilters.forEach(f => {
                    if (f === 'walkable' && typeof l.walkable_score !== 'undefined') scores.push(l.walkable_score)
                    if (f === 'transit' && typeof l.transit_score !== 'undefined') scores.push(l.transit_score)
                    if (f === 'car_friendly' && typeof l.car_score !== 'undefined') scores.push(l.car_score)
                  })
                  const avg = scores.length ? (scores.reduce((a,b)=>a+b,0)/scores.length) : null
                  const contribution = avg !== null ? Math.round((avg/100) * accessWeight * 100) : null
                  return (
                    <div className="mt-3 text-xs text-gray-600">
                      <p><strong>Accessibility contribution</strong> — you asked for: {accessFilters.join(', ')}. The listing's accessibility scores for those filters were averaged{avg !== null ? ` (${scores.join(' / ')}, avg ${avg.toFixed(1)})` : ''} and weighted into the match score. In this configuration accessibility contributed about <span className="font-medium">{contribution !== null ? `${contribution}%` : 'N/A'}</span> to the final matchability.</p>
                      <p className="mt-2 text-gray-500">If no accessibility filters are selected, accessibility scores do not affect the matchability.</p>
                    </div>
                  )
                })()
              )}
            </div>
            <div className="mt-4 text-right">
              <button onClick={() => setShowInfo(false)} className="px-3 py-1 bg-blue-600 text-white rounded">Got it</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function Home() {
  const [listings, setListings] = useState([])
  const [loading, setLoading] = useState(false)
  const [sort, setSort] = useState('match')
  const [budget, setBudget] = useState('')
  const [location, setLocation] = useState('')
  const [amenities, setAmenities] = useState([])
  const [walkable, setWalkable] = useState(false)
  const [transit, setTransit] = useState(false)
  const [carFriendly, setCarFriendly] = useState(false)

  useEffect(() => {
    fetchListings()
  }, [])

  async function fetchListings(params = {}) {
    setLoading(true)
    try {
      const base = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5001'
      const qs = new URLSearchParams()
      if (params.budget) qs.set('budget', params.budget)
      if (params.location) qs.set('location', params.location)
      if (params.amenities) qs.set('amenities', params.amenities.join(','))
      if (params.walkable) qs.set('walkable', params.walkable)
      if (params.transit) qs.set('transit', params.transit)
      if (params.car_friendly) qs.set('car_friendly', params.car_friendly)

      const url = base + '/api/listings' + (qs.toString() ? `?${qs.toString()}` : '')
      const res = await fetch(url)
      const data = await res.json()
      setListings(data)
    } catch (err) {
      console.error('fetchListings error', err)
    } finally {
      setLoading(false)
    }
  }

  function toggleAmenity(a) {
    setAmenities(prev => prev.includes(a) ? prev.filter(x => x !== a) : [...prev, a])
  }

  function onSubmit(e) {
    e.preventDefault()
    const params = {}
    if (budget) params.budget = budget
    if (location) params.location = location
    if (amenities.length) params.amenities = amenities
    if (walkable) params.walkable = 'true'
    if (transit) params.transit = 'true'
    if (carFriendly) params.car_friendly = 'true'
    fetchListings(params)
  }

  function onReset() {
    setBudget('')
    setLocation('')
    setAmenities([])
    setWalkable(false)
    setTransit(false)
    setCarFriendly(false)
    fetchListings()
  }

  const sortedListings = useMemo(() => {
    const arr = [...listings]
    if (sort === 'price-asc') arr.sort((a, b) => a.price - b.price)
    else if (sort === 'price-desc') arr.sort((a, b) => b.price - a.price)
    else arr.sort((a, b) => (b.matchability || 0) - (a.matchability || 0))
    return arr
  }, [listings, sort])

  return (
    <div>
      <Header />
      <main className="max-w-4xl mx-auto px-4">
        <form onSubmit={onSubmit} className="bg-white p-4 rounded shadow mb-6">
          <div className="flex flex-col md:flex-row gap-3">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700">Budget (max)</label>
              <input type="number" value={budget} onChange={e => setBudget(e.target.value)} className="mt-1 block w-full border rounded px-3 py-2" />
            </div>
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700">Location</label>
              <input type="text" value={location} onChange={e => setLocation(e.target.value)} placeholder="e.g. Vancouver" className="mt-1 block w-full border rounded px-3 py-2" />
            </div>
          </div>

          <div className="mt-3">
            <div className="text-sm font-medium text-gray-700">Amenities</div>
            <div className="flex flex-wrap mt-2 gap-2">
              {AMENITY_OPTIONS.map(a => (
                <label key={a} className={`inline-flex items-center px-2 py-1 border rounded ${amenities.includes(a) ? 'bg-blue-50 border-blue-200' : 'bg-gray-50'}`}>
                  <input type="checkbox" checked={amenities.includes(a)} onChange={() => toggleAmenity(a)} className="mr-2" />
                  <span className="text-sm">{a}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="mt-3">
            <div className="text-sm font-medium text-gray-700">Accessibility</div>
            <div className="flex flex-wrap mt-2 gap-2">
              <label className={`inline-flex items-center px-2 py-1 border rounded ${walkable ? 'bg-green-50 border-green-200' : 'bg-gray-50'}`}>
                <input type="checkbox" checked={walkable} onChange={() => setWalkable(v => !v)} className="mr-2" />
                <span className="text-sm">Walkable</span>
              </label>
              <label className={`inline-flex items-center px-2 py-1 border rounded ${transit ? 'bg-blue-50 border-blue-200' : 'bg-gray-50'}`}>
                <input type="checkbox" checked={transit} onChange={() => setTransit(v => !v)} className="mr-2" />
                <span className="text-sm">Transit</span>
              </label>
              <label className={`inline-flex items-center px-2 py-1 border rounded ${carFriendly ? 'bg-gray-50 border-gray-200' : 'bg-gray-50'}`}>
                <input type="checkbox" checked={carFriendly} onChange={() => setCarFriendly(v => !v)} className="mr-2" />
                <span className="text-sm">Car-friendly</span>
              </label>
            </div>
          </div>

          <div className="mt-4 flex gap-2">
            <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Search</button>
            <button type="button" onClick={onReset} className="px-4 py-2 border rounded">Reset</button>
          </div>
        </form>

        {loading ? (
          <div className="text-center text-gray-500">Loading…</div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-3 gap-3">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <span className="inline-flex items-center px-2 py-1 rounded-full bg-gradient-to-r from-green-500 to-emerald-400 text-white text-xs">High</span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full bg-gradient-to-r from-yellow-400 to-orange-400 text-black text-xs">Medium</span>
                  <span className="inline-flex items-center px-2 py-1 rounded-full bg-gradient-to-r from-red-500 to-red-600 text-white text-xs">Low</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <label className="text-sm text-gray-600">Sort by:</label>
                <select value={sort} onChange={e => setSort(e.target.value)} className="border rounded px-2 py-1">
                  <option value="match">Best match</option>
                  <option value="price-asc">Price: low to high</option>
                  <option value="price-desc">Price: high to low</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {sortedListings.length === 0 && (
                <div className="text-gray-500">No listings found.</div>
              )}
              {sortedListings.map((l, i) => (
                <ListingCard
                  key={i}
                  l={l}
                  accessFilters={[walkable ? 'walkable' : null, transit ? 'transit' : null, carFriendly ? 'car_friendly' : null].filter(Boolean)}
                  hasAmenityFilters={amenities.length > 0}
                />
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
