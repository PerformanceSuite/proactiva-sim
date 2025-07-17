import React from 'react';
import { AlertCircle, TrendingUp, Lightbulb, AlertTriangle } from 'lucide-react';

const InsightPanel = ({ insights }) => {
  const getInsightIcon = (type) => {
    switch (type) {
      case 'wait_time_crisis':
      case 'capacity_crisis':
        return AlertTriangle;
      case 'innovation_success':
      case 'social_network_pattern':
        return TrendingUp;
      case 'resource_optimization':
      case 'temporal_pattern':
        return Lightbulb;
      default:
        return AlertCircle;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return 'border-red-200 bg-red-50';
      case 'medium':
        return 'border-yellow-200 bg-yellow-50';
      case 'low':
        return 'border-green-200 bg-green-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-lg font-semibold mb-4">AI-Discovered Insights</h3>
      
      {insights.length === 0 ? (
        <p className="text-gray-500 text-sm">
          Insights will appear here as the AI analyzes patterns...
        </p>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {insights.map((insight, index) => {
            const Icon = getInsightIcon(insight.type);
            const colorClass = getSeverityColor(insight.severity);
            
            return (
              <div
                key={insight.id || index}
                className={`p-4 rounded-lg border ${colorClass} transition-all hover:shadow-md`}
              >
                <div className="flex items-start">
                  <Icon className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 text-sm">
                      {insight.title}
                    </h4>
                    <p className="text-xs text-gray-600 mt-1">
                      {insight.description}
                    </p>
                    {insight.recommendation && (
                      <p className="text-xs font-medium text-gray-800 mt-2">
                        💡 {insight.recommendation}
                      </p>
                    )}
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-gray-500">
                        Confidence: {Math.round(insight.confidence * 100)}%
                      </span>
                      {insight.impact?.patients_affected && (
                        <span className="text-xs text-gray-500">
                          Affects: {insight.impact.patients_affected} patients
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default InsightPanel;