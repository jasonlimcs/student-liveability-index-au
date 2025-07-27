# Liveability Score System Guide

## 🎯 Overview

The liveability score is a comprehensive metric designed specifically for students, ranging from 0-10. It evaluates areas based on factors that directly impact student quality of life in Melbourne.

## 📊 Scoring Components

### 1. Youth Population (25% weight)
- **What it measures**: Percentage of population aged 18-34
- **Why it matters**: Areas with more young people tend to have better student amenities, nightlife, and social opportunities
- **Scoring**: Up to 2.5 points (25% of total score)
- **Formula**: `Math.min(2.5, (pct_youth_18_34 * 10))`

### 2. Student Population (20% weight)
- **What it measures**: Percentage of population who are students
- **Why it matters**: Higher student populations indicate better educational infrastructure, study spaces, and peer support
- **Scoring**: Up to 2.0 points (20% of total score)
- **Formula**: `Math.min(2.0, (pct_students * 10))`

### 3. Age Factor (15% weight)
- **What it measures**: Median age of the population
- **Why it matters**: Younger median ages suggest more vibrant, student-friendly environments
- **Scoring**: Up to 1.5 points (15% of total score)
- **Formula**: `Math.max(0, Math.min(1.5, (40 - median_age) / 10))`

### 4. Affordability (25% weight)
- **What it measures**: Rent-to-income ratio
- **Why it matters**: Lower ratios mean housing is more affordable relative to income
- **Scoring**: Up to 2.5 points (25% of total score)
- **Formula**: `Math.min(2.5, Math.max(0, (0.6 - rent_to_income_ratio) * 10))`

### 5. Income Level (15% weight)
- **What it measures**: Median weekly income
- **Why it matters**: Higher incomes provide better financial stability and access to amenities
- **Scoring**: Up to 1.5 points (15% of total score)
- **Formula**: `Math.min(1.5, Math.log10(weekly_income / 500) * 0.5)`

## 🏆 Score Interpretation

| Score Range | Rating | Description |
|-------------|--------|-------------|
| 0-2 | Poor | Areas with significant challenges for students |
| 2-4 | Fair | Areas with some student-friendly features but room for improvement |
| 4-6 | Good | Areas with decent student amenities and affordability |
| 6-8 | Very Good | Areas with strong student communities and good infrastructure |
| 8-10 | Excellent | Premium student areas with outstanding liveability |

## 🔧 Technical Implementation

### Score Calculation Function
```typescript
function calculateLiveabilityScore(record: any): number {
  // 1. Youth Population (25% weight)
  const youthScore = Math.min(2.5, (record.pct_youth_18_34 || 0) * 10)
  
  // 2. Student Population (20% weight)
  const studentScore = Math.min(2.0, (record.pct_students || 0) * 10)
  
  // 3. Age Factor (15% weight)
  const medianAge = record.median_age || 35
  const ageScore = Math.max(0, Math.min(1.5, (40 - medianAge) / 10))
  
  // 4. Affordability (25% weight)
  const rentToIncomeRatio = record.rent_to_income_ratio || 0.5
  const affordabilityScore = Math.min(2.5, Math.max(0, (0.6 - rentToIncomeRatio) * 10))
  
  // 5. Income Level (15% weight)
  const weeklyIncome = record.median_weekly_income || 1000
  const incomeScore = Math.min(1.5, Math.log10(weeklyIncome / 500) * 0.5)
  
  // Calculate total score (max 10)
  const totalScore = youthScore + studentScore + ageScore + affordabilityScore + incomeScore
  
  // Ensure score is between 0 and 10
  return Math.max(0, Math.min(10, Math.round(totalScore * 100) / 100))
}
```

### Key Features
- **Bounded Range**: Scores are guaranteed to be between 0-10
- **Weighted Components**: Each factor has a specific weight based on importance to students
- **Normalized Values**: All inputs are normalized to prevent any single factor from dominating
- **Robust Handling**: Graceful handling of missing or invalid data

## 📈 Example Calculations

### High-Scoring Area Example
- **Youth Population**: 40% → 2.5 points
- **Student Population**: 30% → 2.0 points
- **Median Age**: 26 → 1.4 points
- **Rent-to-Income**: 0.3 → 2.5 points
- **Weekly Income**: $1200 → 1.2 points
- **Total Score**: 9.6/10 (Excellent)

### Low-Scoring Area Example
- **Youth Population**: 15% → 1.5 points
- **Student Population**: 10% → 1.0 points
- **Median Age**: 45 → 0.0 points
- **Rent-to-Income**: 0.7 → 0.0 points
- **Weekly Income**: $800 → 0.8 points
- **Total Score**: 3.3/10 (Fair)

## 🎨 Dashboard Integration

The liveability score is prominently displayed in the dashboard with:

1. **Summary Cards**: Average liveability score across all areas
2. **Distribution Chart**: Visual breakdown of areas by score range
3. **Top Areas Chart**: Ranking of areas by liveability score
4. **Score Breakdown**: Detailed explanation of scoring components
5. **Color Coding**: Consistent color scheme for score ranges

## 🔄 Data Sources

The scoring system works with:
- **Real Database**: Supabase `sa2_demographics` table
- **Mock Data**: Development fallback with realistic sample data
- **API Endpoint**: `/api/statistics/sa2` provides calculated scores

## 🚀 Benefits

### For Students
- **Clear Guidance**: Easy-to-understand 0-10 scale
- **Relevant Factors**: Focuses on student-specific needs
- **Visual Insights**: Charts and breakdowns for easy interpretation

### For Researchers
- **Transparent Methodology**: Clear calculation process
- **Weighted Approach**: Evidence-based factor importance
- **Reproducible**: Consistent calculation across all areas

### For Policymakers
- **Actionable Insights**: Identifies areas needing improvement
- **Comparative Analysis**: Easy area-to-area comparisons
- **Trend Monitoring**: Can track changes over time

## 🔮 Future Enhancements

Potential improvements to the scoring system:
1. **Additional Factors**: Public transport accessibility, crime rates, cultural amenities
2. **Dynamic Weights**: User-customizable importance of different factors
3. **Temporal Analysis**: Historical score tracking and trends
4. **Seasonal Adjustments**: Account for academic calendar variations
5. **Subjective Data**: Integration of student surveys and feedback

This scoring system provides a comprehensive, student-focused evaluation of Melbourne's liveability that is both scientifically sound and practically useful. 