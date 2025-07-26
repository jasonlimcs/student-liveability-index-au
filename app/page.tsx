'use client'

import { useState, useEffect } from 'react'
import { MapPin, Users, Building2, Coffee, Bus, BookOpen, TrendingUp } from 'lucide-react'
import MapViewer from './components/MapViewer'
import StatisticsDashboard from './components/StatisticsDashboard'
import Navigation from './components/Navigation'

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [mapData, setMapData] = useState<any>(null)

  useEffect(() => {
    // Load map data
    fetch('/api/maps')
      .then(res => res.json())
      .then(data => setMapData(data))
      .catch(err => console.error('Error loading map data:', err))
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Melbourne Student Liveability Index
          </h1>
          <p className="text-lg text-gray-600">
            Comprehensive analysis of student liveability using amenities data and demographic information
          </p>
        </div>

        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            <StatisticsDashboard />
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-semibold mb-4 flex items-center">
                  <MapPin className="w-6 h-6 mr-2 text-blue-600" />
                  Amenities Map
                </h2>
                <MapViewer mapType="amenities" />
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-semibold mb-4 flex items-center">
                  <Users className="w-6 h-6 mr-2 text-green-600" />
                  Combined Analysis Map
                </h2>
                <MapViewer mapType="combined" />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'maps' && (
          <div className="space-y-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-2xl font-semibold mb-4">Interactive Combined Liveability Map</h2>
              <div className="w-full">
                <MapViewer mapType="combined" fullHeight={true} />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'about' && (
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-3xl font-bold mb-6">About the Project</h2>
            <div className="prose max-w-none">
              <p className="text-lg text-gray-700 mb-4">
                The Melbourne Student Liveability Index is a comprehensive analysis that evaluates the quality of life 
                for students in Melbourne by examining various factors including:
              </p>
              <ul className="list-disc list-inside space-y-2 text-gray-700 mb-6">
                <li>Access to educational facilities and libraries</li>
                <li>Public transportation connectivity</li>
                <li>Recreational and entertainment venues</li>
                <li>Safety and security measures</li>
                <li>Demographic and socioeconomic factors</li>
              </ul>
              <p className="text-lg text-gray-700">
                This dashboard provides interactive visualizations and detailed statistics to help students, 
                researchers, and policymakers understand the liveability landscape across different Melbourne suburbs.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  )
} 