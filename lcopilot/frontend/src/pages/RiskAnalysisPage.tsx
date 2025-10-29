import React, { useState } from 'react';
import { ArrowLeft, Filter, Download, AlertTriangle, TrendingUp, DollarSign, Users } from 'lucide-react';
import RiskCard from '../components/RiskCard';
import StatsCard from '../components/StatsCard';
import type { Risk } from '../components/RiskCard';

const RiskAnalysisPage: React.FC = () => {
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'critical' | 'high' | 'medium' | 'low'>('all');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'compliance' | 'financial' | 'operational' | 'reputation'>('all');

  const [risks] = useState<Risk[]>([
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
        'Contact issuing bank immediately to discuss amendment process',
      ],
      affectedDocuments: ['LC_2024_001.pdf', 'Invoice_INV_001.pdf'],
      detectedAt: new Date(Date.now() - 1000 * 60 * 60 * 2),
      lastUpdated: new Date(Date.now() - 1000 * 60 * 30),
    },
    {
      id: 'risk-2',
      title: 'Expired Certificate of Origin',
      description: 'The certificate of origin has expired and may not be accepted by customs authorities.',
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
        {
          type: 'financial',
          severity: 'low',
          description: 'Demurrage charges may apply',
          estimatedCost: '$100-300 per day',
        },
      ],
      recommendations: [
        'Obtain new certificate of origin from authorized issuing authority',
        'Contact supplier to provide updated certificate',
        'Verify certificate validity dates before shipment',
      ],
      affectedDocuments: ['Certificate_Origin_001.pdf'],
      detectedAt: new Date(Date.now() - 1000 * 60 * 60 * 6),
      lastUpdated: new Date(Date.now() - 1000 * 60 * 60 * 1),
    },
    {
      id: 'risk-3',
      title: 'Currency Code Inconsistency',
      description: 'Different currency codes used across LC and supporting documents.',
      category: 'financial',
      level: 'medium',
      priority: 3,
      businessImpacts: [
        {
          type: 'financial',
          severity: 'medium',
          description: 'Exchange rate fluctuations may affect payment amount',
          estimatedCost: '1-3% of transaction value',
        },
      ],
      recommendations: [
        'Standardize currency codes across all documents',
        'Consider currency hedging options',
      ],
      affectedDocuments: ['LC_2024_001.pdf', 'Invoice_INV_001.pdf'],
      detectedAt: new Date(Date.now() - 1000 * 60 * 60 * 8),
      lastUpdated: new Date(Date.now() - 1000 * 60 * 60 * 4),
    },
    {
      id: 'risk-4',
      title: 'Late Shipment Date',
      description: 'Shipment date is within 48 hours of LC expiry, creating tight timeline.',
      category: 'operational',
      level: 'low',
      priority: 4,
      businessImpacts: [
        {
          type: 'operational',
          severity: 'low',
          description: 'Limited time for document processing',
          timeline: '48 hours',
        },
      ],
      recommendations: [
        'Process documents with highest priority',
        'Consider requesting LC extension if needed',
        'Prepare contingency plans for document delays',
      ],
      affectedDocuments: ['LC_2024_001.pdf'],
      detectedAt: new Date(Date.now() - 1000 * 60 * 60 * 12),
      lastUpdated: new Date(Date.now() - 1000 * 60 * 60 * 8),
    },
  ]);

  const filteredRisks = risks.filter(risk => {
    const levelMatch = selectedFilter === 'all' || risk.level === selectedFilter;
    const categoryMatch = selectedCategory === 'all' || risk.category === selectedCategory;
    return levelMatch && categoryMatch;
  });

  const riskStats = {
    critical: risks.filter(r => r.level === 'critical').length,
    high: risks.filter(r => r.level === 'high').length,
    medium: risks.filter(r => r.level === 'medium').length,
    low: risks.filter(r => r.level === 'low').length,
    total: risks.length,
  };

  const handleViewRiskDetails = (riskId: string) => {
    console.log('View risk details:', riskId);
  };

  const handleAcceptRecommendation = (riskId: string, recommendationIndex: number) => {
    console.log('Accept recommendation:', riskId, recommendationIndex);
  };

  const handleExportReport = () => {
    console.log('Export risk analysis report');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 mb-4">
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Risk Analysis</h1>
              <p className="text-gray-600 mt-1">
                Comprehensive risk assessment of your LC documents
              </p>
            </div>
            <button
              onClick={handleExportReport}
              className="flex items-center gap-2 btn-secondary"
            >
              <Download size={18} />
              Export Report
            </button>
          </div>
        </div>

        {/* Risk Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Critical Risks"
            value={riskStats.critical}
            subtitle="require immediate action"
            icon={AlertTriangle}
            color="red"
          />

          <StatsCard
            title="High Risks"
            value={riskStats.high}
            subtitle="review within 24h"
            icon={AlertTriangle}
            color="yellow"
          />

          <StatsCard
            title="Total Risks"
            value={riskStats.total}
            subtitle={`${riskStats.medium + riskStats.low} medium/low`}
            icon={TrendingUp}
            color="blue"
          />

          <StatsCard
            title="Risk Score"
            value="65%"
            subtitle="overall assessment"
            icon={DollarSign}
            trend={{ value: -12, isPositive: true }}
            color="green"
          />
        </div>

        {/* Filters */}
        <div className="card p-6 mb-8">
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <div className="flex items-center gap-2">
              <Filter size={18} className="text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Filter by:</span>
            </div>

            <div className="flex flex-wrap gap-4">
              {/* Risk Level Filter */}
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">Risk Level:</label>
                <select
                  value={selectedFilter}
                  onChange={(e) => setSelectedFilter(e.target.value as any)}
                  className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-primary-500 focus:border-green-500"
                >
                  <option value="all">All Levels</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              {/* Category Filter */}
              <div className="flex items-center gap-2">
                <label className="text-sm text-gray-600">Category:</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value as any)}
                  className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:ring-2 focus:ring-primary-500 focus:border-green-500"
                >
                  <option value="all">All Categories</option>
                  <option value="compliance">Compliance</option>
                  <option value="financial">Financial</option>
                  <option value="operational">Operational</option>
                  <option value="reputation">Reputation</option>
                </select>
              </div>
            </div>

            <div className="ml-auto text-sm text-gray-500">
              Showing {filteredRisks.length} of {riskStats.total} risks
            </div>
          </div>
        </div>

        {/* Risk Cards */}
        <div className="space-y-6">
          {filteredRisks.length === 0 ? (
            <div className="card p-12 text-center">
              <AlertTriangle size={48} className="mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No risks found</h3>
              <p className="text-gray-600">
                No risks match the current filter criteria.
              </p>
            </div>
          ) : (
            filteredRisks.map((risk) => (
              <RiskCard
                key={risk.id}
                risk={risk}
                onViewDetails={handleViewRiskDetails}
                onAcceptRecommendation={handleAcceptRecommendation}
                showFullDetails={true}
              />
            ))
          )}
        </div>

        {/* Summary Section */}
        {filteredRisks.length > 0 && (
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Risk Distribution */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Risk Distribution
              </h3>
              <div className="space-y-3">
                {[
                  { level: 'Critical', count: riskStats.critical, color: 'bg-red-500' },
                  { level: 'High', count: riskStats.high, color: 'bg-orange-500' },
                  { level: 'Medium', count: riskStats.medium, color: 'bg-yellow-500' },
                  { level: 'Low', count: riskStats.low, color: 'bg-green-500' },
                ].map(({ level, count, color }) => (
                  <div key={level} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${color}`} />
                      <span className="text-sm text-gray-700">{level}</span>
                    </div>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations Summary */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Next Steps
              </h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-start gap-2">
                  <AlertTriangle size={16} className="text-red-500 flex-shrink-0 mt-0.5" />
                  <span>
                    Address {riskStats.critical + riskStats.high} high-priority risks immediately
                  </span>
                </div>
                <div className="flex items-start gap-2">
                  <Users size={16} className="text-blue-500 flex-shrink-0 mt-0.5" />
                  <span>
                    Review compliance issues with your legal team
                  </span>
                </div>
                <div className="flex items-start gap-2">
                  <DollarSign size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <span>
                    Consider amendments to reduce financial exposure
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RiskAnalysisPage;