import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  FileText, 
  Code, 
  DollarSign, 
  TrendingUp, 
  Clock,
  CheckCircle,
  AlertCircle 
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useApi } from '../contexts/ApiContext';

const MetricCard = ({ title, value, change, icon: Icon, color = "blue" }) => (
  <div className="metric-card">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        {change && (
          <p className={`text-sm ${change > 0 ? 'text-green-600' : 'text-red-600'}`}>
            {change > 0 ? '+' : ''}{change}% from last month
          </p>
        )}
      </div>
      <div className={`p-3 rounded-full bg-${color}-100`}>
        <Icon className={`h-6 w-6 text-${color}-600`} />
      </div>
    </div>
  </div>
);

const RecentClaims = () => {
  const recentClaims = [
    { id: 'CLM-001', patient: 'John Doe', status: 'Processed', amount: '$2,450', time: '2 hours ago' },
    { id: 'CLM-002', patient: 'Jane Smith', status: 'Under Review', amount: '$1,850', time: '4 hours ago' },
    { id: 'CLM-003', patient: 'Bob Johnson', status: 'Approved', amount: '$3,200', time: '6 hours ago' },
    { id: 'CLM-004', patient: 'Alice Brown', status: 'Pending', amount: '$950', time: '8 hours ago' },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Approved': return 'text-green-600 bg-green-100';
      case 'Processed': return 'text-blue-600 bg-blue-100';
      case 'Under Review': return 'text-yellow-600 bg-yellow-100';
      case 'Pending': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Claims</h3>
      <div className="space-y-4">
        {recentClaims.map((claim) => (
          <div key={claim.id} className="flex items-center justify-between border-b border-gray-100 pb-3">
            <div className="flex items-center space-x-3">
              <FileText className="h-5 w-5 text-gray-400" />
              <div>
                <p className="font-medium text-gray-900">{claim.id}</p>
                <p className="text-sm text-gray-500">{claim.patient}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(claim.status)}`}>
                {claim.status}
              </span>
              <div className="text-right">
                <p className="font-medium text-gray-900">{claim.amount}</p>
                <p className="text-xs text-gray-500">{claim.time}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function Dashboard() {
  const { analyticsApi } = useApi();
  const [metrics, setMetrics] = useState({
    totalClaims: 1247,
    processingTime: '2.3 days',
    approvalRate: '94.2%',
    totalRevenue: '$2.4M'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await analyticsApi.getDashboardMetrics();
        if (response.data) {
          setMetrics({
            totalClaims: response.data.total_claims || 1247,
            processingTime: response.data.avg_processing_time || '2.3 days',
            approvalRate: response.data.approval_rate || '94.2%',
            totalRevenue: response.data.total_revenue || '$2.4M'
          });
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Keep using default mock data
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [analyticsApi]);

  // Sample data for charts
  const revenueData = [
    { month: 'Jan', revenue: 2100000, claims: 890 },
    { month: 'Feb', revenue: 2300000, claims: 950 },
    { month: 'Mar', revenue: 2200000, claims: 920 },
    { month: 'Apr', revenue: 2400000, claims: 1020 },
    { month: 'May', revenue: 2600000, claims: 1100 },
    { month: 'Jun', revenue: 2500000, claims: 1050 },
  ];

  const codingAccuracy = [
    { name: 'ICD-10', accuracy: 96, total: 1200 },
    { name: 'CPT', accuracy: 94, total: 1500 },
    { name: 'DRG', accuracy: 98, total: 800 },
  ];

  const claimStatus = [
    { name: 'Approved', value: 850, color: '#10B981' },
    { name: 'Under Review', value: 200, color: '#F59E0B' },
    { name: 'Pending', value: 150, color: '#6B7280' },
    { name: 'Rejected', value: 47, color: '#EF4444' },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Clock className="h-4 w-4" />
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Claims"
          value={metrics.totalClaims.toLocaleString()}
          change={12.5}
          icon={FileText}
          color="blue"
        />
        <MetricCard
          title="Avg Processing Time"
          value={metrics.processingTime}
          change={-8.2}
          icon={Clock}
          color="green"
        />
        <MetricCard
          title="Approval Rate"
          value={metrics.approvalRate}
          change={2.1}
          icon={CheckCircle}
          color="green"
        />
        <MetricCard
          title="Total Revenue"
          value={metrics.totalRevenue}
          change={15.3}
          icon={DollarSign}
          color="purple"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Trend */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value, name) => [
                name === 'revenue' ? `$${(value / 1000000).toFixed(1)}M` : value,
                name === 'revenue' ? 'Revenue' : 'Claims'
              ]} />
              <Area type="monotone" dataKey="revenue" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Claim Status Distribution */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Claim Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={claimStatus}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {claimStatus.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Coding Accuracy */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Coding Accuracy</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={codingAccuracy}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => [`${value}%`, 'Accuracy']} />
              <Bar dataKey="accuracy" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent Claims */}
        <RecentClaims />
      </div>

      {/* System Health */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center space-x-3">
            <CheckCircle className="h-8 w-8 text-green-500" />
            <div>
              <p className="font-medium text-gray-900">API Status</p>
              <p className="text-sm text-green-600">All systems operational</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <Activity className="h-8 w-8 text-blue-500" />
            <div>
              <p className="font-medium text-gray-900">Active Users</p>
              <p className="text-sm text-gray-600">24 users online</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <TrendingUp className="h-8 w-8 text-purple-500" />
            <div>
              <p className="font-medium text-gray-900">Performance</p>
              <p className="text-sm text-gray-600">98.5% uptime</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
