import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ToastProvider } from './components/Toast';

// Pages
import LandingPage from './pages/LandingPage';
import ExporterDashboard from './pages/ExporterDashboard';
import ExportLCUpload from './pages/ExportLCUpload';
import ExporterResults from './pages/ExporterResults';
import ExporterDocumentCorrections from './pages/ExporterDocumentCorrections';
import ImporterDashboard from './pages/ImporterDashboard';
import ImportLCUpload from './pages/ImportLCUpload';

import './App.css';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Error Boundary
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<{ children: ReactNode }, ErrorBoundaryState> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      );
    }

    return this.props.children;
  }
}


function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <Router>
            <div className="min-h-screen">
              <Routes>
                {/* Landing Page */}
                <Route path="/" element={<LandingPage />} />

                {/* Exporter Flow */}
                <Route path="/exporter-dashboard" element={<ExporterDashboard />} />
                <Route path="/export-lc-upload" element={<ExportLCUpload />} />
                <Route path="/exporter-results/:jobId" element={<ExporterResults />} />
                <Route path="/exporter-document-corrections/:jobId" element={<ExporterDocumentCorrections />} />

                {/* Importer Flow */}
                <Route path="/importer-dashboard" element={<ImporterDashboard />} />
                <Route path="/import-lc-upload" element={<ImportLCUpload />} />
                {/* <Route path="/draft-lc-risk-results/:jobId" element={<DraftLCRiskResults />} />
                <Route path="/draft-lc-corrections/:jobId" element={<DraftLCCorrections />} />
                <Route path="/supplier-document-results/:jobId" element={<SupplierDocumentResults />} />
                <Route path="/supplier-document-corrections/:jobId" element={<SupplierDocumentCorrections />} /> */}
              </Routes>
            </div>
          </Router>
        </ToastProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;