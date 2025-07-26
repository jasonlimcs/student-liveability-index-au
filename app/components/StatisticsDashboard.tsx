'use client'

import { useState, useEffect } from 'react'
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts'
import { 
  MapPin, 
  Users, 
  Building2, 
  Coffee, 
  Bus, 
  BookOpen, 
  TrendingUp,
  Home,
  ShoppingBag,
  Utensils
} from 'lucide-react'

interface AmenityData {
  category: string
  count: number
  percentage: number
}

interface SuburbStats {
  name: string
  liveability_score: number
  amenities_count: number
  population: number
}

export default function StatisticsDashboard() {
  const [amenityData, setAmenityData] = useState<AmenityData[]>([])
  const [suburbStats, setSuburbStats] = useState<SuburbStats[]>([])
  const [loading, setLoading] = useState(true)
  const [summaryStats, setSummaryStats] = useState({
    totalAmenities: 0,
    totalSuburbs: 0,
    avgLiveabilityScore: 0,
    topSuburb: '',
    topScore: 0
  })

  useEffect(() => {
    const loadStatistics = async () => {
      try {
        setLoading(true)
        
        // Load amenities data
        const amenitiesResponse = await fetch('/api/statistics/amenities')
        const amenitiesData = await amenitiesResponse.json()
        setAmenityData(amenitiesData)

        // Load suburb statistics
        const suburbsResponse = await fetch('/api/statistics/suburbs')
        const suburbsData = await suburbsResponse.json()
        setSuburbStats(suburbsData)

        // Calculate summary statistics
        const totalAmenities = amenitiesData.reduce((sum: number, item: AmenityData) => sum + item.count, 0)
        const avgScore = suburbsData.reduce((sum: number, item: SuburbStats) => sum + item.liveability_score, 0) / suburbsData.length
        const topSuburb = suburbsData.reduce((max: SuburbStats, item: SuburbStats) => 
          item.liveability_score > max.liveability_score ? item : max, suburbsData[0])

        setSummaryStats({
          totalAmenities,
          totalSuburbs: suburbsData.length,
          avgLiveabilityScore: Math.round(avgScore * 100) / 100,
          topSuburb: topSuburb?.name || '',
          topScore: topSuburb?.liveability_score || 0
        })

      } catch (error) {
        console.error('Error loading statistics:', error)
      } finally {
        setLoading(false)
      }
    }

    loadStatistics()
  }, [])

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="stat-card animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="stat-card">
          <div className="flex items-center">
            <MapPin className="w-8 h-8 text-blue-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Total Amenities</p>
              <p className="text-2xl font-bold text-gray-900">{summaryStats.totalAmenities.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <Users className="w-8 h-8 text-green-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Suburbs Analyzed</p>
              <p className="text-2xl font-bold text-gray-900">{summaryStats.totalSuburbs}</p>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <TrendingUp className="w-8 h-8 text-purple-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Avg Liveability Score</p>
              <p className="text-2xl font-bold text-gray-900">{summaryStats.avgLiveabilityScore}</p>
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="flex items-center">
            <Home className="w-8 h-8 text-orange-600 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Top Suburb</p>
              <p className="text-lg font-bold text-gray-900">{summaryStats.topSuburb}</p>
              <p className="text-sm text-gray-500">Score: {summaryStats.topScore}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Amenities Distribution */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Amenities Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={amenityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percentage }) => `${name} (${percentage}%)`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {amenityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Top Suburbs by Liveability Score */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Top Suburbs by Liveability Score</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={suburbStats.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="liveability_score" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
} 