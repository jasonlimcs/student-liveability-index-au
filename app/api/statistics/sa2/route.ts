import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.SUPABASE_URL
const supabaseKey = process.env.SUPABASE_KEY

// Create Supabase client only if credentials are available
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null

// Mock data for development when Supabase is not configured
const mockSA2Data = [
  {
    id: 1,
    sa2_code: "206071116",
    sa2_name: "Melbourne",
    total_pop: 15000,
    pct_youth_18_34: 0.35,
    median_age: 28,
    median_weekly_income: 1200,
    median_weekly_rent: 450,
    pct_students: 0.25,
    rent_to_income_ratio: 0.375,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.25,
    youth_friendliness: 35,
    student_friendliness: 25,
    income_level: 1200,
    rent_level: 450
  },
  {
    id: 2,
    sa2_code: "206071117",
    sa2_name: "Carlton",
    total_pop: 12000,
    pct_youth_18_34: 0.40,
    median_age: 26,
    median_weekly_income: 1100,
    median_weekly_rent: 400,
    pct_students: 0.30,
    rent_to_income_ratio: 0.364,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.36,
    youth_friendliness: 40,
    student_friendliness: 30,
    income_level: 1100,
    rent_level: 400
  },
  {
    id: 3,
    sa2_code: "206071118",
    sa2_name: "South Yarra",
    total_pop: 18000,
    pct_youth_18_34: 0.30,
    median_age: 32,
    median_weekly_income: 1500,
    median_weekly_rent: 600,
    pct_students: 0.20,
    rent_to_income_ratio: 0.400,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.0,
    youth_friendliness: 30,
    student_friendliness: 20,
    income_level: 1500,
    rent_level: 600
  },
  {
    id: 4,
    sa2_code: "206071119",
    sa2_name: "St Kilda",
    total_pop: 14000,
    pct_youth_18_34: 0.38,
    median_age: 29,
    median_weekly_income: 1000,
    median_weekly_rent: 380,
    pct_students: 0.28,
    rent_to_income_ratio: 0.380,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.2,
    youth_friendliness: 38,
    student_friendliness: 28,
    income_level: 1000,
    rent_level: 380
  },
  {
    id: 5,
    sa2_code: "206071120",
    sa2_name: "Brunswick",
    total_pop: 16000,
    pct_youth_18_34: 0.42,
    median_age: 27,
    median_weekly_income: 950,
    median_weekly_rent: 350,
    pct_students: 0.32,
    rent_to_income_ratio: 0.368,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.32,
    youth_friendliness: 42,
    student_friendliness: 32,
    income_level: 950,
    rent_level: 350
  },
  {
    id: 6,
    sa2_code: "206071121",
    sa2_name: "Fitzroy",
    total_pop: 11000,
    pct_youth_18_34: 0.45,
    median_age: 25,
    median_weekly_income: 900,
    median_weekly_rent: 320,
    pct_students: 0.35,
    rent_to_income_ratio: 0.356,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.44,
    youth_friendliness: 45,
    student_friendliness: 35,
    income_level: 900,
    rent_level: 320
  },
  {
    id: 7,
    sa2_code: "206071122",
    sa2_name: "Northcote",
    total_pop: 13000,
    pct_youth_18_34: 0.33,
    median_age: 31,
    median_weekly_income: 1300,
    median_weekly_rent: 480,
    pct_students: 0.22,
    rent_to_income_ratio: 0.369,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.31,
    youth_friendliness: 33,
    student_friendliness: 22,
    income_level: 1300,
    rent_level: 480
  },
  {
    id: 8,
    sa2_code: "206071123",
    sa2_name: "Prahran",
    total_pop: 9000,
    pct_youth_18_34: 0.48,
    median_age: 24,
    median_weekly_income: 1400,
    median_weekly_rent: 520,
    pct_students: 0.38,
    rent_to_income_ratio: 0.371,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.29,
    youth_friendliness: 48,
    student_friendliness: 38,
    income_level: 1400,
    rent_level: 520
  },
  {
    id: 9,
    sa2_code: "206071124",
    sa2_name: "Richmond",
    total_pop: 17000,
    pct_youth_18_34: 0.36,
    median_age: 30,
    median_weekly_income: 1150,
    median_weekly_rent: 420,
    pct_students: 0.26,
    rent_to_income_ratio: 0.365,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.35,
    youth_friendliness: 36,
    student_friendliness: 26,
    income_level: 1150,
    rent_level: 420
  },
  {
    id: 10,
    sa2_code: "206071125",
    sa2_name: "Collingwood",
    total_pop: 8000,
    pct_youth_18_34: 0.50,
    median_age: 23,
    median_weekly_income: 850,
    median_weekly_rent: 300,
    pct_students: 0.40,
    rent_to_income_ratio: 0.353,
    liveability_score: 0, // Will be calculated
    affordability_score: 6.47,
    youth_friendliness: 50,
    student_friendliness: 40,
    income_level: 850,
    rent_level: 300
  }
]

