export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI Chat
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Asynchronous LLM chat application
        </p>
        <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full">
          <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
          Frontend is running
        </div>
      </div>
    </main>
  )
}
