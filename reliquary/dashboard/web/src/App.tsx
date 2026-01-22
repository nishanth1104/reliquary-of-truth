import React, { useEffect, useState } from 'react';
import { api, RunSummary, Stats } from './api/client';

function App() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [runsData, statsData] = await Promise.all([
        api.getRuns({ limit: 50 }),
        api.getStats()
      ]);
      setRuns(runsData.runs);
      setStats(statsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'DELIVERED': return 'green';
      case 'BLOCKED': return 'red';
      case 'NEEDS_INFO': return 'yellow';
      default: return 'blue';
    }
  };

  if (loading) {
    return <div style={{ padding: '20px' }}>Loading...</div>;
  }

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🏛️ Reliquary of Truth Dashboard</h1>

      {stats && (
        <div style={{ marginBottom: '30px', padding: '20px', background: '#f5f5f5', borderRadius: '8px' }}>
          <h2>Statistics</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{stats.total_runs}</div>
              <div style={{ color: '#666' }}>Total Runs</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'green' }}>{stats.successful_runs}</div>
              <div style={{ color: '#666' }}>Successful</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{stats.success_rate.toFixed(1)}%</div>
              <div style={{ color: '#666' }}>Success Rate</div>
            </div>
            <div>
              <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{stats.avg_attempts}</div>
              <div style={{ color: '#666' }}>Avg Attempts</div>
            </div>
          </div>
        </div>
      )}

      <h2>Recent Runs</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #ddd' }}>
            <th style={{ textAlign: 'left', padding: '10px' }}>Status</th>
            <th style={{ textAlign: 'left', padding: '10px' }}>Work Item</th>
            <th style={{ textAlign: 'left', padding: '10px' }}>Title</th>
            <th style={{ textAlign: 'left', padding: '10px' }}>Repo</th>
            <th style={{ textAlign: 'left', padding: '10px' }}>Attempts</th>
            <th style={{ textAlign: 'left', padding: '10px' }}>Completed</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr key={run.work_item_id} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '10px' }}>
                <span style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: 'bold',
                  background: getStatusColor(run.final_status),
                  color: 'white'
                }}>
                  {run.final_status}
                </span>
              </td>
              <td style={{ padding: '10px', fontFamily: 'monospace' }}>{run.work_item_id}</td>
              <td style={{ padding: '10px' }}>{run.ticket_title}</td>
              <td style={{ padding: '10px' }}>{run.repo_name}</td>
              <td style={{ padding: '10px' }}>{run.implement_attempts}</td>
              <td style={{ padding: '10px', fontSize: '12px', color: '#666' }}>
                {new Date(run.completed_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
