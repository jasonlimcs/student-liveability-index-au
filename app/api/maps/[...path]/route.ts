import { NextRequest, NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import { join } from 'path'

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  try {
    const filePath = join(process.cwd(), 'output', ...params.path)
    
    // Security check: ensure the path is within the output directory
    const resolvedPath = join(process.cwd(), 'output')
    if (!filePath.startsWith(resolvedPath)) {
      return NextResponse.json({ error: 'Invalid path' }, { status: 400 })
    }

    const content = await readFile(filePath, 'utf-8')
    
    return new NextResponse(content, {
      headers: {
        'Content-Type': 'text/html',
        'Cache-Control': 'public, max-age=3600',
      },
    })
  } catch (error) {
    console.error('Error serving map file:', error)
    return NextResponse.json(
      { error: 'Map file not found' },
      { status: 404 }
    )
  }
} 