# Melbourne Student Liveability Dashboard

A modern Next.js web application that displays interactive maps and comprehensive statistics for the Melbourne Student Liveability Index.

## Features

- **Interactive Maps**: View amenities distribution and combined liveability analysis maps
- **Statistics Dashboard**: Comprehensive charts and metrics showing liveability data
- **Responsive Design**: Modern UI that works on desktop and mobile devices
- **Real-time Data**: API endpoints serving data from processed CSV files

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
app/
├── components/           # React components
│   ├── Navigation.tsx   # Navigation bar with tabs
│   ├── MapViewer.tsx    # Component for displaying HTML maps
│   └── StatisticsDashboard.tsx # Dashboard with charts and stats
├── api/                 # API routes
│   ├── maps/[...path]/route.ts # Serves HTML map files
│   └── statistics/      # Statistics API endpoints
│       ├── amenities/route.ts
│       └── suburbs/route.ts
├── globals.css          # Global styles with Tailwind CSS
├── layout.tsx           # Root layout component
└── page.tsx             # Main page component
```

## Data Sources

The dashboard uses data from the following sources:
- **Amenities Data**: `data/processed/melbourne_amenities_improved_20250718_175145_cleaned_20250718_191258.csv`
- **Demographics Data**: `data/processed/abs_demographics_merged.csv`
- **HTML Maps**: `output/melbourne_amenities_map.html` and `output/melbourne_combined_map.html`

## API Endpoints

- `GET /api/maps/[filename]` - Serves HTML map files
- `GET /api/statistics/amenities` - Returns amenities distribution data
- `GET /api/statistics/suburbs` - Returns suburb liveability statistics

## Technologies Used

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - React charting library
- **Lucide React** - Icon library

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Customization

1. **Styling**: Modify `app/globals.css` and `tailwind.config.js`
2. **Components**: Edit components in `app/components/`
3. **Data**: Update API routes in `app/api/` to use different data sources
4. **Maps**: Replace HTML files in `output/` directory

## Deployment

The application can be deployed to various platforms:

- **Vercel** (recommended for Next.js)
- **Netlify**
- **AWS Amplify**
- **Docker** containerization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is part of the Melbourne Student Liveability Index research. 