import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  FileText,
  CheckCircle,
  Clock,
  AlertTriangle,
  TrendingUp,
  DollarSign,
  Download
} from 'lucide-react';
import { useDashboard } from '../hooks/useApi';
import StatsCard from '../components/StatsCard';

const ExporterDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: dashboardData, isLoading, error } = useDashboard('exporter');

  const handleUploadClick = () => {
    navigate('/export-lc-upload');
  };

  const handleViewResults = (jobId: string) => {
    navigate(`/exporter-results/${jobId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle size={48} className="text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Unable to Load Dashboard</h2>
          <p className="text-gray-600 mb-4">There was an error loading your dashboard data.</p>
          <button
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Exporter Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Manage your LC validations and export documentation
              </p>
            </div>
            <button
              onClick={handleUploadClick}
              className="btn-primary flex items-center gap-2"
            >
              <Upload size={18} />
              Upload New LC
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Validations"
            value={dashboardData?.total_validations || 0}
            subtitle="lifetime validations"
            icon={FileText}
            color="blue"
          />

          <StatsCard
            title="Successful Validations"
            value={dashboardData?.successful_validations || 0}
            subtitle={`${Math.round(((dashboardData?.successful_validations || 0) / (dashboardData?.total_validations || 1)) * 100)}% success rate`}
            icon={CheckCircle}
            trend={{
              value: 5.2,
              isPositive: true
            }}
            color="green"
          />

          <StatsCard
            title="Pending Corrections"
            value={dashboardData?.pending_corrections || 0}
            subtitle="awaiting action"
            icon={Clock}
            color="yellow"
          />

          <StatsCard
            title="Avg Processing Time"
            value={dashboardData?.average_processing_time || "2.3 min"}
            subtitle="per validation"
            icon={TrendingUp}
            trend={{
              value: -12.5,
              isPositive: true
            }}
            color="green"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Recent Validations */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Recent Validations</h2>
                <button className="text-sm font-medium text-green-600 hover:text-green-700">
                  View All
                </button>
              </div>

              <div className="card">
                <div className="p-6">
                  {dashboardData?.recent_jobs && dashboardData.recent_jobs.length > 0 ? (
                    <div className="space-y-4">
                      {dashboardData.recent_jobs.slice(0, 5).map((job) => (
                        <div
                          key={job.job_id}
                          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <div className="flex-shrink-0">
                              {job.status === 'completed' && <CheckCircle size={20} className="text-green-500" />}
                              {job.status === 'processing' && <Clock size={20} className="text-blue-500" />}
                              {job.status === 'failed' && <AlertTriangle size={20} className="text-red-500" />}
                              {job.status === 'pending' && <Clock size={20} className="text-gray-400" />}
                            </div>

                            <div>
                              <h3 className="font-medium text-gray-900">
                                Job {job.job_id.slice(-8)}
                              </h3>
                              <p className="text-sm text-gray-600">
                                {new Date(job.created_at).toLocaleDateString()} • {job.status}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            {job.status === 'completed' && (
                              <>
                                <button
                                  onClick={() => handleViewResults(job.job_id)}
                                  className="text-sm font-medium text-green-600 hover:text-green-700 px-3 py-1.5 border border-green-200 rounded-md hover:bg-green-50 transition-colors"
                                >
                                  View Results
                                </button>
                                <button className="text-sm font-medium text-gray-600 hover:text-gray-700 px-3 py-1.5 border border-gray-200 rounded-md hover:bg-gray-50 transition-colors flex items-center gap-1">
                                  <Download size={14} />
                                  Download
                                </button>
                              </>
                            )}
                            {(job.status === 'processing' || job.status === 'pending') && (
                              <span className="text-sm text-gray-500">Processing...</span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <FileText size={48} className="text-gray-300 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No validations yet</h3>
                      <p className="text-gray-600 mb-4">
                        Upload your first LC to get started with validation and compliance checking.
                      </p>
                      <button
                        onClick={handleUploadClick}
                        className="btn-primary flex items-center gap-2"
                      >
                        <Upload size={18} />
                        Upload LC Documents
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </section>

            {/* Quick Tips */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Export Tips & Best Practices
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="card p-6">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                    <CheckCircle size={20} className="text-green-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">Document Checklist</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Letter of Credit (LC)</li>
                    <li>• Commercial Invoice</li>
                    <li>• Packing List</li>
                    <li>• Bill of Lading</li>
                    <li>• Certificate of Origin</li>
                    <li>• Insurance Certificate</li>
                  </ul>
                </div>

                <div className="card p-6">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <Clock size={20} className="text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">Processing Times</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Validation: 1-3 minutes</li>
                    <li>• Standard corrections: 1-2 days</li>
                    <li>• Urgent corrections: 2-4 hours</li>
                    <li>• Customs pack: Instant download</li>
                  </ul>
                </div>
              </div>
            </section>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
              <div className="card p-6 space-y-3">
                <button
                  onClick={handleUploadClick}
                  className="w-full btn-primary flex items-center justify-center gap-2"
                >
                  <Upload size={18} />
                  Upload New LC
                </button>
                <button className="w-full btn-secondary flex items-center justify-center gap-2">
                  <FileText size={18} />
                  View All Results
                </button>
                <button className="w-full btn-secondary flex items-center justify-center gap-2">
                  <Download size={18} />
                  Download Reports
                </button>
              </div>
            </section>

            {/* Support */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Need Help?</h2>
              <div className="card p-6">
                <div className="text-center">
                  <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileText size={24} className="text-green-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">Export Documentation Guide</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Learn about LC requirements, common issues, and best practices.
                  </p>
                  <button className="btn-secondary w-full text-sm">
                    View Guide
                  </button>
                </div>
              </div>
            </section>

            {/* System Status */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
              <div className="card p-6">
                <div className="flex items-center gap-2 text-green-600 mb-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium">All systems operational</span>
                </div>
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>API Response:</span>
                    <span className="text-green-600">98ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Processing Queue:</span>
                    <span className="text-green-600">Empty</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Success Rate:</span>
                    <span className="text-green-600">99.7%</span>
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

export default ExporterDashboard;