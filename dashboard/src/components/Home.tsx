import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl shadow-2xl overflow-hidden">
        <div className="px-8 py-16 md:px-16 md:py-20">
          <div className="max-w-4xl">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Predictive Reliability & Auto-Remediation Platform
            </h1>
            <p className="text-xl text-blue-100 mb-8 leading-relaxed">
              Intelligent system monitoring with automated anomaly detection and self-healing capabilities
              for cloud-native microservices architecture.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link
                to="/anomalies"
                className="px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition shadow-lg"
              >
                View Anomalies
              </Link>
              <Link
                to="/policies"
                className="px-6 py-3 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-400 transition border-2 border-white/30"
              >
                Configure Policies
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* What is this platform */}
      <div className="bg-white rounded-xl shadow-lg p-8 md:p-10">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">What is This Platform?</h2>
        <div className="prose prose-lg max-w-none">
          <p className="text-gray-700 leading-relaxed mb-4">
            The Predictive Reliability Platform is an end-to-end Site Reliability Engineering (SRE) solution
            designed to proactively monitor, predict, and remediate issues in distributed microservices environments
            before they impact users.
          </p>
          <p className="text-gray-700 leading-relaxed">
            By combining real-time observability, statistical anomaly detection, and policy-driven automation,
            the platform reduces mean time to detection (MTTD) and mean time to resolution (MTTR), ensuring
            high availability and reliability of your critical services.
          </p>
        </div>
      </div>

      {/* Key Features Grid */}
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Core Capabilities</h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Feature 1 */}
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition border-t-4 border-blue-500">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Real-Time Monitoring</h3>
            <p className="text-gray-600">
              Continuous collection of metrics, logs, and traces from all microservices using Prometheus, Loki, and Jaeger.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition border-t-4 border-purple-500">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Anomaly Detection</h3>
            <p className="text-gray-600">
              ML-powered statistical analysis detects abnormal patterns in CPU usage, error rates, and latency before they escalate.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition border-t-4 border-green-500">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Auto-Remediation</h3>
            <p className="text-gray-600">
              Policy-driven automation executes corrective actions like container restarts, scaling, or alerting based on configurable rules.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition border-t-4 border-orange-500">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Policy Engine</h3>
            <p className="text-gray-600">
              YAML-based policy definitions with customizable thresholds, actions, and cooldown periods for fine-grained control.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition border-t-4 border-red-500">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Chaos Engineering</h3>
            <p className="text-gray-600">
              Built-in chaos simulator to inject failures, test resilience, and validate that auto-remediation works as expected.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition border-t-4 border-indigo-500">
            <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Comprehensive Observability</h3>
            <p className="text-gray-600">
              Full-stack visibility with Grafana dashboards, Prometheus metrics, Loki logs, and Jaeger distributed tracing.
            </p>
          </div>

          {/* Feature 7 - NEW AI */}
          <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition border-t-4 border-purple-500">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">AI-Powered Intelligence</h3>
            <p className="text-gray-600">
              LLM-driven root cause analysis, incident summarization, natural language queries, and intelligent remediation recommendations.
            </p>
          </div>
        </div>
      </div>

      {/* Use Cases */}
      <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl shadow-lg p-8 md:p-10">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">Use Cases</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">E-Commerce Platforms</h3>
            <p className="text-gray-600">
              Automatically detect and remediate checkout service degradation during high-traffic events,
              preventing revenue loss and maintaining customer satisfaction.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Financial Services</h3>
            <p className="text-gray-600">
              Ensure payment processing systems remain highly available with predictive monitoring
              and rapid automated recovery from anomalies.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">SaaS Applications</h3>
            <p className="text-gray-600">
              Maintain SLA commitments by proactively identifying performance issues and executing
              remediation before users are impacted.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">Microservices Platforms</h3>
            <p className="text-gray-600">
              Monitor complex distributed systems with hundreds of services, automatically detecting
              cascading failures and isolating problematic components.
            </p>
          </div>
        </div>
      </div>

      {/* Architecture Overview */}
      <div className="bg-white rounded-xl shadow-lg p-8 md:p-10">
        <h2 className="text-3xl font-bold text-gray-900 mb-6">Architecture Overview</h2>
        <div className="space-y-4">
          <div className="flex items-start space-x-4 p-4 bg-blue-50 rounded-lg">
            <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
              1
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">Instrumented Microservices</h4>
              <p className="text-gray-600 text-sm">
                Services expose metrics, health endpoints, and traces. Built-in chaos engineering capabilities
                simulate realistic failure scenarios.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-4 p-4 bg-purple-50 rounded-lg">
            <div className="flex-shrink-0 w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold">
              2
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">Observability Stack</h4>
              <p className="text-gray-600 text-sm">
                Prometheus scrapes metrics, Loki aggregates logs, and Jaeger collects distributed traces
                for comprehensive system visibility.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-4 p-4 bg-green-50 rounded-lg">
            <div className="flex-shrink-0 w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold">
              3
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">Anomaly Detection Engine</h4>
              <p className="text-gray-600 text-sm">
                Statistical analysis on time-series data identifies deviations from normal behavior patterns,
                generating predictions with confidence scores.
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-4 p-4 bg-orange-50 rounded-lg">
            <div className="flex-shrink-0 w-8 h-8 bg-orange-600 text-white rounded-full flex items-center justify-center font-bold">
              4
            </div>
            <div>
              <h4 className="font-semibold text-gray-900">Policy Evaluation & Remediation</h4>
              <p className="text-gray-600 text-sm">
                Policy engine evaluates anomalies against defined rules and executes automated remediation
                actions with cooldown periods to prevent oscillation.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-700 rounded-2xl shadow-2xl p-8 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Ready to Get Started?</h2>
        <p className="text-indigo-100 text-lg mb-8 max-w-2xl mx-auto">
          Explore the dashboard to monitor your services, view detected anomalies, and configure auto-remediation policies.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            to="/anomalies"
            className="px-6 py-3 bg-white text-indigo-600 rounded-lg font-semibold hover:bg-indigo-50 transition shadow-lg"
          >
            Monitor Services
          </Link>
          <a
            href="http://localhost:3001"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 bg-indigo-500 text-white rounded-lg font-semibold hover:bg-indigo-400 transition border-2 border-white/30"
          >
            Open Grafana
          </a>
          <a
            href="http://localhost:8080/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 bg-indigo-500 text-white rounded-lg font-semibold hover:bg-indigo-400 transition border-2 border-white/30"
          >
            API Documentation
          </a>
        </div>
      </div>
    </div>
  )
}

