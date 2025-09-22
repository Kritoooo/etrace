'use client';

import { useState, useMemo } from 'react';
import { GitHubEvent } from '@/types/github';
import { eventTypeConfigs } from '@/lib/eventConfig';
import { formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

interface TimelineProps {
  events: GitHubEvent[];
}

export default function Timeline({ events }: TimelineProps) {
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);

  const getEventConfig = (eventType: string) => {
    return eventTypeConfigs[eventType] || eventTypeConfigs.default;
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return formatDistanceToNow(date, { addSuffix: true, locale: zhCN });
    } catch {
      return dateString;
    }
  };

  // 获取所有唯一的事件类型
  const availableTypes = useMemo(() => {
    const types = Array.from(new Set(events.map(event => event.type)));
    return types.map(type => ({
      type,
      config: getEventConfig(type),
      count: events.filter(event => event.type === type).length
    })).sort((a, b) => b.count - a.count);
  }, [events]);

  // 筛选后的事件
  const filteredEvents = useMemo(() => {
    if (selectedTypes.length === 0) {
      return events;
    }
    return events.filter(event => selectedTypes.includes(event.type));
  }, [events, selectedTypes]);

  const handleTypeToggle = (type: string) => {
    setSelectedTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const handleClearAll = () => {
    setSelectedTypes([]);
  };

  if (!events.length) {
    return (
      <div className="flex items-center justify-center py-12">
        <p className="text-gray-500">暂无事件数据</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 筛选器 */}
      <div className="bg-white rounded-lg shadow-md p-4 border border-gray-100">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">事件类型筛选</h3>
          {selectedTypes.length > 0 && (
            <button
              onClick={handleClearAll}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              清除所有筛选 ({filteredEvents.length}/{events.length})
            </button>
          )}
        </div>
        
        <div className="flex flex-wrap gap-2">
          {availableTypes.map(({ type, config, count }) => (
            <button
              key={type}
              onClick={() => handleTypeToggle(type)}
              className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                selectedTypes.includes(type) || selectedTypes.length === 0
                  ? `${config.color} text-white`
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span className="mr-1">{config.icon}</span>
              {config.label}
              <span className="ml-1 text-xs opacity-80">({count})</span>
            </button>
          ))}
        </div>
      </div>

      {/* 时间线 */}
      <div className="relative">
        <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gray-200"></div>
        
        <div className="space-y-6">
          {filteredEvents.map((event) => {
          const config = getEventConfig(event.type);
          
          return (
            <div key={event.id} className="relative flex items-start space-x-4">
              <div className={`relative z-10 flex items-center justify-center w-16 h-16 rounded-full ${config.color} text-white text-2xl shadow-lg`}>
                {config.icon}
              </div>
              
              <div className="flex-1 bg-white rounded-lg shadow-md p-6 border border-gray-100 min-h-[120px]">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1 mr-4 leading-tight">
                    {config.label}
                  </h3>
                  <span className="text-sm text-gray-500 whitespace-nowrap">
                    {formatDate(event.created_at)}
                  </span>
                </div>
                
                <p className="text-gray-700 mb-3 break-words">
                  {config.description(event.payload, event.repo.name)}
                </p>
                
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center space-x-2">
                    <img 
                      src={event.actor.avatar_url} 
                      alt={event.actor.login}
                      className="w-6 h-6 rounded-full"
                    />
                    <span>{event.actor.login}</span>
                  </div>
                  
                  <div className="truncate">
                    <span className="font-medium">{event.repo.name}</span>
                  </div>
                </div>
                
                {event.payload?.commits && event.payload.commits.length > 0 && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium mb-1">最新提交:</div>
                    {event.payload.commits.slice(0, 3).map((commit: any, index: number) => (
                      <div key={index} className="text-gray-600 break-words line-clamp-2 mb-1">
                        • {commit.message}
                      </div>
                    ))}
                    {event.payload.commits.length > 3 && (
                      <div className="text-gray-500 text-xs mt-1">
                        还有 {event.payload.commits.length - 3} 个提交...
                      </div>
                    )}
                  </div>
                )}
                
                {event.payload?.pull_request && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium break-words line-clamp-2 mb-1">{event.payload.pull_request.title}</div>
                    {event.payload.pull_request.body && (
                      <div className="text-gray-600 mt-1 break-words line-clamp-3">
                        {event.payload.pull_request.body.length > 150 
                          ? `${event.payload.pull_request.body.slice(0, 150)}...`
                          : event.payload.pull_request.body
                        }
                      </div>
                    )}
                  </div>
                )}
                
                {event.payload?.issue && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium break-words line-clamp-2 mb-1">{event.payload.issue.title}</div>
                    {event.payload.issue.body && (
                      <div className="text-gray-600 mt-1 break-words line-clamp-3">
                        {event.payload.issue.body.length > 150 
                          ? `${event.payload.issue.body.slice(0, 150)}...`
                          : event.payload.issue.body
                        }
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
          })}
        </div>
      </div>

      {/* 无匹配结果提示 */}
      {selectedTypes.length > 0 && filteredEvents.length === 0 && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <p className="text-gray-500 mb-2">没有找到匹配的事件</p>
            <button
              onClick={handleClearAll}
              className="text-blue-600 hover:text-blue-800 text-sm"
            >
              清除筛选条件
            </button>
          </div>
        </div>
      )}
    </div>
  );
}