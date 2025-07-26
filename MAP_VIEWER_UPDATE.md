# Map Viewer Update - Full Page Combined Map

## Changes Made

### 1. Updated Main Page (`app/page.tsx`)
- Modified the Maps tab to show only the combined map instead of both maps side by side
- Changed the layout from a 2-column grid to a single full-width map
- Updated the title to "Interactive Combined Liveability Map"

### 2. Enhanced MapViewer Component (`app/components/MapViewer.tsx`)
- Added `fullHeight` prop to support full-screen map display
- Implemented dynamic container classes:
  - `fullHeight={true}`: Uses `h-screen` for full viewport height
  - `fullHeight={false}`: Uses `h-96` for standard height (384px)
- Improved styling with rounded corners and shadow
- Removed dependency on the old `.map-container` CSS class

### 3. Updated CSS (`app/globals.css`)
- Removed the old `.map-container` CSS class since we're now using dynamic Tailwind classes
- Kept the `.stat-card` styles for the dashboard

## How It Works

### Dashboard Tab
- Shows both maps side by side in smaller containers
- Maps use standard height (`h-96`)
- Maintains the original layout with statistics dashboard

### Maps Tab
- Shows only the combined liveability map
- Map takes up the full screen height (`h-screen`)
- Provides an immersive, full-page map experience
- Perfect for detailed exploration of the liveability data

## Benefits

1. **Better User Experience**: Full-screen map allows for better interaction and exploration
2. **Focused View**: Users can concentrate on the combined analysis without distractions
3. **Responsive Design**: Map adapts to different screen sizes
4. **Flexible Component**: MapViewer can be used in both full-height and standard modes

## Usage

- **Dashboard Tab**: Overview with both maps and statistics
- **Maps Tab**: Full-page combined liveability map
- **About Tab**: Project information

The Maps tab now provides an optimal viewing experience for the combined liveability analysis map, making it easier for users to explore the detailed data and interact with the map features. 