import React, { useState } from 'react';
import { Send, Clock, AlertTriangle, CheckCircle } from 'lucide-react';
import { useAmendments, type AmendmentRequest } from '../hooks/useApi';
import { useToast } from './Toast';

interface Issue {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: string;
  description: string;
  recommendation: string;
  affected_documents: string[];
}

interface CorrectionFormProps {
  jobId: string;
  issues: Issue[];
  onSubmit?: (requestId: string) => void;
  userType: 'exporter' | 'importer';
}

const CorrectionForm: React.FC<CorrectionFormProps> = ({
  jobId,
  issues,
  onSubmit,
  userType
}) => {
  const [selectedIssues, setSelectedIssues] = useState<string[]>([]);
  const [correctionType, setCorrectionType] = useState<'urgent' | 'standard' | 'next_shipment'>('standard');
  const [urgencyLevel, setUrgencyLevel] = useState<'low' | 'medium' | 'high'>('medium');
  const [notes, setNotes] = useState('');

  const { showToast } = useToast();
  const amendmentMutation = useAmendments();

  const handleIssueToggle = (issueId: string) => {
    setSelectedIssues(prev =>
      prev.includes(issueId)
        ? prev.filter(id => id !== issueId)
        : [...prev, issueId]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedIssues.length === 0) {
      showToast({
        type: 'warning',
        title: 'No Issues Selected',
        message: 'Please select at least one issue to request corrections for.'
      });
      return;
    }

    try {
      const amendmentData: AmendmentRequest = {
        job_id: jobId,
        selected_issues: selectedIssues,
        correction_type: correctionType,
        urgency_level: urgencyLevel,
        notes: notes.trim() || undefined
      };

      const result = await amendmentMutation.mutateAsync(amendmentData);

      showToast({
        type: 'success',
        title: 'Correction Request Submitted',
        message: `Request ID: ${result.request_id}. You will be notified when corrections are ready.`
      });

      onSubmit?.(result.request_id);
    } catch (error) {
      showToast({
        type: 'error',
        title: 'Submission Failed',
        message: error instanceof Error ? error.message : 'An error occurred while submitting the correction request.'
      });
    }
  };

  const getSeverityBadge = (severity: Issue['severity']) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'high':
        return 'bg-orange-100 text-orange-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
    }
  };

  const getSeverityIcon = (severity: Issue['severity']) => {
    return severity === 'critical' || severity === 'high'
      ? <AlertTriangle size={16} />
      : <CheckCircle size={16} />;
  };

  const getEstimatedTime = () => {
    switch (correctionType) {
      case 'urgent':
        return '2-4 hours';
      case 'standard':
        return '1-2 business days';
      case 'next_shipment':
        return '5-7 business days';
    }
  };

  const getEstimatedCost = () => {
    const baseRate = userType === 'exporter' ? 500 : 750;
    const urgencyMultiplier = correctionType === 'urgent' ? 2 : correctionType === 'standard' ? 1.5 : 1;
    const selectedCount = selectedIssues.length;

    return Math.round(baseRate * urgencyMultiplier * selectedCount);
  };

  return (
    <div className="space-y-6">
      {/* Issues Selection */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Select Issues to Correct
        </h3>
        <div className="space-y-3">
          {issues.map((issue) => (
            <label
              key={issue.id}
              className="flex items-start gap-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <input
                type="checkbox"
                checked={selectedIssues.includes(issue.id)}
                onChange={() => handleIssueToggle(issue.id)}
                className="mt-1 h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300 rounded"
              />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityBadge(issue.severity)}`}>
                    {getSeverityIcon(issue.severity)}
                    {issue.severity.toUpperCase()}
                  </span>
                  <span className="text-sm text-gray-600 capitalize">{issue.category}</span>
                </div>

                <h4 className="font-medium text-gray-900 mb-1">
                  {issue.description}
                </h4>

                <p className="text-sm text-gray-600 mb-2">
                  <strong>Recommendation:</strong> {issue.recommendation}
                </p>

                {issue.affected_documents.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {issue.affected_documents.map((doc, index) => (
                      <span key={index} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600">
                        {doc}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Correction Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Correction Type
          </h3>
          <div className="space-y-3">
            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="correctionType"
                value="urgent"
                checked={correctionType === 'urgent'}
                onChange={(e) => setCorrectionType(e.target.value as any)}
                className="h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300"
              />
              <div>
                <div className="font-medium text-gray-900">Urgent</div>
                <div className="text-sm text-gray-600">Rush processing - same day delivery</div>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="correctionType"
                value="standard"
                checked={correctionType === 'standard'}
                onChange={(e) => setCorrectionType(e.target.value as any)}
                className="h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300"
              />
              <div>
                <div className="font-medium text-gray-900">Standard</div>
                <div className="text-sm text-gray-600">Normal processing timeline</div>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="correctionType"
                value="next_shipment"
                checked={correctionType === 'next_shipment'}
                onChange={(e) => setCorrectionType(e.target.value as any)}
                className="h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300"
              />
              <div>
                <div className="font-medium text-gray-900">Next Shipment</div>
                <div className="text-sm text-gray-600">Apply corrections for future shipments</div>
              </div>
            </label>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Priority Level
          </h3>
          <div className="space-y-3">
            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="urgencyLevel"
                value="high"
                checked={urgencyLevel === 'high'}
                onChange={(e) => setUrgencyLevel(e.target.value as any)}
                className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300"
              />
              <div>
                <div className="font-medium text-gray-900">High</div>
                <div className="text-sm text-gray-600">Blocks shipment - immediate attention</div>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="urgencyLevel"
                value="medium"
                checked={urgencyLevel === 'medium'}
                onChange={(e) => setUrgencyLevel(e.target.value as any)}
                className="h-4 w-4 text-yellow-600 focus:ring-yellow-500 border-gray-300"
              />
              <div>
                <div className="font-medium text-gray-900">Medium</div>
                <div className="text-sm text-gray-600">Important but not blocking</div>
              </div>
            </label>

            <label className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer">
              <input
                type="radio"
                name="urgencyLevel"
                value="low"
                checked={urgencyLevel === 'low'}
                onChange={(e) => setUrgencyLevel(e.target.value as any)}
                className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300"
              />
              <div>
                <div className="font-medium text-gray-900">Low</div>
                <div className="text-sm text-gray-600">Nice to have improvements</div>
              </div>
            </label>
          </div>
        </div>
      </div>

      {/* Additional Notes */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Additional Notes (Optional)
        </h3>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Any specific instructions or context for the corrections..."
          rows={4}
          className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-green-500"
        />
      </div>

      {/* Summary & Submit */}
      <div className="bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Request Summary
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{selectedIssues.length}</div>
            <div className="text-sm text-gray-600">Issues Selected</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 flex items-center justify-center gap-1">
              <Clock size={20} />
              {getEstimatedTime()}
            </div>
            <div className="text-sm text-gray-600">Estimated Time</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">৳{getEstimatedCost()}</div>
            <div className="text-sm text-gray-600">Estimated Cost</div>
          </div>
        </div>

        <button
          onClick={handleSubmit}
          disabled={selectedIssues.length === 0 || amendmentMutation.isPending}
          className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {amendmentMutation.isPending ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Submitting...
            </>
          ) : (
            <>
              <Send size={18} />
              Submit Correction Request
            </>
          )}
        </button>

        <p className="text-xs text-gray-500 text-center mt-2">
          You will receive email confirmation and updates on the progress of your correction request.
        </p>
      </div>
    </div>
  );
};

export default CorrectionForm;