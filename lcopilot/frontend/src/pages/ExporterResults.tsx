import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Download,
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Edit3,
  RefreshCw
} from 'lucide-react';
import { useJob, useResults } from '../hooks/useApi';
import RiskCard from '../components/RiskCard';
import DocumentList from '../components/DocumentList';

const ExporterResults: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [showAllIssues, setShowAllIssues] = useState(false);

  const { data: job, isLoading: jobLoading } = useJob(jobId!, {
    enabled: !!jobId,
    refetchInterval: (data) => data?.status === 'completed' ? false : 3000
  });

  const { data: results, isLoading: resultsLoading } = useResults(jobId!, {
    enabled: !!jobId && job?.status === 'completed'
  });

  const isLoading = jobLoading || resultsLoading;

  const handleRequestCorrections = () => {
    navigate(`/exporter-document-corrections/${jobId}`);
  };

  const handleDownloadCustomsPack = () => {
    // Simulate download
    const link = document.createElement('a');
    link.href = '#';
    link.download = `customs-pack-${jobId}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">
            {job?.status === 'processing' ? 'Processing your documents...' : 'Loading results...'}
          </p>
          {job?.status === 'processing' && (
            <p className="text-sm text-gray-500 mt-2">
              This usually takes 1-3 minutes
            </p>
          )}
        </div>
      </div>
    );
  }

  if (!results || !job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle size={48} className="text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Results Not Found</h2>
          <p className="text-gray-600 mb-4">
            Unable to load validation results for job {jobId}
          </p>
          <button
            onClick={() => navigate('/exporter-dashboard')}
            className="btn-primary"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const highPriorityIssues = results.results.issues.filter(
    issue => issue.severity === 'critical' || issue.severity === 'high'
  );

  const displayedIssues = showAllIssues ? results.results.issues : highPriorityIssues;

  const getComplianceStatus = () => {
    if (results.results.overall_compliance) {
      return {
        status: 'Compliant',
        color: 'text-green-600',
        bg: 'bg-green-50',
        icon: CheckCircle
      };
    }

    const criticalIssues = results.results.issues.filter(i => i.severity === 'critical').length;
    if (criticalIssues > 0) {
      return {
        status: 'Critical Issues',
        color: 'text-red-600',
        bg: 'bg-red-50',
        icon: AlertTriangle
      };
    }

    return {
      status: 'Needs Attention',
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      icon: AlertTriangle
    };
  };

  const complianceStatus = getComplianceStatus();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/exporter-dashboard')}
            className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 mb-4 transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>

          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Validation Results</h1>
              <p className="text-gray-600 mt-1">
                Job {jobId} • Processed on {new Date(job.created_at).toLocaleDateString()}
              </p>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => window.location.reload()}
                className="btn-secondary flex items-center gap-2"
              >
                <RefreshCw size={16} />
                Refresh
              </button>
            </div>
          </div>
        </div>

        {/* Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className={`card p-6 ${complianceStatus.bg}`}>
            <div className="flex items-center gap-3">
              <complianceStatus.icon size={24} className={complianceStatus.color} />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {complianceStatus.status}
                </h3>
                <p className="text-sm text-gray-600">Overall compliance status</p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
                <span className="text-sm font-bold text-blue-600">
                  {results.results.risk_score}
                </span>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {results.results.risk_score}% Risk Score
                </h3>
                <p className="text-sm text-gray-600">
                  {results.results.risk_score < 30 ? 'Low risk' :
                   results.results.risk_score < 70 ? 'Medium risk' : 'High risk'}
                </p>
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center gap-3">
              <FileText size={24} className="text-gray-400" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900">
                  {results.results.documents.length} Documents
                </h3>
                <p className="text-sm text-gray-600">
                  {results.results.documents.filter(d => d.status === 'verified').length} verified
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Issues & Recommendations */}
            <section>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-gray-900">
                  Issues & Recommendations
                </h2>
                {results.results.issues.length > highPriorityIssues.length && (
                  <button
                    onClick={() => setShowAllIssues(!showAllIssues)}
                    className="text-sm font-medium text-green-600 hover:text-green-700"
                  >
                    {showAllIssues ? 'Show High Priority Only' : `Show All ${results.results.issues.length} Issues`}
                  </button>
                )}
              </div>

              {displayedIssues.length === 0 ? (
                <div className="card p-8 text-center">
                  <CheckCircle size={48} className="text-green-500 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    No Issues Found
                  </h3>
                  <p className="text-gray-600">
                    Your documents are compliant and ready for customs clearance.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {displayedIssues.map((issue, index) => (
                    <RiskCard
                      key={index}
                      risk={{
                        id: `issue-${index}`,
                        title: issue.description,
                        description: issue.recommendation,
                        category: issue.category as any,
                        level: issue.severity,
                        priority: issue.severity === 'critical' ? 1 : issue.severity === 'high' ? 2 : 3,
                        businessImpacts: [
                          {
                            type: 'regulatory',
                            severity: issue.severity,
                            description: `Compliance issue in ${issue.category}`,
                          }
                        ],
                        recommendations: [issue.recommendation],
                        affectedDocuments: issue.affected_documents,
                        detectedAt: new Date(job.created_at),
                        lastUpdated: new Date(),
                      }}
                      showFullDetails={false}
                    />
                  ))}
                </div>
              )}
            </section>

            {/* Document Analysis */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Document Analysis
              </h2>

              <DocumentList
                documents={results.results.documents.map((doc, index) => ({
                  id: `doc-${index}`,
                  name: doc.name,
                  type: 'other' as any,
                  status: doc.status as any,
                  uploadDate: new Date(job.created_at),
                  lastModified: new Date(job.created_at),
                  size: 1024 * 1024, // Mock size
                  issues: doc.issues,
                }))}
                showActions={false}
                compact={false}
              />
            </section>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Actions */}
            <section className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Next Steps
              </h3>

              <div className="space-y-3">
                {results.results.overall_compliance ? (
                  <>
                    <button
                      onClick={handleDownloadCustomsPack}
                      className="w-full btn-primary flex items-center justify-center gap-2"
                    >
                      <Download size={18} />
                      Download Customs-Ready Pack
                    </button>
                    <p className="text-xs text-gray-500 text-center">
                      All documents are compliant and ready for export
                    </p>
                  </>
                ) : (
                  <>
                    <button
                      onClick={handleRequestCorrections}
                      className="w-full btn-primary flex items-center justify-center gap-2"
                    >
                      <Edit3 size={18} />
                      Request Document Corrections
                    </button>
                    <button
                      onClick={handleDownloadCustomsPack}
                      className="w-full btn-secondary flex items-center justify-center gap-2"
                    >
                      <Download size={18} />
                      Download Current Pack
                    </button>
                    <p className="text-xs text-gray-500 text-center">
                      Corrections recommended before final export
                    </p>
                  </>
                )}
              </div>
            </section>

            {/* Job Details */}
            <section className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Job Details
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Job ID:</span>
                  <span className="font-mono text-gray-900">{jobId}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className="flex items-center gap-1">
                    {job.status === 'completed' && <CheckCircle size={14} className="text-green-500" />}
                    {job.status === 'processing' && <Clock size={14} className="text-blue-500" />}
                    {job.status === 'failed' && <AlertTriangle size={14} className="text-red-500" />}
                    <span className="capitalize">{job.status}</span>
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Created:</span>
                  <span className="text-gray-900">
                    {new Date(job.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Processing Time:</span>
                  <span className="text-gray-900">2.3 minutes</span>
                </div>
              </div>
            </section>

            {/* Export Summary */}
            <section className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Export Summary
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                  <span className="text-gray-600">Validation Fee</span>
                  <span className="font-semibold text-gray-900">৳150</span>
                </div>

                {!results.results.overall_compliance && highPriorityIssues.length > 0 && (
                  <>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span className="text-gray-600">Correction Services</span>
                      <span className="text-sm text-gray-500">Est. ৳{highPriorityIssues.length * 300}</span>
                    </div>
                    <div className="bg-yellow-50 p-3 rounded-lg">
                      <p className="text-xs text-yellow-800">
                        Correction fees apply only if you request our correction services.
                      </p>
                    </div>
                  </>
                )}

                <div className="pt-2">
                  <div className="text-xs text-gray-500 text-center">
                    Questions about fees? <a href="#" className="text-green-600 hover:text-green-700">Contact support</a>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExporterResults;