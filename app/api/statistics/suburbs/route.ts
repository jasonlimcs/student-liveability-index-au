import { NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import { join } from 'path'

export async function GET() {
  try {
    const filePath = join(process.cwd(), 'data', 'processed', 'abs_demographics_merged.csv')
    
    const content = await readFile(filePath, 'utf-8')
    const lines = content.split('\n')
    
    // Parse CSV and create suburb statistics
    const suburbStats: any[] = []
    
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim()) {
        const values = lines[i].split(',')
        const sa2Code = values[0] || 'Unknown'
        const population = parseInt(values[1]) || 0
        const pctYouth = parseFloat(values[2]) || 0
        const medianAge = parseInt(values[3]) || 0
        const medianIncome = parseInt(values[4]) || 0
        const medianRent = parseInt(values[5]) || 0
        const pctStudents = parseFloat(values[6]) || 0
        const rentToIncomeRatio = parseFloat(values[7]) || 0
        
        // Calculate a liveability score based on multiple factors
        // Higher scores for: more youth, lower rent-to-income ratio, more students
        // Lower scores for: higher median age, lower income
        const youthScore = pctYouth * 10 // 0-10 points
        const ageScore = Math.max(0, (50 - medianAge) / 5) // 0-10 points (younger = better)
        const incomeScore = Math.min(10, medianIncome / 100) // 0-10 points
        const rentScore = Math.max(0, (1 - rentToIncomeRatio) * 10) // 0-10 points (lower ratio = better)
        const studentScore = pctStudents * 10 // 0-10 points
        
        const liveabilityScore = Math.round((youthScore + ageScore + incomeScore + rentScore + studentScore) * 100) / 100
        
        suburbStats.push({
          name: `SA2-${sa2Code}`, // Use SA2 code as suburb identifier
          liveability_score: liveabilityScore,
          amenities_count: Math.floor(Math.random() * 100) + 10, // Random count for demo
          population,
          pct_youth: Math.round(pctYouth * 100) / 100,
          median_age: medianAge,
          median_income: medianIncome,
          pct_students: Math.round(pctStudents * 100) / 100
        })
      }
    }
    
    // Sort by liveability score descending
    suburbStats.sort((a, b) => b.liveability_score - a.liveability_score)
    
    return NextResponse.json(suburbStats.slice(0, 20)) // Return top 20 suburbs
  } catch (error) {
    console.error('Error loading suburb data:', error)
    return NextResponse.json(
      { error: 'Failed to load suburb data' },
      { status: 500 }
    )
  }
} 