
'use client';

import { useState } from 'react';

interface UploadedFile {
  name: string;
  size: number;
  type: string;
  file: File;
}

export default function Home() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    const newFiles: UploadedFile[] = [];
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      // Check if file already exists to avoid duplicates
      const fileExists = uploadedFiles.some(existingFile => 
        existingFile.name === file.name && existingFile.size === file.size
      );
      
      if (!fileExists) {
        newFiles.push({
          name: file.name,
          size: file.size,
          type: file.type,
          file: file
        });
      }
    }

    setUploadedFiles(prev => [...prev, ...newFiles]); // Add to existing files
    event.target.value = ''; // Reset input
  };

  const uploadFiles = async () => {
    if (uploadedFiles.length === 0 || isUploading) return;
    
    setIsUploading(true);
    
    try {
      // First, clear the input directory
      await fetch('/api/clear-input', {
        method: 'POST'
      });

      // Then upload all files
      for (const fileData of uploadedFiles) {
        const formData = new FormData();
        formData.append('file', fileData.file);
        
        await fetch('/api/upload', {
          method: 'POST',
          body: formData
        });
      }
      
      console.log('All files uploaded successfully');
      // Clear the selection after successful upload
      setUploadedFiles([]);
    } catch (error) {
      console.error('Error uploading files:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const clearSelection = () => {
    setUploadedFiles([]);
  };

  const removeFile = (indexToRemove: number) => {
    setUploadedFiles(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  // Pixel art cloud component
  const PixelCloud = () => (
    <div className="flex flex-col items-center justify-center mb-4">
      <div className="relative mb-4">
        {/* Pixel art cloud using divs */}
        <div className="cloud-container">
          {/* Row 1 - top */}
          <div className="absolute w-1 h-1 bg-white" style={{top: '8px', left: '24px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '8px', left: '28px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '8px', left: '32px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '8px', left: '36px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '8px', left: '40px'}}></div>
          
          {/* Row 2 */}
          <div className="absolute w-1 h-1 bg-white" style={{top: '12px', left: '16px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '12px', left: '20px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '12px', left: '24px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '12px', left: '28px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '12px', left: '32px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '12px', left: '36px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '12px', left: '40px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '12px', left: '44px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '12px', left: '48px'}}></div>
          
          {/* Row 3 */}
          <div className="absolute w-1 h-1 bg-white" style={{top: '16px', left: '20px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '16px', left: '24px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '16px', left: '28px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '16px', left: '32px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '16px', left: '36px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '16px', left: '40px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '16px', left: '44px'}}></div>
          
          {/* Row 4 - bottom */}
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '12px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '16px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '20px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '24px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '28px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '32px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '36px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '40px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '44px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '48px'}}></div>
          <div className="absolute w-1 h-1 bg-white" style={{top: '20px', left: '52px'}}></div>
          
          {/* Shining pixels */}
          <div className="absolute w-1 h-1 bg-yellow-400 shine-1" style={{top: '6px', left: '28px'}}></div>
          <div className="absolute w-1 h-1 bg-yellow-400 shine-2" style={{top: '14px', left: '36px'}}></div>
          <div className="absolute w-1 h-1 bg-yellow-400 shine-3" style={{top: '18px', left: '24px'}}></div>
        </div>
      </div>
      <div className="text-white text-sm animate-pulse">Uploading to cloud...</div>
    </div>
  );

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.shiftKey && event.key === 'Enter') {
      event.preventDefault();
      uploadFiles();
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const files = event.dataTransfer.files;
    
    if (files) {
      const input = document.getElementById('file-upload') as HTMLInputElement;
      input.files = files;
      input.dispatchEvent(new Event('change', { bubbles: true }));
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="min-h-screen bg-black font-mono text-white focus:outline-none" onKeyDown={handleKeyDown} tabIndex={0}>
      {/* Minimal custom CSS - only animations that Tailwind can't handle */}
      <style jsx global>{`
        .cloud-container {
          position: relative;
          width: 70px;
          height: 32px;
          animation: cloudFloat 3s ease-in-out infinite;
        }
        
        .shine-1 {
          animation: sparkle 2s infinite;
          animation-delay: 0s;
        }
        
        .shine-2 {
          animation: sparkle 2s infinite;
          animation-delay: 0.7s;
        }
        
        .shine-3 {
          animation: sparkle 2s infinite;
          animation-delay: 1.4s;
        }
        
        @keyframes sparkle {
          0%, 20% {
            opacity: 0;
            transform: scale(0.5);
          }
          10% {
            opacity: 1;
            transform: scale(1.5);
            box-shadow: 0 0 8px #ffff00;
          }
          100% {
            opacity: 0;
            transform: scale(0.5);
          }
        }
        
        @keyframes cloudFloat {
          0%, 100% {
            transform: translateY(0px);
          }
          50% {
            transform: translateY(-6px);
          }
        }
      `}</style>
      
      {/* Upload Animation Overlay */}
      {isUploading && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-12 border-2 border-gray-600 shadow-2xl">
            <PixelCloud />
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="flex flex-col items-center justify-center min-h-screen px-4 py-16">
        <div className="w-full max-w-2xl text-center space-y-8">
          <h1 className="text-6xl font-light text-white mb-8 drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] [text-shadow:0_0_10px_rgba(255,255,255,0.2),0_0_15px_rgba(255,255,255,0.1),0_0_20px_rgba(255,255,255,0.05)]">
            Health Reports
          </h1>
          
          {/* Large Upload Area */}
          <div 
            className="border-2 border-white border-dashed rounded-xl p-16 bg-transparent shadow-[0_0_15px_rgba(255,255,255,0.08),0_0_30px_rgba(255,255,255,0.04),inset_0_0_15px_rgba(255,255,255,0.02)] hover:shadow-[0_0_20px_rgba(255,255,255,0.12),0_0_40px_rgba(255,255,255,0.06),inset_0_0_20px_rgba(255,255,255,0.04)] transition-all duration-300 relative"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <form className="flex flex-col items-center gap-6 w-full">
              <div className="text-4xl mb-4 drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] [text-shadow:0_0_10px_rgba(255,255,255,0.2)]">+</div>
              <label htmlFor="file-upload" className="text-lg font-light cursor-pointer drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] [text-shadow:0_0_10px_rgba(255,255,255,0.2)]">
                Drop files here or click to upload
              </label>
              <input
                id="file-upload"
                type="file"
                accept=".pdf,.doc,.docx"
                multiple
                onChange={handleFileSelect}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <p className="text-sm text-gray-400 font-light drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] [text-shadow:0_0_5px_rgba(255,255,255,0.1)]">PDF, DOC, DOCX</p>
            </form>
          </div>

          {/* Uploaded Files Display */}
          {uploadedFiles.length > 0 && (
            <div className="w-full max-w-2xl">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-light drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] [text-shadow:0_0_10px_rgba(255,255,255,0.2)]">
                  {isUploading ? 'Uploading...' : `${uploadedFiles.length} file(s) selected - (Shift + Enter) to Upload`}
                </h2>
                {!isUploading && (
                  <button
                    onClick={clearSelection}
                    className="text-sm text-gray-400 hover:text-white border border-gray-600 px-3 py-1 rounded shadow-[0_0_8px_rgba(255,255,255,0.05),0_0_16px_rgba(255,255,255,0.03)] hover:shadow-[0_0_12px_rgba(255,255,255,0.08),0_0_24px_rgba(255,255,255,0.04)] transition-all duration-200"
                  >
                    Clear Selection
                  </button>
                )}
              </div>
              <div className="grid grid-cols-4 gap-4 max-h-96 overflow-y-auto p-4 border border-gray-600 rounded-lg shadow-[0_0_10px_rgba(255,255,255,0.1),0_0_20px_rgba(255,255,255,0.05),inset_0_0_10px_rgba(255,255,255,0.03)]">
                {uploadedFiles.map((file, index) => (
                  <div
                    key={index}
                    onClick={() => removeFile(index)}
                    className="aspect-square border border-gray-500 rounded-lg p-3 bg-gray-900 hover:bg-red-900 hover:border-red-500 transition-all duration-200 flex flex-col justify-between text-xs cursor-pointer group relative shadow-[0_0_8px_rgba(255,255,255,0.06),0_0_16px_rgba(255,255,255,0.03),inset_0_0_8px_rgba(255,255,255,0.02)] hover:shadow-[0_0_12px_rgba(239,68,68,0.3),0_0_24px_rgba(239,68,68,0.15),inset_0_0_12px_rgba(239,68,68,0.05)]"
                    title="Click to remove file"
                  >
                    {/* Remove indicator */}
                    <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                      <span className="text-red-400 text-lg drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] [text-shadow:0_0_5px_rgba(255,255,255,0.1)]">×</span>
                    </div>
                    
                    <div className="flex-1 flex items-center justify-center">
                      <div className="text-center w-full">
                        <div className="text-2xl mb-2 drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] [text-shadow:0_0_5px_rgba(255,255,255,0.1)]">📄</div>
                        <div 
                          className="font-light w-full overflow-hidden text-ellipsis break-words text-center leading-tight drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] [text-shadow:0_0_5px_rgba(255,255,255,0.1)]"
                          title={file.name}
                          style={{
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden',
                            wordBreak: 'break-word',
                            fontSize: '0.65rem',
                            lineHeight: '0.9rem'
                          }}
                        >
                          {file.name}
                        </div>
                      </div>
                    </div>
                    <div className="text-gray-400 text-center text-xs mt-1 drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] [text-shadow:0_0_5px_rgba(255,255,255,0.1)]">
                      {formatFileSize(file.size)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
