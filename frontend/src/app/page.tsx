'use client';

import { useState } from 'react';
import { githubApi } from '@/lib/api';
import { GitHubEvent } from '@/types/github';
import Timeline from '@/components/Timeline';

export default function Home() {
  const [username, setUsername] = useState('');
  const [events, setEvents] = useState<GitHubEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;

    setLoading(true);
    setError('');
    
    try {
      const response = await githubApi.getEvents(username.trim());
      if (response.success && response.data) {
        setEvents(response.data);
      } else {
        setError(response.message || '获取数据失败');
        setEvents([]);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '请求失败');
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            GitHub 用户活动时间线
          </h1>
          <p className="text-gray-600 text-lg">
            输入 GitHub 用户名查看其活动时间线
          </p>
        </div>

        <div className="max-w-md mx-auto mb-8">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="输入 GitHub 用户名"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !username.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '搜索中...' : '搜索'}
            </button>
          </form>
        </div>

        {error && (
          <div className="max-w-2xl mx-auto mb-6">
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          </div>
        )}

        {loading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        <div className="max-w-4xl mx-auto">
          <Timeline events={events} />
        </div>
      </div>
    </div>
  );
}
