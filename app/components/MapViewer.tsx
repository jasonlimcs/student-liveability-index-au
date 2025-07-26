'use client'

import { useState, useEffect } from 'react'

interface MapViewerProps {
  mapType: 'amenities' | 'combined'
}

export default function MapViewer({ mapType }: MapViewerProps) {
  const [mapContent, setMapContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadMap = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const fileName = mapType === 'amenities' 
          ? 'melbourne_amenities_map.html' 
          : 'melbourne_combined_map.html'
        
        const response = await fetch(`/maps/${fileName}`)
        
        if (!response.ok) {
          throw new Error(`Failed to load map: ${response.statusText}`)
        }
        
        const htmlContent = await response.text()
        setMapContent(htmlContent)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load map')
        console.error('Error loading map:', err)
      } finally {
        setLoading(false)
      }
    }

    loadMap()
  }, [mapType])

  if (loading) {
    return (
      <div className="map-container flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading map...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="map-container flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <p className="text-red-600 mb-2">Error loading map</p>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="map-container">
      <iframe
        srcDoc={mapContent}
        title={`Melbourne ${mapType === 'amenities' ? 'Amenities' : 'Combined Analysis'} Map`}
        className="w-full h-full"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  )
} 