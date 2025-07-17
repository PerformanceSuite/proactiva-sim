"""
AI-powered insight detection engine
"""
import numpy as np
from scipy import stats
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd


class InsightEngine:
    """Detects patterns, anomalies, and optimization opportunities"""
    
    def __init__(self, model):
        self.model = model
        self.insights_history = []
        self.pattern_memory = defaultdict(list)
        self.confidence_threshold = 0.75
        
    def detect_insights(self) -> List[Dict[str, Any]]:
        """Run all insight detection algorithms"""
        insights = []
        
        # Run different types of analysis
        insights.extend(self._detect_wait_time_patterns())
        insights.extend(self._detect_satisfaction_drivers())
        insights.extend(self._detect_bottlenecks())
        insights.extend(self._detect_innovation_effectiveness())
        insights.extend(self._detect_social_network_effects())
        insights.extend(self._detect_temporal_patterns())
        insights.extend(self._detect_resource_optimization())
        
        # Filter and rank insights
        significant_insights = self._filter_insights(insights)
        
        # Store for historical analysis
        self.insights_history.extend(significant_insights)
        
        return significant_insights
        
    def _detect_wait_time_patterns(self) -> List[Dict[str, Any]]:
        """Analyze wait time patterns across different dimensions"""
        insights = []
        
        # Get current agent data
        patients = [a for a in self.model.schedule.agents 
                   if hasattr(a, 'wait_time') and hasattr(a, 'condition')]
        
        if len(patients) < 20:
            return insights
            
        # Group by condition
        condition_waits = defaultdict(list)
        for patient in patients:
            condition_waits[patient.condition.value].append(patient.wait_time)
            
        # Analyze each condition
        for condition, wait_times in condition_waits.items():
            if len(wait_times) >= 5:
                avg_wait = np.mean(wait_times)
                std_wait = np.std(wait_times)
                
                # Check for concerning patterns
                if condition == 'mental_health' and avg_wait > 45:
                    # Check if VR could help
                    vr_potential = self._estimate_vr_impact(wait_times)
                    
                    insights.append({
                        'id': f'wait_pattern_{datetime.now().timestamp()}',
                        'type': 'wait_time_crisis',
                        'severity': 'high',
                        'title': 'Mental Health Wait Times at Critical Level',
                        'description': f'Mental health patients experiencing {avg_wait:.0f} minute average wait times, significantly above acceptable threshold',
                        'recommendation': f'Immediate intervention needed. VR therapy expansion could reduce waits by {vr_potential:.0f}%',
                        'confidence': 0.88,
                        'impact': {
                            'patients_affected': len(wait_times),
                            'current_wait': avg_wait,
                            'potential_reduction': avg_wait * vr_potential / 100
                        },
                        'supporting_data': {
                            'sample_size': len(wait_times),
                            'standard_deviation': std_wait,
                            'max_wait': max(wait_times)
                        }
                    })
                    
                elif avg_wait > 60:  # Any condition with > 1 hour wait
                    insights.append({
                        'id': f'wait_pattern_{datetime.now().timestamp()}',
                        'type': 'excessive_wait',
                        'severity': 'medium',
                        'title': f'{condition.title()} Patients Experiencing Long Waits',
                        'description': f'Average wait time of {avg_wait:.0f} minutes indicates capacity mismatch',
                        'recommendation': 'Consider adding providers or implementing express care pathway',
                        'confidence': 0.82,
                        'impact': {
                            'patients_affected': len(wait_times)
                        }
                    })
                    
        return insights
        
    def _detect_satisfaction_drivers(self) -> List[Dict[str, Any]]:
        """Identify what drives patient satisfaction"""
        insights = []
        
        # Collect patient data
        patient_data = []
        for agent in self.model.schedule.agents:
            if hasattr(agent, 'satisfaction') and hasattr(agent, 'wait_time'):
                patient_data.append({
                    'satisfaction': agent.satisfaction,
                    'wait_time': agent.wait_time,
                    'condition': agent.condition.value if hasattr(agent, 'condition') else 'unknown',
                    'vr_used': getattr(agent, 'used_vr', False),
                    'provider_type': getattr(agent, 'treated_by', 'unknown')
                })
                
        if len(patient_data) < 30:
            return insights
            
        df = pd.DataFrame(patient_data)
        
        # Correlation analysis
        if len(df) > 0:
            wait_satisfaction_corr = df['satisfaction'].corr(df['wait_time'])
            
            if abs(wait_satisfaction_corr) > 0.5:
                insights.append({
                    'id': f'satisfaction_driver_{datetime.now().timestamp()}',
                    'type': 'correlation_found',
                    'severity': 'medium',
                    'title': 'Wait Time Strongly Impacts Satisfaction',
                    'description': f'Statistical analysis shows {abs(wait_satisfaction_corr):.0%} correlation between wait time and satisfaction',
                    'recommendation': 'Focus on wait time reduction as primary satisfaction improvement strategy',
                    'confidence': 0.85,
                    'supporting_data': {
                        'correlation': wait_satisfaction_corr,
                        'sample_size': len(df)
                    }
                })
                
        return insights
        
    def _detect_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify system bottlenecks and constraints"""
        insights = []
        
        # Analyze provider utilization
        providers = [a for a in self.model.schedule.agents 
                    if hasattr(a, 'patients_seen_today')]
        
        if providers:
            # Group by specialty
            specialty_util = defaultdict(list)
            for provider in providers:
                if hasattr(provider, 'specialty'):
                    utilization = provider.patients_seen_today
                    specialty_util[provider.specialty.value].append(utilization)
                    
            # Find imbalances
            avg_utils = {spec: np.mean(utils) for spec, utils in specialty_util.items() 
                        if len(utils) > 0}
            
            if avg_utils:
                overall_avg = np.mean(list(avg_utils.values()))
                
                for specialty, avg_util in avg_utils.items():
                    if avg_util > overall_avg * 1.5:
                        insights.append({
                            'id': f'bottleneck_{datetime.now().timestamp()}',
                            'type': 'resource_bottleneck',
                            'severity': 'high',
                            'title': f'{specialty.replace("_", " ").title()} Department Overwhelmed',
                            'description': f'{specialty} providers seeing {avg_util/overall_avg:.1f}x more patients than average, creating system bottleneck',
                            'recommendation': f'Urgently add {specialty} capacity or redistribute appropriate cases to other departments',
                            'confidence': 0.86,
                            'impact': {
                                'department_load': avg_util,
                                'system_average': overall_avg,
                                'overload_factor': avg_util / overall_avg
                            }
                        })
                        
        # Check waiting room congestion
        if len(self.model.waiting_room) > 50:
            # Analyze waiting room composition
            condition_counts = Counter(p.condition.value for p in self.model.waiting_room 
                                     if hasattr(p, 'condition'))
            
            most_common = condition_counts.most_common(1)[0] if condition_counts else ('unknown', 0)
            
            insights.append({
                'id': f'congestion_{datetime.now().timestamp()}',
                'type': 'capacity_crisis',
                'severity': 'high',
                'title': 'Waiting Room Reaching Critical Capacity',
                'description': f'{len(self.model.waiting_room)} patients waiting, with {most_common[0]} cases most prevalent',
                'recommendation': 'Activate surge protocols: open overflow areas, call in additional staff, implement fast-track for low-acuity cases',
                'confidence': 0.92,
                'impact': {
                    'patients_waiting': len(self.model.waiting_room),
                    'primary_condition': most_common[0],
                    'condition_count': most_common[1]
                }
            })
            
        return insights
        
    def _detect_innovation_effectiveness(self) -> List[Dict[str, Any]]:
        """Measure effectiveness of innovations like VR, telehealth"""
        insights = []
        
        # VR effectiveness
        if self.model.vr_stations > 0:
            vr_utilization = self.model.vr_sessions_completed / max(self.model.schedule.time, 1)
            
            if vr_utilization < 0.5:  # Under-utilized
                insights.append({
                    'id': f'vr_underuse_{datetime.now().timestamp()}',
                    'type': 'innovation_underutilization',
                    'severity': 'medium',
                    'title': 'VR Therapy Stations Underutilized',
                    'description': f'Only {vr_utilization:.0%} utilization of expensive VR equipment',
                    'recommendation': 'Implement provider training program and patient education campaign to increase adoption',
                    'confidence': 0.81,
                    'impact': {
                        'current_utilization': vr_utilization,
                        'potential_sessions': self.model.vr_stations * 8,  # 8 sessions per day potential
                        'missed_opportunities': int((1 - vr_utilization) * self.model.vr_stations * 8)
                    }
                })
                
        return insights
        
    def _detect_social_network_effects(self) -> List[Dict[str, Any]]:
        """Analyze how veterans influence each other"""
        insights = []
        
        # Look for influence patterns in VR adoption
        vr_adopters = [a for a in self.model.schedule.agents 
                      if hasattr(a, 'vr_willingness') and a.vr_willingness]
        
        if len(vr_adopters) > 10:
            # Check clustering of VR adoption
            adoption_clusters = self._find_adoption_clusters(vr_adopters)
            
            if adoption_clusters:
                insights.append({
                    'id': f'social_influence_{datetime.now().timestamp()}',
                    'type': 'social_network_pattern',
                    'severity': 'low',
                    'title': 'Peer Influence Driving VR Therapy Adoption',
                    'description': f'Veterans who try VR therapy are influencing {len(adoption_clusters)} connected peers to also try it',
                    'recommendation': 'Leverage peer champions and success stories to accelerate adoption',
                    'confidence': 0.76,
                    'impact': {
                        'influenced_veterans': len(adoption_clusters),
                        'network_effect_multiplier': len(adoption_clusters) / len(vr_adopters)
                    }
                })
                
        return insights
        
    def _detect_temporal_patterns(self) -> List[Dict[str, Any]]:
        """Find time-based patterns in operations"""
        insights = []
        
        # Simple pattern detection based on current metrics
        current_wait = getattr(self.model, 'current_average_wait', 0)
        
        if current_wait > 60:
            insights.append({
                'id': f'temporal_pattern_{datetime.now().timestamp()}',
                'type': 'temporal_pattern',
                'severity': 'medium',
                'title': 'Extended Wait Times Detected',
                'description': f'Current average wait time of {current_wait:.0f} minutes indicates system stress',
                'recommendation': 'Monitor for recurring patterns and implement dynamic staffing adjustments',
                'confidence': 0.73,
                'impact': {
                    'current_wait': current_wait,
                    'threshold_exceeded': current_wait - 30
                }
            })
            
        return insights
        
    def _detect_resource_optimization(self) -> List[Dict[str, Any]]:
        """Find opportunities for resource optimization"""
        insights = []
        
        # Staff allocation analysis
        providers = [a for a in self.model.schedule.agents if hasattr(a, 'specialty')]
        
        if providers:
            # Calculate workload by specialty
            workload = defaultdict(lambda: {'providers': 0, 'patients': 0})
            
            for provider in providers:
                spec = provider.specialty.value
                workload[spec]['providers'] += 1
                workload[spec]['patients'] += provider.patients_seen_today if hasattr(provider, 'patients_seen_today') else 0
                
            # Find imbalances
            ratios = {}
            for spec, data in workload.items():
                if data['providers'] > 0:
                    ratios[spec] = data['patients'] / data['providers']
                    
            if ratios:
                avg_ratio = np.mean(list(ratios.values()))
                
                for spec, ratio in ratios.items():
                    if ratio < avg_ratio * 0.5:  # Underutilized
                        insights.append({
                            'id': f'resource_opt_{datetime.now().timestamp()}',
                            'type': 'resource_optimization',
                            'severity': 'medium',
                            'title': f'{spec.replace("_", " ").title()} Staff Underutilized',
                            'description': f'{spec} providers seeing only {ratio:.1f} patients each while system average is {avg_ratio:.1f}',
                            'recommendation': f'Cross-train {spec} staff for other departments or reduce {spec} staffing during low-demand periods',
                            'confidence': 0.78,
                            'impact': {
                                'current_utilization': ratio / avg_ratio,
                                'potential_savings': f'${(1 - ratio/avg_ratio) * 50000:.0f} annually'
                            }
                        })
                        
        return insights
        
    def _estimate_vr_impact(self, current_wait_times: List[float]) -> float:
        """Estimate potential impact of VR therapy expansion"""
        # Simple model: VR sessions are 25% faster and can handle more patients
        vr_efficiency_gain = 0.25
        
        # Estimate based on mental health patient percentage
        mh_percentage = 0.25  # From typical VA distribution
        
        potential_reduction = mh_percentage * vr_efficiency_gain * 100
        return min(potential_reduction, 40)  # Cap at 40% reduction
        
    def _find_adoption_clusters(self, adopters: List[Any]) -> List[Any]:
        """Find clusters of veterans who adopted innovation"""
        clusters = []
        
        # Simple approach: find adopters who are connected in social network
        for adopter in adopters:
            if hasattr(adopter, 'social_connections'):
                influenced = [conn for conn in adopter.social_connections 
                            if hasattr(conn, 'vr_willingness') and conn.vr_willingness]
                if influenced:
                    clusters.extend(influenced)
                    
        return list(set(clusters))  # Unique influenced veterans
        
    def _filter_insights(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and rank insights by importance"""
        # Remove duplicates
        unique_insights = []
        seen_types = set()
        
        for insight in insights:
            key = (insight['type'], insight.get('title', ''))
            if key not in seen_types:
                seen_types.add(key)
                unique_insights.append(insight)
                
        # Filter by confidence
        filtered = [i for i in unique_insights if i['confidence'] >= self.confidence_threshold]
        
        # Sort by severity and confidence
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        filtered.sort(key=lambda x: (severity_order.get(x['severity'], 0), x['confidence']), 
                     reverse=True)
        
        return filtered[:10]  # Return top 10 insights