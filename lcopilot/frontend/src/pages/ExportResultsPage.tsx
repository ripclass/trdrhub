import React, { useState } from 'react';
import { ArrowLeft, Download, FileText, Mail, Calendar, Filter, CheckCircle } from 'lucide-react';

interface ExportFormat {
  id: string;
  name: string;
  description: string;
  extension: string;
  icon: React.ReactNode;
}

interface ExportTemplate {
  id: string;
  name: string;
  description: string;
  sections: string[];
}

const ExportResultsPage: React.FC = () => {
  const [selectedFormat, setSelectedFormat] = useState<string>('pdf');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('comprehensive');
  const [includeRisks, setIncludeRisks] = useState<string[]>(['all']);
  const [includeSections, setIncludeSections] = useState<string[]>([
    'summary',
    'risks',
    'recommendations',
    'documents'
  ]);
  const [exportSettings, setExportSettings] = useState({
    includeCharts: true,
    includeTimestamps: true,
    includeMetadata: true,
    password: '',
  });

  const formats: ExportFormat[] = [
    {
      id: 'pdf',
      name: 'PDF Report',
      description: 'Professional report with charts and formatting',
      extension: '.pdf',
      icon: <FileText size={24} className="text-red-500" />
    },
    {
      id: 'excel',
      name: 'Excel Spreadsheet',
      description: 'Data tables with filtering and analysis capabilities',
      extension: '.xlsx',
      icon: <FileText size={24} className="text-green-500" />
    },
    {
      id: 'json',
      name: 'JSON Data',
      description: 'Raw data for API integration or custom processing',
      extension: '.json',
      icon: <FileText size={24} className="text-blue-500" />
    },
    {
      id: 'csv',
      name: 'CSV Export',
      description: 'Comma-separated values for data analysis tools',
      extension: '.csv',
      icon: <FileText size={24} className="text-purple-500" />
    },
  ];

  const templates: ExportTemplate[] = [
    {
      id: 'comprehensive',
      name: 'Comprehensive Report',
      description: 'Full analysis with all sections included',
      sections: ['Executive Summary', 'Risk Analysis', 'Document Review', 'Recommendations', 'Appendices']
    },
    {
      id: 'executive',
      name: 'Executive Summary',
      description: 'High-level overview for management',
      sections: ['Key Findings', 'Risk Overview', 'Priority Actions']
    },
    {
      id: 'technical',
      name: 'Technical Analysis',
      description: 'Detailed technical findings for compliance teams',
      sections: ['Document Analysis', 'Risk Details', 'Compliance Issues', 'Technical Recommendations']
    },
    {
      id: 'custom',
      name: 'Custom Report',
      description: 'Select specific sections to include',
      sections: ['Customizable']
    }
  ];

  const availableSections = [
    { id: 'summary', label: 'Executive Summary', description: 'High-level findings and overview' },
    { id: 'risks', label: 'Risk Analysis', description: 'Detailed risk assessment and scores' },
    { id: 'documents', label: 'Document Review', description: 'Analysis of uploaded documents' },
    { id: 'recommendations', label: 'Recommendations', description: 'Suggested actions and improvements' },
    { id: 'compliance', label: 'Compliance Issues', description: 'Regulatory compliance findings' },
    { id: 'amendments', label: 'Amendment History', description: 'Record of proposed amendments' },
    { id: 'costs', label: 'Cost Analysis', description: 'Financial impact assessment' },
    { id: 'timeline', label: 'Timeline & Deadlines', description: 'Critical dates and milestones' }
  ];

  const riskLevels = [
    { id: 'all', label: 'All Risks', count: 12 },
    { id: 'critical', label: 'Critical', count: 0 },
    { id: 'high', label: 'High', count: 1 },
    { id: 'medium', label: 'Medium', count: 2 },
    { id: 'low', label: 'Low', count: 9 }
  ];

  const handleExport = () => {
    console.log('Export configuration:', {
      format: selectedFormat,
      template: selectedTemplate,
      includeRisks,
      includeSections,
      exportSettings
    });

    // Simulate export process
    alert(`Generating ${formats.find(f => f.id === selectedFormat)?.name}...`);
  };

  const handleSectionToggle = (sectionId: string) => {
    setIncludeSections(prev =>
      prev.includes(sectionId)
        ? prev.filter(s => s !== sectionId)
        : [...prev, sectionId]
    );
  };

  const handleRiskLevelToggle = (riskLevel: string) => {
    if (riskLevel === 'all') {
      setIncludeRisks(['all']);
    } else {
      setIncludeRisks(prev => {
        const filtered = prev.filter(r => r !== 'all');
        return filtered.includes(riskLevel)
          ? filtered.filter(r => r !== riskLevel)
          : [...filtered, riskLevel];
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900 mb-4">
            <ArrowLeft size={16} />
            Back to Dashboard
          </button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Export Results</h1>
              <p className="text-gray-600 mt-1">
                Generate and download comprehensive analysis reports
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Export Configuration */}
          <div className="lg:col-span-2 space-y-8">
            {/* Format Selection */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Export Format
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {formats.map((format) => (
                  <div
                    key={format.id}
                    className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedFormat === format.id
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedFormat(format.id)}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0">
                        {format.icon}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 mb-1">
                          {format.name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {format.description}
                        </p>
                        <p className="text-xs text-gray-500 mt-2">
                          File format: {format.extension}
                        </p>
                      </div>
                      {selectedFormat === format.id && (
                        <CheckCircle size={20} className="text-green-500" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Template Selection */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Report Template
              </h2>
              <div className="space-y-3">
                {templates.map((template) => (
                  <div
                    key={template.id}
                    className={`p-4 border rounded-lg cursor-pointer transition-all ${
                      selectedTemplate === template.id
                        ? 'border-green-500 bg-green-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedTemplate(template.id)}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-gray-900">
                            {template.name}
                          </h3>
                          {selectedTemplate === template.id && (
                            <CheckCircle size={16} className="text-green-500" />
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">
                          {template.description}
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {template.sections.map((section, index) => (
                            <span key={index} className="status-badge bg-gray-100 text-gray-700 text-xs">
                              {section}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Custom Sections (only show if custom template is selected) */}
            {selectedTemplate === 'custom' && (
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">
                  Select Sections
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {availableSections.map((section) => (
                    <label
                      key={section.id}
                      className="flex items-start gap-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
                    >
                      <input
                        type="checkbox"
                        checked={includeSections.includes(section.id)}
                        onChange={() => handleSectionToggle(section.id)}
                        className="mt-1 h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <div className="flex-1">
                        <div className="font-medium text-gray-900 text-sm">
                          {section.label}
                        </div>
                        <div className="text-xs text-gray-600">
                          {section.description}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}

            {/* Risk Level Filter */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Risk Level Filter
              </h2>
              <div className="space-y-2">
                {riskLevels.map((risk) => (
                  <label
                    key={risk.id}
                    className="flex items-center gap-3 p-2 rounded hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={includeRisks.includes(risk.id) || includeRisks.includes('all')}
                      onChange={() => handleRiskLevelToggle(risk.id)}
                      disabled={includeRisks.includes('all') && risk.id !== 'all'}
                      className="h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <span className="flex-1 text-sm font-medium text-gray-900">
                      {risk.label}
                    </span>
                    <span className="text-xs text-gray-500">
                      ({risk.count})
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Additional Settings */}
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Additional Settings
              </h2>
              <div className="space-y-4">
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={exportSettings.includeCharts}
                    onChange={(e) => setExportSettings({...exportSettings, includeCharts: e.target.checked})}
                    className="h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="text-sm font-medium text-gray-900">Include charts and visualizations</span>
                </label>

                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={exportSettings.includeTimestamps}
                    onChange={(e) => setExportSettings({...exportSettings, includeTimestamps: e.target.checked})}
                    className="h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="text-sm font-medium text-gray-900">Include timestamps and metadata</span>
                </label>

                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={exportSettings.includeMetadata}
                    onChange={(e) => setExportSettings({...exportSettings, includeMetadata: e.target.checked})}
                    className="h-4 w-4 text-green-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="text-sm font-medium text-gray-900">Include technical metadata</span>
                </label>

                {selectedFormat === 'pdf' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Password Protection (Optional)
                    </label>
                    <input
                      type="password"
                      value={exportSettings.password}
                      onChange={(e) => setExportSettings({...exportSettings, password: e.target.value})}
                      placeholder="Enter password to protect PDF"
                      className="w-full max-w-xs border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-green-500"
                    />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Export Preview */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Export Preview
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Format:</span>
                  <span className="font-medium">
                    {formats.find(f => f.id === selectedFormat)?.name}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Template:</span>
                  <span className="font-medium">
                    {templates.find(t => t.id === selectedTemplate)?.name}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Sections:</span>
                  <span className="font-medium">
                    {selectedTemplate === 'custom' ? includeSections.length : 'All'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Risk Levels:</span>
                  <span className="font-medium">
                    {includeRisks.includes('all') ? 'All' : includeRisks.length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Est. Size:</span>
                  <span className="font-medium">2.3 MB</span>
                </div>
              </div>

              <button
                onClick={handleExport}
                className="w-full btn-primary mt-6 flex items-center justify-center gap-2"
              >
                <Download size={18} />
                Generate Export
              </button>
            </div>

            {/* Quick Actions */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <button className="w-full btn-secondary flex items-center gap-2">
                  <Mail size={16} />
                  Email Report
                </button>
                <button className="w-full btn-secondary flex items-center gap-2">
                  <Calendar size={16} />
                  Schedule Export
                </button>
                <button className="w-full btn-secondary flex items-center gap-2">
                  <Filter size={16} />
                  Save Template
                </button>
              </div>
            </div>

            {/* Export History */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Recent Exports
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                  <div>
                    <div className="font-medium text-gray-900">Comprehensive Report</div>
                    <div className="text-gray-500">PDF • 2.1 MB</div>
                  </div>
                  <div className="text-xs text-gray-500">Today</div>
                </div>
                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                  <div>
                    <div className="font-medium text-gray-900">Risk Analysis Data</div>
                    <div className="text-gray-500">Excel • 850 KB</div>
                  </div>
                  <div className="text-xs text-gray-500">Yesterday</div>
                </div>
                <div className="flex items-center justify-between py-2">
                  <div>
                    <div className="font-medium text-gray-900">Executive Summary</div>
                    <div className="text-gray-500">PDF • 456 KB</div>
                  </div>
                  <div className="text-xs text-gray-500">3 days ago</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportResultsPage;