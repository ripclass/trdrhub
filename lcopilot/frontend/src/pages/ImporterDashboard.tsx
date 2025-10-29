import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload,
  Shield,
  FileText,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Users,
  DollarSign
} from 'lucide-react';
import { useDashboard } from '../hooks/useApi';
import StatsCard from '../components/StatsCard';

const ImporterDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { data: dashboardData, isLoading, error } = useDashboard('importer');

  const handleUploadClick = () => {
    navigate('/import-lc-upload');
  };

  const handleViewResults = (jobId: string, workflowType?: string) => {
    if (workflowType === 'draft-lc-risk') {
      navigate(`/draft-lc-risk-results/${jobId}`);
    } else {
      navigate(`/supplier-document-results/${jobId}`);
    }
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
              <h1 className="text-2xl font-bold text-gray-900">Importer Dashboard</h1>
              <p className="text-gray-600 mt-1">
                Manage LC risk analysis and supplier document validation
              </p>
            </div>
            <button
              onClick={handleUploadClick}
              className="btn-primary flex items-center gap-2"
            >
              <Upload size={18} />
              Upload Documents
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Reviews"
            value={dashboardData?.total_validations || 0}
            subtitle="LC & document reviews"
            icon={FileText}
            color="blue"
          />

          <StatsCard
            title="Risk Assessments"
            value={Math.floor((dashboardData?.total_validations || 0) * 0.6)}
            subtitle="draft LC reviews"
            icon={Shield}
            trend={{
              value: 8.3,
              isPositive: true
            }}
            color="blue"
          />

          <StatsCard
            title="High Risk LCs"
            value={dashboardData?.pending_corrections || 0}
            subtitle="require attention"
            icon={AlertTriangle}
            color="red"
          />

          <StatsCard
            title="Avg Review Time"
            value={dashboardData?.average_processing_time || "1.8 min"}
            subtitle="per assessment"
            icon={TrendingUp}
            trend={{
              value: -15.2,
              isPositive: true
            }}
            color="green"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Recent Reviews */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Recent Reviews</h2>
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
                                {job.workflow_type === 'draft-lc-risk' ? 'Draft LC Risk Review' : 'Supplier Document Check'}
                              </h3>
                              <p className="text-sm text-gray-600">
                                Job {job.job_id.slice(-8)} • {new Date(job.created_at).toLocaleDateString()} • {job.status}
                              </p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            {job.status === 'completed' && (
                              <button
                                onClick={() => handleViewResults(job.job_id, job.workflow_type)}
                                className="text-sm font-medium text-green-600 hover:text-green-700 px-3 py-1.5 border border-green-200 rounded-md hover:bg-green-50 transition-colors"
                              >
                                View Results
                              </button>
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
                      <Shield size={48} className="text-gray-300 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No reviews yet</h3>
                      <p className="text-gray-600 mb-4">
                        Upload your first LC or supplier documents to get started with risk analysis.
                      </p>
                      <button
                        onClick={handleUploadClick}
                        className="btn-primary flex items-center gap-2"
                      >
                        <Upload size={18} />
                        Upload Documents
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </section>

            {/* Import Workflows */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Choose Your Workflow
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Draft LC Risk Analysis */}
                <div className="card p-6 hover:shadow-md transition-shadow cursor-pointer"
                     onClick={() => navigate('/import-lc-upload?workflow=draft-lc-risk')}>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                    <Shield size={24} className="text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Draft LC Risk Analysis
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Upload draft LC from your bank for comprehensive risk assessment
                    and clause analysis before finalization.
                  </p>
                  <ul className="space-y-2 text-sm text-gray-600 mb-4">
                    <li className="flex items-center gap-2">
                      <CheckCircle size={14} className="text-green-500" />
                      <span>Clause risk assessment</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle size={14} className="text-green-500" />
                      <span>UCP 600 compliance check</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle size={14} className="text-green-500" />
                      <span>Amendment recommendations</span>
                    </li>
                  </ul>
                  <button className="btn-primary w-full text-sm">
                    Start Risk Analysis
                  </button>
                </div>

                {/* Supplier Document Check */}
                <div className="card p-6 hover:shadow-md transition-shadow cursor-pointer"
                     onClick={() => navigate('/import-lc-upload?workflow=supplier-document-check')}>
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                    <FileText size={24} className="text-green-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Supplier Document Check
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Upload supplier's documents for compliance verification
                    against your LC terms and requirements.
                  </p>
                  <ul className="space-y-2 text-sm text-gray-600 mb-4">
                    <li className="flex items-center gap-2">
                      <CheckCircle size={14} className="text-green-500" />
                      <span>Document authenticity check</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle size={14} className="text-green-500" />
                      <span>LC compliance verification</span>
                    </li>
                    <li className="flex items-center gap-2">
                      <CheckCircle size={14} className="text-green-500" />
                      <span>Discrepancy identification</span>
                    </li>
                  </ul>
                  <button className="btn-primary w-full text-sm">
                    Check Documents
                  </button>
                </div>
              </div>
            </section>

            {/* Best Practices */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Import Best Practices
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="card p-6">
                  <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mb-4">
                    <AlertTriangle size={20} className="text-red-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">Common Risk Factors</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Ambiguous document requirements</li>
                    <li>• Tight presentation deadlines</li>
                    <li>• Complex shipping terms</li>
                    <li>• Multiple transhipment points</li>
                    <li>• Unusual payment terms</li>
                  </ul>
                </div>

                <div className="card p-6">
                  <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                    <Users size={20} className="text-green-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">When to Review</h3>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li>• Before LC finalization</li>
                    <li>• Upon document receipt</li>
                    <li>• Before payment authorization</li>
                    <li>• When discrepancies are noted</li>
                    <li>• For first-time suppliers</li>
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
                  onClick={() => navigate('/import-lc-upload?workflow=draft-lc-risk')}
                  className="w-full btn-primary flex items-center justify-center gap-2"
                >
                  <Shield size={18} />
                  LC Risk Analysis
                </button>
                <button
                  onClick={() => navigate('/import-lc-upload?workflow=supplier-document-check')}
                  className="w-full btn-secondary flex items-center justify-center gap-2"
                >
                  <FileText size={18} />
                  Check Supplier Docs
                </button>
                <button className="w-full btn-secondary flex items-center justify-center gap-2">
                  <TrendingUp size={18} />
                  View Risk Reports
                </button>
              </div>
            </section>

            {/* Risk Alerts */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Alerts</h2>
              <div className="card p-6">
                <div className="space-y-4">
                  <div className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
                    <AlertTriangle size={16} className="text-red-500 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-medium text-red-900">High Risk LC Detected</h4>
                      <p className="text-xs text-red-700 mt-1">
                        Draft LC contains ambiguous shipment terms
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg">
                    <Clock size={16} className="text-yellow-500 mt-0.5" />
                    <div>
                      <h4 className="text-sm font-medium text-yellow-900">Review Pending</h4>
                      <p className="text-xs text-yellow-700 mt-1">
                        2 supplier document sets awaiting review
                      </p>
                    </div>
                  </div>
                </div>

                <button className="w-full mt-4 text-sm font-medium text-green-600 hover:text-green-700 py-2">
                  View All Alerts
                </button>
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
                    <span>Risk Analysis:</span>
                    <span className="text-green-600">Online</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Document Processing:</span>
                    <span className="text-green-600">Normal</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Response:</span>
                    <span className="text-green-600">1.2s</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Support */}
            <section>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Need Help?</h2>
              <div className="card p-6">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Shield size={24} className="text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-2">LC Risk Guide</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Learn about common LC risks, red flags, and mitigation strategies.
                  </p>
                  <button className="btn-secondary w-full text-sm">
                    View Guide
                  </button>
                </div>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImporterDashboard;