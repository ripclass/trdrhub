import React, { useState, useEffect } from 'react';
import { Upload, FileText, AlertTriangle, TrendingUp, Users, DollarSign } from 'lucide-react';
import StatsCard from '../components/StatsCard';
import NotificationList from '../components/NotificationList';
import RiskCard from '../components/RiskCard';
import DocumentList from '../components/DocumentList';
import type { Risk } from '../components/RiskCard';

const DashboardPage: React.FC = () => {
  const [notifications, setNotifications] = useState([
    {
      id: '1',
      title: 'Document Analysis Complete',
      message: 'LC_2024_001.pdf has been successfully analyzed. No critical issues found.',
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
      status: 'success' as const,
      read: false,
    },
    {
      id: '2',
      title: 'High Risk Alert',
      message: 'Multiple compliance issues detected in recent submission. Review required.',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
      status: 'error' as const,
      read: false,
    },
    {
      id: '3',
      title: 'Amendment Processed',
      message: 'Amendment for LC_2024_001 has been processed and approved.',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4),
      status: 'info' as const,
      read: true,
    },
  ]);

  const [risks, setRisks] = useState<Risk[]>([
    {
      id: 'risk-1',
      title: 'Beneficiary Name Mismatch',
      description: 'The beneficiary name in the LC does not exactly match the invoice beneficiary.',
      category: 'compliance',
      level: 'high',
      priority: 1,
      businessImpacts: [
        {
          type: 'regulatory',
          severity: 'high',
          description: 'May cause payment delays or rejection by banks',
          timeline: '1-2 business days',
        },
        {
          type: 'financial',
          severity: 'medium',
          description: 'Potential additional fees for amendments',
          estimatedCost: '$250-500',
        },
      ],
      recommendations: [
        'Request amendment to correct beneficiary name in LC',
        'Verify all supporting documents use consistent naming',
        'Update company records to ensure name consistency',
      ],
      affectedDocuments: ['LC_2024_001.pdf', 'Invoice_INV_001.pdf'],
      detectedAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
      lastUpdated: new Date(Date.now() - 1000 * 60 * 30),
    },
    {
      id: 'risk-2',
      title: 'Expired Certificate of Origin',
      description: 'The certificate of origin has expired and may not be accepted.',
      category: 'compliance',
      level: 'medium',
      priority: 2,
      businessImpacts: [
        {
          type: 'operational',
          severity: 'medium',
          description: 'Shipment may be delayed at customs',
          timeline: '2-5 business days',
        },
      ],
      recommendations: [
        'Obtain new certificate of origin',
        'Contact supplier to provide updated certificate',
      ],
      affectedDocuments: ['Certificate_Origin_001.pdf'],
      detectedAt: new Date(Date.now() - 1000 * 60 * 60 * 6),
      lastUpdated: new Date(Date.now() - 1000 * 60 * 60 * 1),
    },
  ]);

  const [documents, setDocuments] = useState([
    {
      id: 'doc-1',
      name: 'LC_2024_001.pdf',
      type: 'LC' as const,
      status: 'verified' as const,
      uploadDate: new Date(Date.now() - 1000 * 60 * 60 * 24),
      lastModified: new Date(Date.now() - 1000 * 60 * 60 * 2),
      size: 1024 * 1024 * 2.5,
      riskScore: 25,
      downloadUrl: '/api/documents/doc-1/download',
    },
    {
      id: 'doc-2',
      name: 'Invoice_INV_001.pdf',
      type: 'invoice' as const,
      status: 'warning' as const,
      uploadDate: new Date(Date.now() - 1000 * 60 * 60 * 20),
      lastModified: new Date(Date.now() - 1000 * 60 * 60 * 1),
      size: 1024 * 512,
      riskScore: 65,
      issues: ['Beneficiary name mismatch with LC', 'Minor calculation discrepancy'],
      downloadUrl: '/api/documents/doc-2/download',
    },
    {
      id: 'doc-3',
      name: 'Certificate_Origin_001.pdf',
      type: 'certificate' as const,
      status: 'error' as const,
      uploadDate: new Date(Date.now() - 1000 * 60 * 60 * 48),
      lastModified: new Date(Date.now() - 1000 * 60 * 60 * 48),
      size: 1024 * 256,
      riskScore: 85,
      issues: ['Certificate has expired', 'Invalid signature format'],
      downloadUrl: '/api/documents/doc-3/download',
    },
  ]);

  const handleMarkNotificationAsRead = (id: string) => {
    setNotifications(notifications.map(notif =>
      notif.id === id ? { ...notif, read: true } : notif
    ));
  };

  const handleDismissNotification = (id: string) => {
    setNotifications(notifications.filter(notif => notif.id !== id));
  };

  const handleViewRiskDetails = (riskId: string) => {
    console.log('View risk details:', riskId);
  };

  const handleAcceptRecommendation = (riskId: string, recommendationIndex: number) => {
    console.log('Accept recommendation:', riskId, recommendationIndex);
  };

  const handleViewDocument = (document: any) => {
    console.log('View document:', document);
  };

  const handleDownloadDocument = (document: any) => {
    console.log('Download document:', document);
    window.open(document.downloadUrl, '_blank');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Overview of your LC documents and risk analysis</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Documents"
            value={documents.length}
            subtitle="3 processed today"
            icon={FileText}
            trend={{ value: 12.5, isPositive: true }}
            color="blue"
          />

          <StatsCard
            title="Active Risks"
            value={risks.length}
            subtitle="1 high priority"
            icon={AlertTriangle}
            trend={{ value: -8.2, isPositive: true }}
            color="red"
          />

          <StatsCard
            title="Processing Time"
            value="2.3 min"
            subtitle="avg per document"
            icon={TrendingUp}
            trend={{ value: -15.8, isPositive: true }}
            color="green"
          />

          <StatsCard
            title="Cost Savings"
            value="$2,450"
            subtitle="this month"
            icon={DollarSign}
            trend={{ value: 23.1, isPositive: true }}
            color="green"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Recent Documents & Risks */}
          <div className="lg:col-span-2 space-y-8">
            {/* Recent Documents */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Recent Documents</h2>
                <button className="text-sm font-medium text-green-600 hover:text-green-700">
                  View All
                </button>
              </div>
              <DocumentList
                documents={documents}
                onView={handleViewDocument}
                onDownload={handleDownloadDocument}
                compact={true}
              />
            </section>

            {/* Active Risks */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Active Risks</h2>
                <button className="text-sm font-medium text-green-600 hover:text-green-700">
                  View All
                </button>
              </div>
              <div className="space-y-4">
                {risks.map((risk) => (
                  <RiskCard
                    key={risk.id}
                    risk={risk}
                    onViewDetails={handleViewRiskDetails}
                    onAcceptRecommendation={handleAcceptRecommendation}
                  />
                ))}
              </div>
            </section>
          </div>

          {/* Right Column - Notifications */}
          <div className="space-y-8">
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
                <button className="text-sm font-medium text-green-600 hover:text-green-700">
                  View All
                </button>
              </div>
              <NotificationList
                notifications={notifications}
                onMarkAsRead={handleMarkNotificationAsRead}
                onDismiss={handleDismissNotification}
                maxItems={5}
              />
            </section>

            {/* Quick Actions */}
            <section>
              <div className="mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
              </div>
              <div className="card p-6 space-y-3">
                <button className="w-full btn-primary flex items-center justify-center gap-2">
                  <Upload size={18} />
                  Upload New Document
                </button>
                <button className="w-full btn-secondary flex items-center justify-center gap-2">
                  <FileText size={18} />
                  View Risk Analysis
                </button>
                <button className="w-full btn-secondary flex items-center justify-center gap-2">
                  <TrendingUp size={18} />
                  Export Report
                </button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;