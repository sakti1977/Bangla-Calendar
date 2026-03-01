import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MonthView } from './components/calendar/MonthView'
import { DayDetailPanel } from './components/dayDetail/DayDetailPanel'
import { RegionToggle } from './components/controls/RegionToggle'
import { TraditionFilter } from './components/controls/TraditionFilter'
import { LocationInput } from './components/controls/LocationInput'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

function AppLayout() {
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-4 flex-wrap shadow-sm">
        <div className="flex items-center gap-2">
          <span className="text-2xl">📅</span>
          <h1 className="text-lg font-bold text-gray-800 bangla-font" lang="bn">
            বাংলা ক্যালেন্ডার
          </h1>
        </div>
        <div className="flex items-center gap-3 ml-auto flex-wrap">
          <LocationInput />
          <RegionToggle />
          <TraditionFilter />
        </div>
      </header>

      {/* Main content: calendar grid + day detail sidebar */}
      <div className="flex flex-1 overflow-hidden">
        <main className="flex-1 overflow-y-auto">
          <MonthView />
        </main>
        <DayDetailPanel />
      </div>
    </div>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppLayout />
    </QueryClientProvider>
  )
}
