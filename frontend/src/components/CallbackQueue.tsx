import React, { useState } from 'react';
import type { Callback, Encounter } from '../types';

interface CallbackQueueProps {
  callbacks: Callback[];
  encounters: Map<number, Encounter>;
  providerId: number; // eslint-disable-line @typescript-eslint/no-unused-vars
  onAssign: (callbackId: number) => Promise<void>;
  onComplete: (callbackId: number, outcome: string, notes?: string) => Promise<void>;
  onRefresh: () => void;
}

const CallbackQueue: React.FC<CallbackQueueProps> = ({
  callbacks,
  encounters,
  onAssign,
  onComplete,
  onRefresh
}) => {
  const [activeTab, setActiveTab] = useState<'queued' | 'in_progress' | 'done'>('queued');
  const [selectedCallback, setSelectedCallback] = useState<Callback | null>(null);
  const [outcome, setOutcome] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getRiskBadge = (riskCode?: string) => {
    if (!riskCode) return null;
    
    const colors = {
      'EMERGENCY': 'bg-red-600 text-white',
      'MALARIA_SUSPECT': 'bg-orange-500 text-white',
      'FEVER_GENERAL': 'bg-yellow-500 text-white',
      'LOW_RISK': 'bg-green-500 text-white',
    };
    
    const labels = {
      'EMERGENCY': 'Emergency',
      'MALARIA_SUSPECT': 'Malaria?',
      'FEVER_GENERAL': 'Fever',
      'LOW_RISK': 'Low Risk',
    };
    
    return (
      <span className={`px-2 py-1 rounded text-xs font-semibold ${colors[riskCode as keyof typeof colors] || 'bg-gray-500 text-white'}`}>
        {labels[riskCode as keyof typeof labels] || riskCode}
      </span>
    );
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const past = new Date(timestamp);
    const diffMs = now.getTime() - past.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays}d ago`;
    if (diffHours > 0) return `${diffHours}h ago`;
    if (diffMins > 0) return `${diffMins}m ago`;
    return 'Just now';
  };

  const handleAssign = async (callbackId: number) => {
    setLoading(true);
    try {
      await onAssign(callbackId);
      onRefresh();
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    if (!selectedCallback || !outcome) return;
    
    setLoading(true);
    try {
      await onComplete(selectedCallback.id, outcome, notes);
      setSelectedCallback(null);
      setOutcome('');
      setNotes('');
      onRefresh();
    } finally {
      setLoading(false);
    }
  };

  const filteredCallbacks = callbacks.filter(cb => {
    if (activeTab === 'queued') return cb.status === 'queued';
    if (activeTab === 'in_progress') return cb.status === 'in_progress';
    if (activeTab === 'done') return cb.status === 'done';
    return false;
  });

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="border-b border-gray-200">
        <div className="flex justify-between items-center p-4">
          <h2 className="text-xl font-bold text-gray-900">USSD Callback Queue</h2>
          <button
            onClick={onRefresh}
            className="text-blue-600 hover:text-blue-800"
            disabled={loading}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
        
        <div className="flex space-x-1 px-4">
          {(['queued', 'in_progress', 'done'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium text-sm border-b-2 ${
                activeTab === tab
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-800 hover:border-gray-300'
              }`}
            >
              {tab === 'queued' && 'Queued'}
              {tab === 'in_progress' && 'In Progress'}
              {tab === 'done' && 'Completed'}
              <span className="ml-2 px-2 py-0.5 text-xs rounded-full bg-gray-200">
                {callbacks.filter(cb => cb.status === tab).length}
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {filteredCallbacks.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No {activeTab.replace('_', ' ')} callbacks
          </div>
        ) : (
          filteredCallbacks.map((callback) => {
            const encounter = encounters.get(callback.encounter_id);
            
            return (
              <div key={callback.id} className="p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(callback.priority)}`}>
                        {callback.priority.toUpperCase()}
                      </span>
                      {encounter?.risk_code && getRiskBadge(encounter.risk_code)}
                      <span className="text-sm text-gray-600">
                        Case #{callback.encounter_id}
                      </span>
                    </div>
                    
                    {encounter && (
                      <div className="text-sm text-gray-700 mb-2">
                        <div className="flex space-x-4">
                          {encounter.age_group && (
                            <span>Age: {encounter.age_group}</span>
                          )}
                          {encounter.patient_gender && (
                            <span>Gender: {encounter.patient_gender}</span>
                          )}
                        </div>
                      </div>
                    )}
                    
                    <div className="text-xs text-gray-500 flex items-center space-x-3">
                      <span>Queued: {getTimeAgo(callback.created_at)}</span>
                      {callback.assigned_at && (
                        <span>Assigned: {getTimeAgo(callback.assigned_at)}</span>
                      )}
                      {callback.completed_at && (
                        <span>Completed: {getTimeAgo(callback.completed_at)}</span>
                      )}
                    </div>
                  </div>
                  
                  <div className="ml-4 flex space-x-2">
                    {callback.status === 'queued' && (
                      <button
                        onClick={() => handleAssign(callback.id)}
                        disabled={loading}
                        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 text-sm"
                      >
                        Assign to Me
                      </button>
                    )}
                    
                    {callback.status === 'in_progress' && (
                      <button
                        onClick={() => setSelectedCallback(callback)}
                        disabled={loading}
                        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400 text-sm"
                      >
                        Complete
                      </button>
                    )}
                    
                    {callback.status === 'done' && callback.outcome && (
                      <div className="text-sm">
                        <div className="text-gray-700 font-medium">Outcome:</div>
                        <div className="text-gray-600">{callback.outcome}</div>
                        {callback.notes && (
                          <div className="text-gray-500 text-xs mt-1">{callback.notes}</div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Complete Callback Modal */}
      {selectedCallback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-bold mb-4">Complete Callback #{selectedCallback.id}</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Outcome *
              </label>
              <textarea
                value={outcome}
                onChange={(e) => setOutcome(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={3}
                placeholder="Describe the outcome of the call..."
                required
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes (Optional)
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={2}
                placeholder="Additional notes..."
              />
            </div>
            
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => {
                  setSelectedCallback(null);
                  setOutcome('');
                  setNotes('');
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                onClick={handleComplete}
                disabled={loading || !outcome}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
              >
                {loading ? 'Saving...' : 'Complete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CallbackQueue;