// Improved liveability score calculation
function calculateLiveabilityScore(record: any): number {
  // Normalize and weight different factors for student liveability
  
  // 1. Youth Population (25% weight) - Higher is better for students
  const youthScore = Math.min(2.5, (record.pct_youth_18_34 || 0) * 10)
  
  // 2. Student Population (20% weight) - Higher is better
  const studentScore = Math.min(2.0, (record.pct_students || 0) * 10)
  
  // 3. Age Factor (15% weight) - Younger median age is better for students
  const medianAge = record.median_age || 35
  const ageScore = Math.max(0, Math.min(1.5, (45 - medianAge) / 15))
  
  // 4. Affordability (25% weight) - Lower rent-to-income ratio is better
  const rentToIncomeRatio = record.rent_to_income_ratio || 0.5
  const affordabilityScore = Math.min(2.5, Math.max(0, (0.7 - rentToIncomeRatio) * 12.5))
  
  // 5. Income Level (15% weight) - Higher income is better, but with diminishing returns
  const weeklyIncome = record.median_weekly_income || 1000
  const incomeScore = Math.min(1.5, Math.max(0, (weeklyIncome - 500) / 1000))
  
  // Calculate total score (max 10)
  const totalScore = youthScore + studentScore + ageScore + affordabilityScore + incomeScore
  
  // Ensure score is between 0 and 10
  const finalScore = Math.max(0, Math.min(10, Math.round(totalScore * 100) / 100))
  
  // Debug logging for first few records
  if (record.id <= 3) {
    console.log(`Area: ${record.sa2_name || record.sa2_code}`)
    console.log(`  Youth: ${record.pct_youth_18_34} -> ${youthScore}`)
    console.log(`  Students: ${record.pct_students} -> ${studentScore}`)
    console.log(`  Age: ${medianAge} -> ${ageScore}`)
    console.log(`  Affordability: ${rentToIncomeRatio} -> ${affordabilityScore}`)
    console.log(`  Income: ${weeklyIncome} -> ${incomeScore}`)
    console.log(`  Total: ${totalScore} -> ${finalScore}`)
  }
  
  return finalScore
}

export async function GET() {
  try {
    // If Supabase is not configured, return mock data
    if (!supabase) {
      console.log('Supabase not configured, returning mock data')
      // Calculate liveability scores for mock data
      const enhancedMockData = mockSA2Data.map((record: any) => {
        const liveabilityScore = calculateLiveabilityScore(record)
        return {
          ...record,
          liveability_score: liveabilityScore,
          affordability_score: Math.max(0, Math.min(10, (1 - (record.rent_to_income_ratio || 0)) * 10)),
          youth_friendliness: (record.pct_youth_18_34 || 0) * 100,
          student_friendliness: (record.pct_students || 0) * 100,
          income_level: record.median_weekly_income || 0,
          rent_level: record.median_weekly_rent || 0
        }
      })
      
      console.log('Mock data scores:', enhancedMockData.map(d => ({ name: d.sa2_name, score: d.liveability_score })))
      return NextResponse.json(enhancedMockData)
    }

    // Fetch SA2 demographics data from Supabase
    const { data, error } = await supabase
      .from('sa2_demographics')
      .select('*')
      .order('total_pop', { ascending: false })

    if (error) {
      console.error('Supabase error:', error)
      console.log('Falling back to mock data due to Supabase error')
      // Calculate liveability scores for mock data
      const enhancedMockData = mockSA2Data.map((record: any) => {
        const liveabilityScore = calculateLiveabilityScore(record)
        return {
          ...record,
          liveability_score: liveabilityScore,
          affordability_score: Math.max(0, Math.min(10, (1 - (record.rent_to_income_ratio || 0)) * 10)),
          youth_friendliness: (record.pct_youth_18_34 || 0) * 100,
          student_friendliness: (record.pct_students || 0) * 100,
          income_level: record.median_weekly_income || 0,
          rent_level: record.median_weekly_rent || 0
        }
      })
      return NextResponse.json(enhancedMockData)
    }

    // Calculate liveability scores and additional metrics
    const enhancedData = data.map((record: any) => {
      const liveabilityScore = calculateLiveabilityScore(record)

      return {
        ...record,
        liveability_score: liveabilityScore,
        // Add additional calculated fields
        affordability_score: Math.max(0, Math.min(10, (1 - (record.rent_to_income_ratio || 0)) * 10)),
        youth_friendliness: (record.pct_youth_18_34 || 0) * 100,
        student_friendliness: (record.pct_students || 0) * 100,
        income_level: record.median_weekly_income || 0,
        rent_level: record.median_weekly_rent || 0
      }
    })

    // Log some sample scores for debugging
    console.log('Sample scores from database:', enhancedData.slice(0, 5).map(d => ({ 
      name: d.sa2_name || d.sa2_code, 
      score: d.liveability_score 
    })))

    return NextResponse.json(enhancedData)
  } catch (error) {
    console.error('Error fetching SA2 data:', error)
    console.log('Falling back to mock data due to error')
    // Calculate liveability scores for mock data
    const enhancedMockData = mockSA2Data.map((record: any) => {
      const liveabilityScore = calculateLiveabilityScore(record)
      return {
        ...record,
        liveability_score: liveabilityScore,
        affordability_score: Math.max(0, Math.min(10, (1 - (record.rent_to_income_ratio || 0)) * 10)),
        youth_friendliness: (record.pct_youth_18_34 || 0) * 100,
        student_friendliness: (record.pct_students || 0) * 100,
        income_level: record.median_weekly_income || 0,
        rent_level: record.median_weekly_rent || 0
      }
    })
    return NextResponse.json(enhancedMockData)
  }
} 