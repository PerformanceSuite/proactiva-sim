import React, { useState } from 'react';
import { 
  Search, 
  AlertTriangle, 
  Link, 
  TrendingUp, 
  DollarSign,
  Users,
  Building,
  GitBranch,
  Mail,
  FileText,
  MessageSquare,
  BarChart3,
  Lightbulb,
  Package,
  Clock,
  CheckCircle2,
  XCircle,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';

const ProjectIntelligence = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedProject, setSelectedProject] = useState(null);

  // Mock data for demonstration
  const duplicateProjects = [
    {
      id: 1,
      name: "Telehealth Platform Implementation",
      departments: ["IT", "Cardiology", "Primary Care"],
      similarity: 85,
      potentialSavings: 250000,
      status: "active",
      description: "Multiple departments implementing separate telehealth solutions"
    },
    {
      id: 2,
      name: "Patient Portal Enhancement",
      departments: ["IT", "Patient Experience", "Billing"],
      similarity: 72,
      potentialSavings: 180000,
      status: "planning",
      description: "Overlapping efforts to improve patient portal functionality"
    },
    {
      id: 3,
      name: "Analytics Dashboard Development",
      departments: ["Quality", "Operations", "Finance"],
      similarity: 68,
      potentialSavings: 120000,
      status: "active",
      description: "Three separate analytics initiatives with similar goals"
    }
  ];

  const synergyOpportunities = [
    {
      id: 1,
      projects: ["VR Therapy Program", "Mental Health Innovation Lab"],
      benefit: "Shared VR equipment and expertise",
      impact: "high",
      estimatedValue: 180000,
      departments: ["Psychiatry", "Research"]
    },
    {
      id: 2,
      projects: ["AI Triage System", "Emergency Department Optimization"],
      benefit: "Combined AI model development",
      impact: "medium",
      estimatedValue: 150000,
      departments: ["Emergency", "IT", "Operations"]
    },
    {
      id: 3,
      projects: ["Mobile Health Units", "Rural Outreach Program"],
      benefit: "Coordinated deployment and resources",
      impact: "high",
      estimatedValue: 320000,
      departments: ["Community Health", "Primary Care"]
    }
  ];

  const vendorAnalysis = [
    {
      vendor: "TechHealth Solutions",
      contracts: 4,
      totalSpend: 850000,
      departments: ["IT", "Radiology", "Lab", "Pharmacy"],
      consolidationOpportunity: 255000,
      services: ["Cloud Storage", "Analytics", "Integration", "Support"]
    },
    {
      vendor: "MedAnalytics Pro",
      contracts: 3,
      totalSpend: 520000,
      departments: ["Quality", "Finance", "Operations"],
      consolidationOpportunity: 130000,
      services: ["Reporting", "Dashboards", "Data Warehouse"]
    },
    {
      vendor: "CareConnect Systems",
      contracts: 2,
      totalSpend: 380000,
      departments: ["IT", "Clinical"],
      consolidationOpportunity: 76000,
      services: ["Integration", "Messaging", "Workflow"]
    }
  ];

  const projectMetrics = {
    totalProjects: 147,
    duplicatesDetected: 23,
    synergiesFound: 18,
    potentialSavings: 2.3,
    projectsAnalyzed: 892,
    communicationsProcessed: 45678,
    vendorsTracked: 67,
    departmentsConnected: 24
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'duplicates', label: 'Duplicate Detection', icon: AlertTriangle },
    { id: 'synergies', label: 'Synergy Opportunities', icon: Link },
    { id: 'vendors', label: 'Vendor Analysis', icon: Package },
    { id: 'insights', label: 'AI Insights', icon: Lightbulb }
  ];

  const renderMetricCard = (title, value, trend, icon) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-600 text-sm">{title}</span>
        {icon}
      </div>
      <div className="flex items-baseline">
        <span className="text-2xl font-bold text-gray-900">{value}</span>
        {trend && (
          <span className={`ml-2 text-sm flex items-center ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend > 0 ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
            {Math.abs(trend)}%
          </span>
        )}
      </div>
    </div>
  );

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-4 gap-4">
        {renderMetricCard('Active Projects', projectMetrics.totalProjects, 12, <FileText className="w-5 h-5 text-blue-500" />)}
        {renderMetricCard('Duplicates Found', projectMetrics.duplicatesDetected, -8, <AlertTriangle className="w-5 h-5 text-yellow-500" />)}
        {renderMetricCard('Synergy Opportunities', projectMetrics.synergiesFound, 15, <Link className="w-5 h-5 text-green-500" />)}
        {renderMetricCard('Potential Savings', `$${projectMetrics.potentialSavings}M`, 23, <DollarSign className="w-5 h-5 text-emerald-500" />)}
      </div>

      {/* Communication Analysis */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Communication Analysis</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="flex items-center space-x-3">
            <Mail className="w-8 h-8 text-gray-400" />
            <div>
              <p className="text-2xl font-bold">{(projectMetrics.communicationsProcessed / 1000).toFixed(1)}K</p>
              <p className="text-sm text-gray-600">Emails Analyzed</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <MessageSquare className="w-8 h-8 text-gray-400" />
            <div>
              <p className="text-2xl font-bold">1.2K</p>
              <p className="text-sm text-gray-600">Meeting Transcripts</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <FileText className="w-8 h-8 text-gray-400" />
            <div>
              <p className="text-2xl font-bold">3.4K</p>
              <p className="text-sm text-gray-600">Documents Scanned</p>
            </div>
          </div>
        </div>
      </div>

      {/* Department Network */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Department Collaboration Network</h3>
        <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
          <p className="text-gray-500">Interactive network visualization would go here</p>
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Alerts</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              <div>
                <p className="font-medium">High Duplication Risk Detected</p>
                <p className="text-sm text-gray-600">3 departments evaluating similar EHR modules</p>
              </div>
            </div>
            <span className="text-sm text-gray-500">2 hours ago</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <Link className="w-5 h-5 text-green-600" />
              <div>
                <p className="font-medium">New Synergy Opportunity</p>
                <p className="text-sm text-gray-600">AI initiatives in Radiology and Pathology could collaborate</p>
              </div>
            </div>
            <span className="text-sm text-gray-500">5 hours ago</span>
          </div>
          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <DollarSign className="w-5 h-5 text-blue-600" />
              <div>
                <p className="font-medium">Vendor Consolidation Opportunity</p>
                <p className="text-sm text-gray-600">Save $180K by consolidating analytics vendors</p>
              </div>
            </div>
            <span className="text-sm text-gray-500">1 day ago</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderDuplicates = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-lg font-semibold">Duplicate Project Detection</h3>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2">
            <Search className="w-4 h-4" />
            <span>Scan for Duplicates</span>
          </button>
        </div>
        
        <div className="space-y-4">
          {duplicateProjects.map((project) => (
            <div key={project.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                 onClick={() => setSelectedProject(project)}>
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h4 className="font-semibold text-lg">{project.name}</h4>
                  <p className="text-gray-600 text-sm mt-1">{project.description}</p>
                  <div className="flex items-center space-x-4 mt-3">
                    <div className="flex items-center space-x-1">
                      <Building className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600">{project.departments.join(", ")}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Clock className="w-4 h-4 text-gray-400" />
                      <span className="text-sm text-gray-600 capitalize">{project.status}</span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-sm text-gray-600">Similarity:</span>
                    <span className={`font-bold ${project.similarity > 80 ? 'text-red-600' : 'text-yellow-600'}`}>
                      {project.similarity}%
                    </span>
                  </div>
                  <div className="text-green-600 font-semibold">
                    ${(project.potentialSavings / 1000).toFixed(0)}K savings
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedProject && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Consolidation Recommendation</h3>
          <div className="space-y-4">
            <p className="text-gray-700">
              Based on our analysis, consolidating these {selectedProject.departments.length} initiatives could:
            </p>
            <ul className="space-y-2">
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span>Save ${(selectedProject.potentialSavings / 1000).toFixed(0)}K in development costs</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span>Reduce implementation time by 40%</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span>Improve cross-department collaboration</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-green-500" />
                <span>Create unified user experience</span>
              </li>
            </ul>
            <div className="flex space-x-3 mt-6">
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Schedule Consolidation Meeting
              </button>
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                View Detailed Analysis
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderSynergies = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-6">Synergy Opportunities</h3>
        <div className="space-y-4">
          {synergyOpportunities.map((synergy) => (
            <div key={synergy.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <GitBranch className="w-5 h-5 text-green-600" />
                    <h4 className="font-semibold">Projects that could collaborate:</h4>
                  </div>
                  <div className="space-y-1 ml-7">
                    {synergy.projects.map((project, idx) => (
                      <p key={idx} className="text-gray-700">• {project}</p>
                    ))}
                  </div>
                  <p className="text-gray-600 mt-3 ml-7">{synergy.benefit}</p>
                  <div className="flex items-center space-x-4 mt-3 ml-7">
                    <span className="text-sm text-gray-600">
                      Departments: {synergy.departments.join(", ")}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`px-3 py-1 rounded-full text-sm font-medium mb-2 ${
                    synergy.impact === 'high' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {synergy.impact.toUpperCase()} IMPACT
                  </div>
                  <div className="text-green-600 font-semibold">
                    ${(synergy.estimatedValue / 1000).toFixed(0)}K value
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Collaboration Benefits</h3>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium mb-3">Resource Sharing</h4>
            <ul className="space-y-2">
              <li className="flex items-center space-x-2">
                <Users className="w-4 h-4 text-gray-400" />
                <span className="text-sm">Share expertise across teams</span>
              </li>
              <li className="flex items-center space-x-2">
                <Package className="w-4 h-4 text-gray-400" />
                <span className="text-sm">Consolidate vendor contracts</span>
              </li>
              <li className="flex items-center space-x-2">
                <DollarSign className="w-4 h-4 text-gray-400" />
                <span className="text-sm">Pool budget resources</span>
              </li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium mb-3">Innovation Acceleration</h4>
            <ul className="space-y-2">
              <li className="flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-gray-400" />
                <span className="text-sm">Faster time to market</span>
              </li>
              <li className="flex items-center space-x-2">
                <Lightbulb className="w-4 h-4 text-gray-400" />
                <span className="text-sm">Cross-pollination of ideas</span>
              </li>
              <li className="flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 text-gray-400" />
                <span className="text-sm">Reduced implementation risk</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );

  const renderVendors = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-6">Vendor Consolidation Analysis</h3>
        <div className="space-y-4">
          {vendorAnalysis.map((vendor, idx) => (
            <div key={idx} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h4 className="font-semibold text-lg">{vendor.vendor}</h4>
                  <div className="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <p className="text-sm text-gray-600">Active Contracts</p>
                      <p className="text-xl font-bold">{vendor.contracts}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Annual Spend</p>
                      <p className="text-xl font-bold">${(vendor.totalSpend / 1000).toFixed(0)}K</p>
                    </div>
                  </div>
                  <div className="mt-3">
                    <p className="text-sm text-gray-600 mb-1">Services:</p>
                    <div className="flex flex-wrap gap-2">
                      {vendor.services.map((service, sIdx) => (
                        <span key={sIdx} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="mt-3">
                    <p className="text-sm text-gray-600">
                      Used by: {vendor.departments.join(", ")}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-medium mb-2">
                    CONSOLIDATION OPPORTUNITY
                  </div>
                  <div className="text-green-600 font-semibold text-lg">
                    Save ${(vendor.consolidationOpportunity / 1000).toFixed(0)}K
                  </div>
                  <button className="mt-3 text-blue-600 hover:text-blue-700 text-sm font-medium">
                    View Details →
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Total Vendor Optimization Potential</h3>
        <div className="text-center py-8">
          <p className="text-5xl font-bold text-green-600">$461K</p>
          <p className="text-gray-600 mt-2">Annual savings through vendor consolidation</p>
          <button className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
            Generate Consolidation Report
          </button>
        </div>
      </div>
    </div>
  );

  const renderInsights = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-6">AI-Generated Insights</h3>
        <div className="space-y-4">
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
            <div className="flex items-start space-x-3">
              <Lightbulb className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-blue-900">Innovation Velocity Pattern</h4>
                <p className="text-blue-800 mt-1">
                  Projects initiated by the Research department have a 73% higher success rate when 
                  they collaborate with clinical departments within the first 30 days.
                </p>
                <p className="text-sm text-blue-700 mt-2">
                  Recommendation: Establish mandatory clinical partnership for all research initiatives.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4">
            <div className="flex items-start space-x-3">
              <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-yellow-900">Resource Allocation Imbalance</h4>
                <p className="text-yellow-800 mt-1">
                  IT department is involved in 67% of all projects but only receives 23% of innovation 
                  budget. This is creating a bottleneck for digital transformation initiatives.
                </p>
                <p className="text-sm text-yellow-700 mt-2">
                  Recommendation: Reallocate 15% of budget to IT or establish shared resource pool.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-green-50 border-l-4 border-green-500 p-4">
            <div className="flex items-start space-x-3">
              <TrendingUp className="w-5 h-5 text-green-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-green-900">Vendor Consolidation Success</h4>
                <p className="text-green-800 mt-1">
                  Departments that consolidated vendors in the last 6 months saved an average of 31% 
                  on software costs and reported 45% higher satisfaction with vendor support.
                </p>
                <p className="text-sm text-green-700 mt-2">
                  Recommendation: Prioritize the 3 identified consolidation opportunities.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Natural Language Query</h3>
        <div className="space-y-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Ask about projects, duplicates, or optimization opportunities..."
              className="w-full px-4 py-3 pr-10 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <Search className="absolute right-3 top-3.5 w-5 h-5 text-gray-400" />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button className="text-left px-3 py-2 text-sm bg-gray-100 rounded hover:bg-gray-200">
              Which departments have the most duplicate projects?
            </button>
            <button className="text-left px-3 py-2 text-sm bg-gray-100 rounded hover:bg-gray-200">
              What's our total vendor consolidation opportunity?
            </button>
            <button className="text-left px-3 py-2 text-sm bg-gray-100 rounded hover:bg-gray-200">
              Show me all AI-related initiatives
            </button>
            <button className="text-left px-3 py-2 text-sm bg-gray-100 rounded hover:bg-gray-200">
              Which projects are at risk of failure?
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Project Intelligence System</h2>
        <p className="text-gray-600">AI-powered analysis of organizational projects and resources</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 mb-6 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-4 py-2 font-medium transition-colors
              ${activeTab === tab.id 
                ? 'text-blue-600 border-b-2 border-blue-600' 
                : 'text-gray-600 hover:text-gray-900'}`}
          >
            <tab.icon className="w-4 h-4" />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'duplicates' && renderDuplicates()}
        {activeTab === 'synergies' && renderSynergies()}
        {activeTab === 'vendors' && renderVendors()}
        {activeTab === 'insights' && renderInsights()}
      </div>
    </div>
  );
};

export default ProjectIntelligence;