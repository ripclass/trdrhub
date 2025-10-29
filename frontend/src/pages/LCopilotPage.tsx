import { Link } from 'react-router-dom'
import { ArrowLeft, FileText, Upload, CheckCircle, AlertCircle } from 'lucide-react'

const LCopilotPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link to="/" className="flex items-center text-primary-600 hover:text-primary-700">
                <ArrowLeft className="h-5 w-5 mr-2" />
                Back to TrdrHub
              </Link>
            </div>
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-primary-600">LCopilot</h1>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            LCopilot - Document Validator
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Avoid Costly LC Errors. Get Bank-Ready in Minutes.
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <div className="text-center mb-8">
              <div className="bg-primary-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="h-10 w-10 text-primary-600" />
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Upload Your LC Documents
              </h2>
              <p className="text-gray-600">
                Upload your Letter of Credit documents for instant validation and compliance checking.
              </p>
            </div>

            {/* Upload Area */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-primary-400 transition-colors">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-lg text-gray-600 mb-2">Drag and drop your files here</p>
              <p className="text-sm text-gray-500 mb-4">or click to browse</p>
              <button className="btn-primary">
                Choose Files
              </button>
              <p className="text-xs text-gray-400 mt-2">
                Supports PDF, DOC, DOCX files up to 10MB
              </p>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Compliance Check</h3>
              <p className="text-gray-600 text-sm">
                Automated validation against international banking standards
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="bg-yellow-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertCircle className="h-6 w-6 text-yellow-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Error Detection</h3>
              <p className="text-gray-600 text-sm">
                Real-time identification of common LC errors and discrepancies
              </p>
            </div>

            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="bg-blue-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Export Ready</h3>
              <p className="text-gray-600 text-sm">
                Generate bank-ready documents with proper formatting
              </p>
            </div>
          </div>

          {/* Demo Section */}
          <div className="bg-primary-50 rounded-lg p-8 text-center">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Ready to Get Started?
            </h3>
            <p className="text-gray-600 mb-6">
              Upload your first document and see how LCopilot can help streamline your export process.
            </p>
            <button className="btn-primary">
              Start Validating Documents
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © 2024 TrdrHub. Empowering Bangladesh's SME exporters, one intelligent tool at a time.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default LCopilotPage
