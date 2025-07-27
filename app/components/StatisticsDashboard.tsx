'use client'

import { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale,
} from 'chart.js'
import { Line, Bar, Doughnut, Radar, Scatter } from 'react-chartjs-2'
import {
  MapPin,
  Users,
  TrendingUp,
  Home,
  DollarSign,
  GraduationCap,
  Shield,
  Building2,
  Target,
  Activity,
  BarChart3,
  PieChart
} from 'lucide-react'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale
)

interface SA2Data {
  id: number
  sa2_code: string
  sa2_name: string
  total_pop: number
  pct_youth_18_34: number
  median_age: number
  median_weekly_income: number
  median_weekly_rent: number
  pct_students: number
  rent_to_income_ratio: number
  liveability_score: number
  affordability_score: number
  youth_friendliness: number
  student_friendliness: number
  income_level: number
  rent_level: number
}

interface DashboardStats {
  totalAreas: number
  avgLiveabilityScore: number
  avgIncome: number
  avgRent: number
  avgStudentPercentage: number
  topArea: string
  topScore: number
  totalPopulation: number
}

export default function StatisticsDashboard() {
  const [sa2Data, setSa2Data] = useState<SA2Data[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<DashboardStats>({
    totalAreas: 0,
    avgLiveabilityScore: 0,
    avgIncome: 0,
    avgRent: 0,
    avgStudentPercentage: 0,
    topArea: '',
    topScore: 0,
    totalPopulation: 0
  })

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)
        
        const response = await fetch('/api/statistics/sa2')
        if (!response.ok) {
          throw new Error('Failed to fetch data')
        }
        
        const data = await response.json()
        setSa2Data(data)
        
        // Debug logging
        console.log('Dashboard received data:', data.length, 'records')
        console.log('Sample scores:', data.slice(0, 5).map((d: SA2Data) => ({ 
          name: d.sa2_name, 
          score: d.liveability_score 
        })))
        
        // Calculate summary statistics
        const totalAreas = data.length
        const avgLiveabilityScore = data.reduce((sum: number, item: SA2Data) => sum + item.liveability_score, 0) / totalAreas
        const avgIncome = data.reduce((sum: number, item: SA2Data) => sum + item.income_level, 0) / totalAreas
        const avgRent = data.reduce((sum: number, item: SA2Data) => sum + item.rent_level, 0) / totalAreas
        const avgStudentPercentage = data.reduce((sum: number, item: SA2Data) => sum + item.student_friendliness, 0) / totalAreas
        const totalPopulation = data.reduce((sum: number, item: SA2Data) => sum + item.total_pop, 0)
        
        const topArea = data.reduce((max: SA2Data, item: SA2Data) => 
          item.liveability_score > max.liveability_score ? item : max, data[0])
        
        setStats({
          totalAreas,
          avgLiveabilityScore: Math.round(avgLiveabilityScore * 100) / 100,
          avgIncome: Math.round(avgIncome),
          avgRent: Math.round(avgRent),
          avgStudentPercentage: Math.round(avgStudentPercentage * 100) / 100,
          topArea: topArea?.sa2_name || '',
          topScore: topArea?.liveability_score || 0,
          totalPopulation
        })
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data')
        console.error('Error loading statistics:', err)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [])

  // Chart configurations
  const liveabilityDistributionData = {
    labels: ['Poor (0-2)', 'Fair (2-4)', 'Good (4-6)', 'Very Good (6-8)', 'Excellent (8-10)'],
    datasets: [{
      label: 'Number of Areas',
      data: [
        sa2Data.filter(d => d.liveability_score < 2).length,
        sa2Data.filter(d => d.liveability_score >= 2 && d.liveability_score < 4).length,
        sa2Data.filter(d => d.liveability_score >= 4 && d.liveability_score < 6).length,
        sa2Data.filter(d => d.liveability_score >= 6 && d.liveability_score < 8).length,
        sa2Data.filter(d => d.liveability_score >= 8).length,
      ],
      backgroundColor: [
        'rgba(239, 68, 68, 0.8)',   // Red for poor
        'rgba(245, 158, 11, 0.8)',  // Orange for fair
        'rgba(59, 130, 246, 0.8)',  // Blue for good
        'rgba(16, 185, 129, 0.8)',  // Green for very good
        'rgba(139, 92, 246, 0.8)',  // Purple for excellent
      ],
      borderColor: [
        'rgba(239, 68, 68, 1)',
        'rgba(245, 158, 11, 1)',
        'rgba(59, 130, 246, 1)',
        'rgba(16, 185, 129, 1)',
        'rgba(139, 92, 246, 1)',
      ],
      borderWidth: 2,
    }]
  }

  const topAreasData = {
    labels: sa2Data
      .sort((a, b) => b.liveability_score - a.liveability_score)
      .slice(0, 10)
      .map(d => d.sa2_name),
    datasets: [{
      label: 'Liveability Score',
      data: sa2Data
        .sort((a, b) => b.liveability_score - a.liveability_score)
        .slice(0, 10)
        .map(d => d.liveability_score),
      backgroundColor: 'rgba(59, 130, 246, 0.8)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 2,
    }]
  }

  const incomeVsRentData = {
    datasets: [{
      label: 'Income vs Rent',
      data: sa2Data.slice(0, 50).map(d => ({
        x: d.income_level,
        y: d.rent_level
      })),
      backgroundColor: 'rgba(16, 185, 129, 0.6)',
      borderColor: 'rgba(16, 185, 129, 1)',
      borderWidth: 1,
    }]
  }

  const affordabilityRadarData = {
    labels: ['Youth Friendliness', 'Student Friendliness', 'Affordability', 'Income Level', 'Population'],
    datasets: [{
      label: 'Melbourne Average',
      data: [
        stats.avgStudentPercentage,
        stats.avgStudentPercentage,
        Math.min(100, stats.avgRent / stats.avgIncome * 100),
        Math.min(100, stats.avgIncome / 1000),
        Math.min(100, stats.totalPopulation / stats.totalAreas / 1000)
      ],
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      borderColor: 'rgba(59, 130, 246, 1)',
      borderWidth: 2,
      pointBackgroundColor: 'rgba(59, 130, 246, 1)',
    }]
  }

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="bg-white rounded-xl shadow-lg p-6 animate-pulse">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="h-64 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
        <div className="text-red-600 text-lg font-semibold mb-2">Error Loading Data</div>
        <div className="text-red-500">{error}</div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Enhanced Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Areas</p>
              <p className="text-3xl font-bold">{stats.totalAreas.toLocaleString()}</p>
            </div>
            <MapPin className="w-8 h-8 text-blue-200" />
          </div>
          <div className="mt-4 text-blue-100 text-sm">
            Across Melbourne
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Avg Liveability</p>
              <p className="text-3xl font-bold">{stats.avgLiveabilityScore}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-200" />
          </div>
          <div className="mt-4 text-green-100 text-sm">
            Score out of 10
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Avg Income</p>
              <p className="text-3xl font-bold">${stats.avgIncome}</p>
            </div>
            <DollarSign className="w-8 h-8 text-purple-200" />
          </div>
          <div className="mt-4 text-purple-100 text-sm">
            Weekly median
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl shadow-lg p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm font-medium">Student %</p>
              <p className="text-3xl font-bold">{stats.avgStudentPercentage}%</p>
            </div>
            <GraduationCap className="w-8 h-8 text-orange-200" />
          </div>
          <div className="mt-4 text-orange-100 text-sm">
            Average across areas
          </div>
        </div>
      </div>

      {/* Enhanced Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Liveability Distribution */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Liveability Score Distribution</h3>
            <BarChart3 className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-80">
            <Bar 
              data={liveabilityDistributionData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  },
                  tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    grid: {
                      color: 'rgba(0, 0, 0, 0.1)'
                    }
                  },
                  x: {
                    grid: {
                      display: false
                    }
                  }
                }
              }}
            />
          </div>
        </div>

        {/* Top Areas by Liveability */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Top 10 Areas by Liveability</h3>
            <Target className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-80">
            <Bar 
              data={topAreasData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y' as const,
                plugins: {
                  legend: {
                    display: false
                  },
                  tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                  }
                },
                scales: {
                  x: {
                    beginAtZero: true,
                    grid: {
                      color: 'rgba(0, 0, 0, 0.1)'
                    }
                  },
                  y: {
                    grid: {
                      display: false
                    }
                  }
                }
              }}
            />
          </div>
        </div>

        {/* Income vs Rent Scatter */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Income vs Rent Analysis</h3>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-80">
            <Scatter 
              data={incomeVsRentData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  },
                  tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    callbacks: {
                      label: (context) => {
                        const point = context.parsed
                        return `Income: $${point.x}, Rent: $${point.y}`
                      }
                    }
                  }
                },
                scales: {
                  x: {
                    title: {
                      display: true,
                      text: 'Weekly Income ($)'
                    },
                    grid: {
                      color: 'rgba(0, 0, 0, 0.1)'
                    }
                  },
                  y: {
                    title: {
                      display: true,
                      text: 'Weekly Rent ($)'
                    },
                    grid: {
                      color: 'rgba(0, 0, 0, 0.1)'
                    }
                  }
                }
              }}
            />
          </div>
        </div>

        {/* Affordability Radar */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Melbourne Liveability Profile</h3>
            <PieChart className="w-5 h-5 text-gray-400" />
          </div>
          <div className="h-80">
            <Radar 
              data={affordabilityRadarData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  },
                  tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                  }
                },
                scales: {
                  r: {
                    beginAtZero: true,
                    grid: {
                      color: 'rgba(0, 0, 0, 0.1)'
                    },
                    pointLabels: {
                      font: {
                        size: 10
                      }
                    }
                  }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Key Insights Section */}
      <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Key Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center mb-2">
              <Shield className="w-5 h-5 text-green-500 mr-2" />
              <span className="font-medium text-gray-900">Best Area</span>
            </div>
            <p className="text-2xl font-bold text-green-600">{stats.topArea}</p>
            <p className="text-sm text-gray-600">Score: {stats.topScore}/10</p>
          </div>
          
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center mb-2">
              <Building2 className="w-5 h-5 text-blue-500 mr-2" />
              <span className="font-medium text-gray-900">Total Population</span>
            </div>
            <p className="text-2xl font-bold text-blue-600">{stats.totalPopulation.toLocaleString()}</p>
            <p className="text-sm text-gray-600">Across all areas</p>
          </div>
          
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="flex items-center mb-2">
              <Home className="w-5 h-5 text-purple-500 mr-2" />
              <span className="font-medium text-gray-900">Avg Rent</span>
            </div>
            <p className="text-2xl font-bold text-purple-600">${stats.avgRent}</p>
            <p className="text-sm text-gray-600">Weekly median</p>
          </div>
        </div>
      </div>

      {/* Liveability Score Breakdown */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Liveability Score Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600 mb-2">25%</div>
            <div className="text-sm font-medium text-gray-900">Youth Population</div>
            <div className="text-xs text-gray-600 mt-1">Higher % of 18-34 year olds</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600 mb-2">20%</div>
            <div className="text-sm font-medium text-gray-900">Student Population</div>
            <div className="text-xs text-gray-600 mt-1">Higher % of students</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600 mb-2">15%</div>
            <div className="text-sm font-medium text-gray-900">Age Factor</div>
            <div className="text-xs text-gray-600 mt-1">Lower median age</div>
          </div>
          
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600 mb-2">25%</div>
            <div className="text-sm font-medium text-gray-900">Affordability</div>
            <div className="text-xs text-gray-600 mt-1">Lower rent-to-income ratio</div>
          </div>
          
          <div className="text-center p-4 bg-indigo-50 rounded-lg">
            <div className="text-2xl font-bold text-indigo-600 mb-2">15%</div>
            <div className="text-sm font-medium text-gray-900">Income Level</div>
            <div className="text-xs text-gray-600 mt-1">Higher median income</div>
          </div>
        </div>
        
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">Score Interpretation</h4>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-2 text-sm">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
              <span>0-2: Poor</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
              <span>2-4: Fair</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
              <span>4-6: Good</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span>6-8: Very Good</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-2"></div>
              <span>8-10: Excellent</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 