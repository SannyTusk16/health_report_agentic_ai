
export default function Home() {
  return (
    <div className="min-h-screen bg-black font-mono text-white">
      {/* Main Content */}
      <main className="flex flex-col items-center justify-center min-h-screen px-4 py-16">
        <div className="w-full max-w-2xl text-center space-y-8">
          <h1 className="text-6xl font-light text-white mb-8">Health Reports</h1>
          
          {/* Large Upload Area */}
          <div className="border-2 border-white border-dashed rounded-1xl p-16 bg-transparent hover:bg-white/5 transition-colors duration-200">
            <form className="flex flex-col items-center gap-6 w-full">
              <div className="text-4xl mb-4">+</div>
              <label htmlFor="file-upload" className="text-lg font-light cursor-pointer">
                Drop files here or click to upload
              </label>
              <input
                id="file-upload"
                type="file"
                accept=".pdf,.doc,.docx"
                multiple
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <p className="text-sm text-gray-400 font-light">PDF, DOC, DOCX</p>
            </form>
          </div>
        </div>
      </main>
    </div>
  );
}
