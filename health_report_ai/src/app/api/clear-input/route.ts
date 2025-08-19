import { NextResponse } from 'next/server';
import { readdir, unlink } from 'fs/promises';
import path from 'path';

export async function POST() {
  try {
    const inputDir = path.join(process.cwd(), 'input');
    
    // Read all files in the input directory
    const files = await readdir(inputDir);
    
    // Delete each file
    await Promise.all(
      files.map(file => unlink(path.join(inputDir, file)))
    );

    return NextResponse.json({ 
      success: true, 
      message: 'Input directory cleared successfully',
      deletedFiles: files.length
    });
  } catch (error) {
    console.error('Error clearing input directory:', error);
    return NextResponse.json({ 
      success: false, 
      message: 'Error clearing input directory' 
    });
  }
}
