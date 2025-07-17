import React from 'react';
import { Clock, Users, TrendingUp, DollarSign, Heart, Brain } from 'lucide-react';

const MetricsDisplay = ({ metrics }) => {
  const metricCards = [
    {
      title: 'Patients Waiting',
      value: metrics.patients_waiting || 0,
      icon: Users,
      color: 'blue',
      trend: null
    },
    {
      title: 'Avg Wait Time',
      value: `${Math.round(metrics.average_wait_time || 0)} min`,
      icon: Clock,
      color: 'yellow',
      baseline: 28,
      current: metrics.average_wait_time || 0
    },
    {
      title: 'Satisfaction',
      value: `${Math.round(metrics.average_satisfaction || 50)}%`,
      icon: Heart,
      color: 'green',
      baseline: 72,
      current: metrics.average_satisfaction || 50
    },
    {
      title: 'Provider Utilization',
      value: `${Math.round((metrics.provider_utilization || 0) * 100)}%`,
      icon: TrendingUp,
      color: 'purple',
      optimal: 85
    },
    {
      title: 'Cost per Visit',
      value: `$${Math.round(metrics.cost_per_visit || 150)}`,
      icon: DollarSign,
      color: 'indigo',
      baseline: 185,
      current: metrics.cost_per_visit || 150
    },
    {
      title: 'Mental Health Access',
      value: `${Math.round(metrics.mental_health_access || 0)}%`,
      icon: Brain,
      color: 'pink',
      target: 90
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 text-blue-600',
      yellow: 'bg-yellow-50 text-yellow-600',
      green: 'bg-green-50 text-green-600',
      purple: 'bg-purple-50 text-purple-600',
      indigo: 'bg-indigo-50 text-indigo-600',
      pink: 'bg-pink-50 text-pink-600'
    };
    return colors[color] || colors.blue;
  };

  const getTrend = (current, baseline) => {
    if (!baseline || !current) return null;
    const change = ((current - baseline) / baseline) * 100;
    return {
      value: Math.abs(Math.round(change)),
      direction: current < baseline ? 'down' : 'up',
      positive: current < baseline // For wait time and cost, down is good
    };
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {metricCards.map((metric, index) => {
        const Icon = metric.icon;
        const colorClasses = getColorClasses(metric.color);
        const trend = metric.baseline ? getTrend(metric.current, metric.baseline) : null;
        
        return (
          <div key={index} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-medium text-gray-600">{metric.title}</p>
              <Icon className={`w-4 h-4 ${colorClasses}`} />
            </div>
            <p className="text-xl font-bold text-gray-900">
              {metric.value}
            </p>
            {trend && (
              <p className={`text-xs mt-1 ${trend.positive ? 'text-green-600' : 'text-red-600'}`}>
                {trend.direction === 'down' ? '↓' : '↑'} {trend.value}%
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default MetricsDisplay;