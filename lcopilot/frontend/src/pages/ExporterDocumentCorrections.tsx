import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, AlertTriangle } from 'lucide-react';
import { useResults } from '../hooks/useApi';
import CorrectionForm from '../components/CorrectionForm';

const ExporterDocumentCorrections: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  const { data: results, isLoading, error } = useResults(jobId!, {
    enabled: !!jobId
  });

  const handleSubmitSuccess = (requestId: string) => {
    navigate(`/exporter-results/${jobId}`, {
      state: { correctionRequestId: requestId }
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading validation results...</p>
        </div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle size={48} className="text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Results</h2>
          <p className="text-gray-600 mb-4">
            Cannot load validation results for job {jobId}
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => navigate('/exporter-dashboard')}
              className="btn-secondary"
            >
              Back to Dashboard
            </button>
            <button
              onClick={() => window.location.reload()}
              className="btn-primary"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const issues = results.results.issues.map((issue, index) => ({
    id: `issue-${index}`,
    severity: issue.severity,
    category: issue.category,
    description: issue.description,
    recommendation: issue.recommendation,
    affected_documents: issue.affected_documents
  }));

  if (issues.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <button
            onClick={() => navigate(`/exporter-results/${jobId}`)}
            className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Results
          </button>

          <div className="text-center py-20">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertTriangle size={24} className="text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              No Corrections Needed
            </h2>
            <p className="text-gray-600 mb-6">
              Your documents are fully compliant. No correction requests are required.
            </p>
            <button
              onClick={() => navigate(`/exporter-results/${jobId}`)}
              className="btn-primary"
            >
              Back to Results
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate(`/exporter-results/${jobId}`)}
            className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Results
          </button>

          <div>
            <h1 className="text-2xl font-bold text-gray-900">Request Document Corrections</h1>
            <p className="text-gray-600 mt-1">
              Select issues you'd like corrected and specify your requirements
            </p>
          </div>
        </div>

        {/* Info Banner */}
        <div className="card p-6 mb-8 bg-blue-50 border-blue-200">
          <div className="flex items-start gap-3">
            <div className="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
              <AlertTriangle size={16} className="text-blue-600" />
            </div>
            <div>
              <h3 className="font-medium text-blue-900 mb-1">
                About Correction Services
              </h3>
              <p className="text-sm text-blue-800 mb-3">
                Our expert team will review your documents and provide corrected versions based on your
                specifications. Corrections typically take 1-2 business days for standard requests.
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium text-blue-900">Standard:</span>
                  <span className="text-blue-800"> 1-2 business days</span>
                </div>
                <div>
                  <span className="font-medium text-blue-900">Urgent:</span>
                  <span className="text-blue-800"> 2-4 hours</span>
                </div>
                <div>
                  <span className="font-medium text-blue-900">Quality:</span>
                  <span className="text-blue-800"> 99.7% accuracy</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Correction Form */}
        <div className="card p-8">
          <CorrectionForm
            jobId={jobId!}
            issues={issues}
            onSubmit={handleSubmitSuccess}
            userType="exporter"
          />
        </div>

        {/* Help Section */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Correction Types Explained
            </h3>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-gray-900">Urgent</h4>
                <p className="text-sm text-gray-600">
                  Rush processing for time-sensitive shipments. Documents delivered within 2-4 hours.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Standard</h4>
                <p className="text-sm text-gray-600">
                  Normal processing timeline with thorough review. Ideal for most export transactions.
                </p>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Next Shipment</h4>
                <p className="text-sm text-gray-600">
                  Corrections applied to document templates for future shipments. Best for recurring issues.
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              What's Included
            </h3>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                <span>Expert review by trade documentation specialists</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                <span>Corrected documents in original format</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                <span>Compliance verification and re-validation</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                <span>Email notifications on progress updates</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                <span>Customer support throughout the process</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                <span>Final customs-ready documentation pack</span>
              </div>
            </div>
          </div>
        </div>

        {/* Contact Support */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600">
            Have questions about corrections or need assistance?{' '}
            <a href="#" className="text-green-600 hover:text-green-700 font-medium">
              Contact our support team
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default ExporterDocumentCorrections;