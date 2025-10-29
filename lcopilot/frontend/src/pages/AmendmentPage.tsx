import React, { useState } from 'react';
import { ArrowLeft, Edit3, Send, Clock, CheckCircle, AlertTriangle, DollarSign } from 'lucide-react';

interface Amendment {
  id: string;
  type: 'beneficiary' | 'amount' | 'expiry' | 'documents' | 'terms' | 'other';
  title: string;
  description: string;
  currentValue: string;
  proposedValue: string;
  reason: string;
  estimatedCost: string;
  processingTime: string;
  status: 'draft' | 'submitted' | 'approved' | 'rejected';
  submittedAt?: Date;
  updatedAt: Date;
}

const AmendmentPage: React.FC = () => {
  const [amendments, setAmendments] = useState<Amendment[]>([
    {
      id: 'amend-1',
      type: 'beneficiary',
      title: 'Beneficiary Name Correction',
      description: 'Correct beneficiary name to match invoice exactly',
      currentValue: 'ACME Trading Co Ltd',
      proposedValue: 'ACME Trading Company Limited',
      reason: 'Name mismatch between LC and supporting documents causing compliance issues',
      estimatedCost: '$350',
      processingTime: '2-3 business days',
      status: 'draft',
      updatedAt: new Date(),
    },
    {
      id: 'amend-2',
      type: 'expiry',
      title: 'LC Expiry Extension',
      description: 'Extend LC expiry date to allow sufficient processing time',
      currentValue: '2024-03-15',
      proposedValue: '2024-03-30',
      reason: 'Current expiry date creates tight timeline for document processing',
      estimatedCost: '$200',
      processingTime: '1-2 business days',
      status: 'submitted',
      submittedAt: new Date(Date.now() - 1000 * 60 * 60 * 6),
      updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 6),
    },
  ]);

  const [newAmendment, setNewAmendment] = useState<Partial<Amendment>>({
    type: 'beneficiary',
    title: '',
    description: '',
    currentValue: '',
    proposedValue: '',
    reason: '',
  });

  const [showNewAmendmentForm, setShowNewAmendmentForm] = useState(false);

  const getAmendmentTypeLabel = (type: Amendment['type']) => {
    switch (type) {
      case 'beneficiary': return 'Beneficiary Details';
      case 'amount': return 'LC Amount';
      case 'expiry': return 'Expiry Date';
      case 'documents': return 'Document Requirements';
      case 'terms': return 'Terms & Conditions';
      case 'other': return 'Other';
    }
  };

  const getStatusIcon = (status: Amendment['status']) => {
    switch (status) {
      case 'draft': return <Edit3 size={16} className="text-gray-500" />;
      case 'submitted': return <Clock size={16} className="text-blue-500" />;
      case 'approved': return <CheckCircle size={16} className="text-green-500" />;
      case 'rejected': return <AlertTriangle size={16} className="text-red-500" />;
    }
  };

  const getStatusBadge = (status: Amendment['status']) => {
    switch (status) {
      case 'draft': return 'status-badge bg-gray-100 text-gray-700';
      case 'submitted': return 'status-badge bg-blue-100 text-blue-800';
      case 'approved': return 'status-badge status-verified';
      case 'rejected': return 'status-badge status-high';
    }
  };

  const handleCreateAmendment = () => {
    if (!newAmendment.title || !newAmendment.currentValue || !newAmendment.proposedValue) {
      return;
    }

    const amendment: Amendment = {
      id: `amend-${Date.now()}`,
      type: newAmendment.type || 'other',
      title: newAmendment.title,
      description: newAmendment.description || '',
      currentValue: newAmendment.currentValue,
      proposedValue: newAmendment.proposedValue,
      reason: newAmendment.reason || '',
      estimatedCost: '$250-500',
      processingTime: '2-3 business days',
      status: 'draft',
      updatedAt: new Date(),
    };

    setAmendments([amendment, ...amendments]);
    setNewAmendment({
      type: 'beneficiary',
      title: '',
      description: '',
      currentValue: '',
      proposedValue: '',
      reason: '',
    });
    setShowNewAmendmentForm(false);
  };

  const handleSubmitAmendment = (amendmentId: string) => {
    setAmendments(amendments.map(amend =>
      amend.id === amendmentId
        ? { ...amend, status: 'submitted', submittedAt: new Date() }
        : amend
    ));
  };

  const handleDeleteAmendment = (amendmentId: string) => {
    setAmendments(amendments.filter(amend => amend.id !== amendmentId));
  };

  const draftAmendments = amendments.filter(a => a.status === 'draft');
  const submittedAmendments = amendments.filter(a => a.status !== 'draft');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 mb-4">
            <ArrowLeft size={16} />
            Back to Risk Analysis
          </button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">LC Amendments</h1>
              <p className="text-gray-600 mt-1">
                Create and manage amendments to address compliance issues
              </p>
            </div>
            <button
              onClick={() => setShowNewAmendmentForm(true)}
              className="btn-primary flex items-center gap-2"
            >
              <Edit3 size={18} />
              New Amendment
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* New Amendment Form */}
            {showNewAmendmentForm && (
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Create New Amendment
                </h2>

                <div className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Amendment Type
                      </label>
                      <select
                        value={newAmendment.type}
                        onChange={(e) => setNewAmendment({...newAmendment, type: e.target.value as Amendment['type']})}
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-green-500"
                      >
                        <option value="beneficiary">Beneficiary Details</option>
                        <option value="amount">LC Amount</option>
                        <option value="expiry">Expiry Date</option>
                        <option value="documents">Document Requirements</option>
                        <option value="terms">Terms & Conditions</option>
                        <option value="other">Other</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Amendment Title
                      </label>
                      <input
                        type="text"
                        value={newAmendment.title}
                        onChange={(e) => setNewAmendment({...newAmendment, title: e.target.value})}
                        placeholder="Brief description of amendment"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-green-500"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Current Value
                    </label>
                    <input
                      type="text"
                      value={newAmendment.currentValue}
                      onChange={(e) => setNewAmendment({...newAmendment, currentValue: e.target.value})}
                      placeholder="Current value in LC"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-green-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Proposed Value
                    </label>
                    <input
                      type="text"
                      value={newAmendment.proposedValue}
                      onChange={(e) => setNewAmendment({...newAmendment, proposedValue: e.target.value})}
                      placeholder="New value to be amended"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-green-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Reason for Amendment
                    </label>
                    <textarea
                      value={newAmendment.reason}
                      onChange={(e) => setNewAmendment({...newAmendment, reason: e.target.value})}
                      placeholder="Explain why this amendment is necessary"
                      rows={3}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-green-500"
                    />
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={handleCreateAmendment}
                      className="btn-primary"
                    >
                      Create Amendment
                    </button>
                    <button
                      onClick={() => setShowNewAmendmentForm(false)}
                      className="btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Draft Amendments */}
            {draftAmendments.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Draft Amendments ({draftAmendments.length})
                </h2>
                <div className="space-y-4">
                  {draftAmendments.map((amendment) => (
                    <div key={amendment.id} className="card p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">
                              {amendment.title}
                            </h3>
                            <span className={getStatusBadge(amendment.status)}>
                              {amendment.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">
                            {getAmendmentTypeLabel(amendment.type)}
                          </p>
                        </div>
                        {getStatusIcon(amendment.status)}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">Current</h4>
                          <p className="text-sm text-gray-900 bg-red-50 p-2 rounded">
                            {amendment.currentValue}
                          </p>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">Proposed</h4>
                          <p className="text-sm text-gray-900 bg-green-50 p-2 rounded">
                            {amendment.proposedValue}
                          </p>
                        </div>
                      </div>

                      {amendment.reason && (
                        <div className="mb-4">
                          <h4 className="text-sm font-medium text-gray-700 mb-1">Reason</h4>
                          <p className="text-sm text-gray-600">{amendment.reason}</p>
                        </div>
                      )}

                      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          <div className="flex items-center gap-1">
                            <DollarSign size={16} />
                            <span>Est. Cost: {amendment.estimatedCost}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <Clock size={16} />
                            <span>{amendment.processingTime}</span>
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <button
                            onClick={() => handleSubmitAmendment(amendment.id)}
                            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-white bg-green-500 hover:bg-green-600 rounded-md"
                          >
                            <Send size={14} />
                            Submit
                          </button>
                          <button
                            onClick={() => handleDeleteAmendment(amendment.id)}
                            className="px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-red-600 rounded-md"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Submitted Amendments */}
            {submittedAmendments.length > 0 && (
              <section>
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Amendment History
                </h2>
                <div className="space-y-4">
                  {submittedAmendments.map((amendment) => (
                    <div key={amendment.id} className="card p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="text-lg font-medium text-gray-900">
                              {amendment.title}
                            </h3>
                            <span className={getStatusBadge(amendment.status)}>
                              {amendment.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">
                            {getAmendmentTypeLabel(amendment.type)} •{' '}
                            {amendment.submittedAt?.toLocaleDateString()}
                          </p>
                        </div>
                        {getStatusIcon(amendment.status)}
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">Changed From</h4>
                          <p className="text-sm text-gray-900">{amendment.currentValue}</p>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-700 mb-1">Changed To</h4>
                          <p className="text-sm text-gray-900">{amendment.proposedValue}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Amendment Guidelines */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Amendment Guidelines
              </h3>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <span>All parties must agree to amendments</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Processing typically takes 2-5 business days</span>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Amendment fees apply (varies by complexity)</span>
                </div>
                <div className="flex items-start gap-2">
                  <AlertTriangle size={16} className="text-yellow-500 flex-shrink-0 mt-0.5" />
                  <span>Some amendments may require additional documentation</span>
                </div>
              </div>
            </div>

            {/* Cost Estimator */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Estimated Costs
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Draft amendments</span>
                  <span className="font-medium">$0</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Submitted amendments</span>
                  <span className="font-medium">$550</span>
                </div>
                <div className="border-t border-gray-100 pt-2 flex justify-between">
                  <span className="font-medium text-gray-900">Total estimated</span>
                  <span className="font-semibold text-gray-900">$550</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AmendmentPage;