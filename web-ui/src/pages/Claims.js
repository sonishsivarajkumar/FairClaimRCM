import React, { useState, useEffect, useCallback } from 'react';
import { useApi } from '../contexts/ApiContext';
import { 
  ClipboardDocumentListIcon, 
  PlusIcon, 
  FunnelIcon, 
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

const Claims = () => {
  const { claimsApi } = useApi();
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  const fetchClaims = useCallback(async () => {
    try {
      setLoading(true);
      const response = await claimsApi.getAll();
      setClaims(response.data || []);
    } catch (error) {
      console.error('Error fetching claims:', error);
      // Set mock data as fallback
      setClaims([
        { id: 1, patient_name: 'John Doe', claim_id: 'CLM-2024-001', status: 'pending', amount: 2500.00, date_submitted: '2024-01-15', diagnosis_codes: ['I10'], procedure_codes: ['99213'] },
        { id: 2, patient_name: 'Jane Smith', claim_id: 'CLM-2024-002', status: 'approved', amount: 1800.00, date_submitted: '2024-01-14', diagnosis_codes: ['E11.9'], procedure_codes: ['99214'] },
        { id: 3, patient_name: 'Bob Johnson', claim_id: 'CLM-2024-003', status: 'denied', amount: 3200.00, date_submitted: '2024-01-13', diagnosis_codes: ['J44.1'], procedure_codes: ['99215'] }
      ]);
    } finally {
      setLoading(false);
    }
  }, [claimsApi]);

  useEffect(() => {
    fetchClaims();
  }, [fetchClaims]);

  const filteredClaims = claims.filter(claim => {
    const matchesSearch = claim.patient_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         claim.claim_id?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || claim.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch(status?.toLowerCase()) {
      case 'approved': return 'bg-green-100 text-green-800';
      case 'denied': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'processing': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Claims Management</h1>
            <p className="text-gray-600">Manage and track healthcare claims</p>
          </div>
          <button 
            onClick={() => alert('Create claim functionality coming soon!')}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <PlusIcon className="h-5 w-5" />
            New Claim
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <ClipboardDocumentListIcon className="h-6 w-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Total Claims</p>
              <p className="text-2xl font-bold text-gray-900">{claims.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <ClipboardDocumentListIcon className="h-6 w-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Approved</p>
              <p className="text-2xl font-bold text-gray-900">
                {claims.filter(c => c.status === 'approved').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <ClipboardDocumentListIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-gray-900">
                {claims.filter(c => c.status === 'pending').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <ClipboardDocumentListIcon className="h-6 w-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Denied</p>
              <p className="text-2xl font-bold text-gray-900">
                {claims.filter(c => c.status === 'denied').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="p-4 border-b border-gray-200">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search claims by patient name or claim ID..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="flex gap-2">
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="approved">Approved</option>
                <option value="denied">Denied</option>
              </select>
              
              <button className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
                <FunnelIcon className="h-4 w-4" />
                Filters
              </button>
            </div>
          </div>
        </div>

        {/* Claims Table */}
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">Loading claims...</p>
            </div>
          ) : filteredClaims.length === 0 ? (
            <div className="p-8 text-center">
              <ClipboardDocumentListIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No claims found</p>
            </div>
          ) : (
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Claim ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Patient
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredClaims.map((claim) => (
                  <tr key={claim.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {claim.claim_id || claim.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {claim.patient_name || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {claim.created_at ? new Date(claim.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(claim.status)}`}>
                        {claim.status || 'pending'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {claim.total_amount ? `$${claim.total_amount.toLocaleString()}` : '$0'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-900">
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button className="text-green-600 hover:text-green-900">
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button className="text-red-600 hover:text-red-900">
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default Claims;
