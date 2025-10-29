import { Link } from 'react-router-dom'
import { ArrowRight, CheckCircle, Shield, Zap, Users, Globe } from 'lucide-react'

const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-primary-600">TrdrHub</h1>
              </div>
            </div>
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-4">
                <Link to="/lcopilot" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                  LCopilot
                </Link>
                <a href="#features" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                  Features
                </a>
                <a href="#about" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                  About
                </a>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Empowering Bangladesh's
            <span className="text-primary-600"> SME Exporters</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            One intelligent tool at a time. Streamline your trade documentation, 
            avoid costly LC errors, and get bank-ready in minutes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/lcopilot" className="btn-primary inline-flex items-center">
              Try LCopilot
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <button className="btn-secondary inline-flex items-center">
              Learn More
            </button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div id="features" className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose TrdrHub?
            </h2>
            <p className="text-xl text-gray-600">
              Built specifically for Bangladesh's export ecosystem
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Bank-Ready Documents</h3>
              <p className="text-gray-600">
                Ensure your LC documents meet international banking standards before submission.
              </p>
            </div>
            
            <div className="text-center p-6">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Zap className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Instant Validation</h3>
              <p className="text-gray-600">
                Get real-time feedback on document compliance and error detection.
              </p>
            </div>
            
            <div className="text-center p-6">
              <div className="bg-primary-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">SME Focused</h3>
              <p className="text-gray-600">
                Designed specifically for small and medium exporters in Bangladesh.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* LCopilot Preview Section */}
      <div className="bg-primary-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                Meet LCopilot
              </h2>
              <p className="text-lg text-gray-600 mb-6">
                Our flagship document validation tool that helps you create perfect 
                Letter of Credit documents every time.
              </p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-primary-600 mr-3" />
                  <span className="text-gray-700">Automated compliance checking</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-primary-600 mr-3" />
                  <span className="text-gray-700">Real-time error detection</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-primary-600 mr-3" />
                  <span className="text-gray-700">Bank-specific validation rules</span>
                </li>
                <li className="flex items-center">
                  <CheckCircle className="h-5 w-5 text-primary-600 mr-3" />
                  <span className="text-gray-700">Export-ready formatting</span>
                </li>
              </ul>
              <Link to="/lcopilot" className="btn-primary inline-flex items-center">
                Try LCopilot Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </div>
            <div className="bg-white rounded-lg shadow-lg p-8">
              <div className="text-center">
                <div className="bg-primary-100 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Globe className="h-10 w-10 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">LCopilot</h3>
                <p className="text-gray-600 mb-4">
                  Document Validator
                </p>
                <p className="text-sm text-gray-500">
                  Avoid Costly LC Errors<br />
                  Get Bank-Ready in Minutes
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* About Section */}
      <div id="about" className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">
              About TrdrHub
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              We're on a mission to democratize international trade for Bangladesh's SME exporters. 
              By providing intelligent tools and automated validation, we help businesses compete 
              globally without the complexity.
            </p>
            <div className="mt-8">
              <p className="text-lg text-primary-600 font-semibold">
                🇧🇩 Empowering Bangladesh's SME exporters, one intelligent tool at a time.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4">TrdrHub</h3>
            <p className="text-gray-400 mb-4">
              Empowering Bangladesh's SME exporters, one intelligent tool at a time.
            </p>
            <div className="flex justify-center space-x-6">
              <Link to="/lcopilot" className="text-gray-400 hover:text-white">
                LCopilot
              </Link>
              <a href="#features" className="text-gray-400 hover:text-white">
                Features
              </a>
              <a href="#about" className="text-gray-400 hover:text-white">
                About
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage
