import React from 'react';
import { AlertTriangle, TrendingUp, DollarSign, Users, Clock, ChevronRight } from 'lucide-react';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';
export type RiskCategory = 'compliance' | 'financial' | 'operational' | 'reputation';

interface BusinessImpact {
  type: 'financial' | 'operational' | 'reputation' | 'regulatory';
  severity: RiskLevel;
  description: string;
  estimatedCost?: string;
  timeline?: string;
}

export interface Risk {
  id: string;
  title: string;
  description: string;
  category: RiskCategory;
  level: RiskLevel;
  priority: number;
  businessImpacts: BusinessImpact[];
  recommendations: string[];
  affectedDocuments?: string[];
  detectedAt: Date;
  lastUpdated: Date;
}

interface RiskCardProps {
  risk: Risk;
  onViewDetails?: (riskId: string) => void;
  onAcceptRecommendation?: (riskId: string, recommendationIndex: number) => void;
  showFullDetails?: boolean;
}

const RiskCard: React.FC<RiskCardProps> = ({
  risk,
  onViewDetails,
  onAcceptRecommendation,
  showFullDetails = false,
}) => {
  const getRiskLevelStyles = (level: RiskLevel) => {
    switch (level) {
      case 'critical':
        return {
          badge: 'bg-red-100 text-red-800 border-red-200',
          border: 'border-red-200',
          accent: 'bg-red-500',
        };
      case 'high':
        return {
          badge: 'bg-orange-100 text-orange-800 border-orange-200',
          border: 'border-orange-200',
          accent: 'bg-orange-500',
        };
      case 'medium':
        return {
          badge: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          border: 'border-yellow-200',
          accent: 'bg-yellow-500',
        };
      case 'low':
        return {
          badge: 'bg-green-100 text-green-800 border-green-200',
          border: 'border-green-200',
          accent: 'bg-green-500',
        };
    }
  };

  const getCategoryIcon = (category: RiskCategory) => {
    switch (category) {
      case 'compliance':
        return <AlertTriangle size={20} />;
      case 'financial':
        return <DollarSign size={20} />;
      case 'operational':
        return <Users size={20} />;
      case 'reputation':
        return <TrendingUp size={20} />;
    }
  };

  const getImpactIcon = (type: BusinessImpact['type']) => {
    switch (type) {
      case 'financial':
        return <DollarSign size={16} />;
      case 'operational':
        return <Users size={16} />;
      case 'reputation':
        return <TrendingUp size={16} />;
      case 'regulatory':
        return <AlertTriangle size={16} />;
    }
  };

  const styles = getRiskLevelStyles(risk.level);
  const displayRecommendations = showFullDetails ? risk.recommendations : risk.recommendations.slice(0, 2);
  const displayImpacts = showFullDetails ? risk.businessImpacts : risk.businessImpacts.slice(0, 2);

  return (
    <div className={`card border-l-4 ${styles.border} transition-all hover:shadow-md`}>
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${styles.accent}`} />

      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start gap-3 flex-1">
            <div className="flex-shrink-0 mt-0.5 text-gray-600">
              {getCategoryIcon(risk.category)}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-start gap-2 mb-2">
                <h3 className="text-lg font-semibold text-gray-900 truncate flex-1">
                  {risk.title}
                </h3>
                <span className={`status-badge ${styles.badge} flex-shrink-0`}>
                  {risk.level.toUpperCase()}
                </span>
              </div>

              <p className="text-sm text-gray-600 mb-2">
                {risk.description}
              </p>

              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span className="capitalize">{risk.category}</span>
                <span>Priority: {risk.priority}</span>
                <div className="flex items-center gap-1">
                  <Clock size={12} />
                  <span>Updated {risk.lastUpdated.toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Business Impacts */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Business Impact</h4>
          <div className="space-y-2">
            {displayImpacts.map((impact, index) => (
              <div key={index} className="flex items-start gap-2 p-2 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0 mt-0.5 text-gray-500">
                  {getImpactIcon(impact.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-gray-700 capitalize">
                      {impact.type}
                    </span>
                    <span className={`status-badge ${getRiskLevelStyles(impact.severity).badge}`}>
                      {impact.severity}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600">{impact.description}</p>
                  {(impact.estimatedCost || impact.timeline) && (
                    <div className="flex items-center gap-3 mt-1 text-xs text-gray-500">
                      {impact.estimatedCost && <span>Cost: {impact.estimatedCost}</span>}
                      {impact.timeline && <span>Timeline: {impact.timeline}</span>}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {!showFullDetails && risk.businessImpacts.length > 2 && (
              <p className="text-xs text-gray-500 text-center">
                +{risk.businessImpacts.length - 2} more impacts
              </p>
            )}
          </div>
        </div>

        {/* Recommendations */}
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Recommendations</h4>
          <div className="space-y-2">
            {displayRecommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start gap-2 p-2 bg-blue-50 rounded-lg">
                <div className="flex-1">
                  <p className="text-sm text-gray-700">{recommendation}</p>
                </div>
                {onAcceptRecommendation && (
                  <button
                    onClick={() => onAcceptRecommendation(risk.id, index)}
                    className="flex-shrink-0 px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-100 rounded transition-colors"
                  >
                    Apply
                  </button>
                )}
              </div>
            ))}
            {!showFullDetails && risk.recommendations.length > 2 && (
              <p className="text-xs text-gray-500 text-center">
                +{risk.recommendations.length - 2} more recommendations
              </p>
            )}
          </div>
        </div>

        {/* Affected Documents */}
        {risk.affectedDocuments && risk.affectedDocuments.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Affected Documents</h4>
            <div className="flex flex-wrap gap-1">
              {risk.affectedDocuments.slice(0, showFullDetails ? undefined : 3).map((doc, index) => (
                <span key={index} className="status-badge bg-gray-100 text-gray-700 text-xs">
                  {doc}
                </span>
              ))}
              {!showFullDetails && risk.affectedDocuments.length > 3 && (
                <span className="status-badge bg-gray-100 text-gray-500 text-xs">
                  +{risk.affectedDocuments.length - 3}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <div className="flex items-center gap-2">
            {risk.level === 'critical' && (
              <span className="text-xs font-medium text-red-600">Immediate action required</span>
            )}
            {risk.level === 'high' && (
              <span className="text-xs font-medium text-orange-600">Review within 24h</span>
            )}
          </div>

          {onViewDetails && (
            <button
              onClick={() => onViewDetails(risk.id)}
              className="flex items-center gap-1 text-sm font-medium text-green-600 hover:text-green-700 transition-colors"
            >
              {showFullDetails ? 'View Analysis' : 'View Details'}
              <ChevronRight size={16} />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RiskCard;