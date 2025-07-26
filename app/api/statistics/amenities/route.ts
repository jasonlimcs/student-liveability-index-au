import { NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import { join } from 'path'

export async function GET() {
  try {
    const filePath = join(process.cwd(), 'data', 'processed', 'melbourne_amenities_improved_20250718_175145_cleaned_20250718_191258.csv')
    
    const content = await readFile(filePath, 'utf-8')
    const lines = content.split('\n')
    
    // Parse CSV and count amenities by category
    const amenityCounts: { [key: string]: number } = {}
    let totalCount = 0
    
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim()) {
        const values = lines[i].split(',')
        const category = values[1] || 'Unknown' // category is in column 2 (index 1)
        amenityCounts[category] = (amenityCounts[category] || 0) + 1
        totalCount++
      }
    }
    
    // Convert to array format for charts
    const amenityData = Object.entries(amenityCounts).map(([category, count]) => ({
      category,
      count,
      percentage: Math.round((count / totalCount) * 100)
    })).sort((a, b) => b.count - a.count)
    
    return NextResponse.json(amenityData)
  } catch (error) {
    console.error('Error loading amenities data:', error)
    return NextResponse.json(
      { error: 'Failed to load amenities data' },
      { status: 500 }
    )
  }
} 