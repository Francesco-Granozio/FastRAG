import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Navbar from './components/Layout/Navbar';
import PDFUpload from './components/Upload/PDFUpload';
import QueryForm from './components/Query/QueryForm';
import FilesList from './components/Files/FilesList';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-slate-900 text-slate-100">
          <Navbar />
          <main className="ml-64 max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route
                path="/"
                element={
                  <div className="space-y-12">
                    <PDFUpload />
                    <div className="border-t border-slate-700 pt-12">
                      <QueryForm />
                    </div>
                  </div>
                }
              />
              <Route path="/files" element={<FilesList />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;

