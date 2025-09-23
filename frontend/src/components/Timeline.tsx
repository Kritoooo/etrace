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
  const [expandedEvents, setExpandedEvents] = useState<Set<string>>(new Set());

  const getEventConfig = (eventType: string) => {
    return eventTypeConfigs[eventType] || eventTypeConfigs.default;
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return formatDistanceToNow(date, { addSuffix: true, locale: zhCN });
    } catch (error) {
      console.error('Error formatting date:', dateString, error);
      return 'Invalid date';
    }
  };

  // 获取所有唯一的事件类型
  const availableTypes = useMemo(() => {
    const typeGroups = new Map<string, {
      types: string[],
      config: any,
      count: number
    }>();

    events.forEach(event => {
      const config = getEventConfig(event.type);
      const key = config.label; // 使用标签作为分组键
      
      if (typeGroups.has(key)) {
        const group = typeGroups.get(key)!;
        if (!group.types.includes(event.type)) {
          group.types.push(event.type);
        }
        group.count++;
      } else {
        typeGroups.set(key, {
          types: [event.type],
          config,
          count: 1
        });
      }
    });

    return Array.from(typeGroups.entries()).map(([label, group]) => ({
      type: group.types[0], // 使用第一个类型作为代表
      types: group.types, // 保存所有类型用于过滤
      config: group.config,
      count: group.count
    })).sort((a, b) => b.count - a.count);
  }, [events]);

  // 筛选后的事件
  const filteredEvents = useMemo(() => {
    if (selectedTypes.length === 0) {
      return events;
    }
    
    // 获取所有选中分组对应的事件类型
    const selectedEventTypes = new Set<string>();
    selectedTypes.forEach(selectedType => {
      const group = availableTypes.find(item => item.type === selectedType);
      if (group) {
        group.types.forEach(type => selectedEventTypes.add(type));
      }
    });
    
    return events.filter(event => selectedEventTypes.has(event.type));
  }, [events, selectedTypes, availableTypes]);

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

  const toggleEventExpansion = (eventId: string) => {
    setExpandedEvents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(eventId)) {
        newSet.delete(eventId);
      } else {
        newSet.add(eventId);
      }
      return newSet;
    });
  };

  const truncateText = (text: string, maxLength: number = 120) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  // 统一判断是否需要显示展开按钮的函数
  const shouldShowExpandButton = (text: string, lineLimit: number = 3) => {
    if (!text) return false;
    // 根据行数限制计算合理的字符数阈值
    // 假设每行约80个字符（包括中英文混合）
    const charThreshold = lineLimit * 80;
    return text.length > charThreshold;
  };

  const formatTextWithUrls = (text: string, isExpanded: boolean = false, maxLength: number = 240) => {
    if (!text) return text;
    
    // If not expanded and text is too long, truncate it first
    let displayText = text;
    if (!isExpanded && text.length > maxLength) {
      displayText = text.slice(0, maxLength) + '...';
    }
    
    // URL regex pattern - matches http/https URLs
    const urlRegex = /(https?:\/\/[^\s]+)/g;
    
    // Split text by URLs and process each part
    const parts = displayText.split(urlRegex);
    
    return parts.map((part, index) => {
      if (urlRegex.test(part)) {
        // This is a URL
        const truncatedUrl = part.length > 50 ? part.slice(0, 47) + '...' : part;
        return (
          <a
            key={index}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-800 underline break-all inline-block max-w-full"
            title={part}
          >
            {truncatedUrl}
          </a>
        );
      } else {
        // This is regular text
        return <span key={index} className="break-words">{part}</span>;
      }
    });
  };

  const generateGitHubLink = (repoName: string, type: 'issue' | 'pr' | 'commit', identifier: string | number) => {
    const baseUrl = `https://github.com/${repoName}`;
    switch (type) {
      case 'issue':
        return `${baseUrl}/issues/${identifier}`;
      case 'pr':
        return `${baseUrl}/pull/${identifier}`;
      case 'commit':
        return `${baseUrl}/commit/${identifier}`;
      default:
        return baseUrl;
    }
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
          const isExpanded = expandedEvents.has(event.id);
          const description = config.description(event.payload, event.repo.name);
          const shouldTruncate = shouldShowExpandButton(description, 2);
          
          return (
            <div key={event.id} className="relative flex items-start space-x-4">
              <div className={`relative z-10 flex items-center justify-center w-16 h-16 rounded-full ${config.color} text-white text-2xl shadow-lg`}>
                {config.icon}
              </div>
              
              <div className="flex-1 bg-white rounded-lg shadow-md p-6 border border-gray-100 min-h-[120px] overflow-hidden">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 flex-1 mr-4 leading-tight">
                    {config.label}
                  </h3>
                  <span className="text-sm text-gray-500 whitespace-nowrap">
                    {formatDate(event.created_at)}
                  </span>
                </div>
                
                <div className="text-gray-700 mb-3 overflow-hidden">
                  <div className={`${shouldTruncate && !isExpanded ? 'line-clamp-2' : ''} break-words`}>
                    {formatTextWithUrls(isExpanded || !shouldTruncate ? description : truncateText(description), isExpanded)}
                  </div>
                  {shouldTruncate && (
                    <button
                      onClick={() => toggleEventExpansion(event.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm mt-1 font-medium block"
                    >
                      {isExpanded ? '收起' : '展开'}
                    </button>
                  )}
                </div>
                
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center space-x-2">
                    <a 
                      href={`https://github.com/${event.actor.login}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 hover:text-gray-700"
                    >
                      <img 
                        src={event.actor.avatar_url} 
                        alt={event.actor.login}
                        className="w-6 h-6 rounded-full"
                      />
                      <span>{event.actor.login}</span>
                    </a>
                  </div>
                  
                  <div className="truncate">
                    <a 
                      href={`https://github.com/${event.repo.name}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-medium text-blue-600 hover:text-blue-800 hover:underline"
                    >
                      {event.repo.name}
                    </a>
                  </div>
                </div>
                
                {event.payload?.commits && event.payload.commits.length > 0 && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium mb-1">最新提交:</div>
                    {event.payload.commits.slice(0, isExpanded ? event.payload.commits.length : 3).map((commit: any, index: number) => (
                      <div key={index} className="text-gray-600 break-words mb-1">
                        <div className="flex items-start space-x-2">
                          <a
                            href={generateGitHubLink(event.repo.name, 'commit', commit.sha)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-mono text-xs text-blue-600 hover:text-blue-800 hover:underline flex-shrink-0 mt-0.5"
                          >
                            {commit.sha.substring(0, 7)}
                          </a>
                          <div className="line-clamp-2 flex-1">
                            {commit.message}
                          </div>
                        </div>
                      </div>
                    ))}
                    {event.payload.commits.length > 3 && !isExpanded && (
                      <button
                        onClick={() => toggleEventExpansion(event.id)}
                        className="text-blue-600 hover:text-blue-800 text-xs mt-1 font-medium"
                      >
                        查看全部 {event.payload.commits.length} 个提交
                      </button>
                    )}
                  </div>
                )}
                
                {/* Issue Comment Event */}
                {event.type === 'IssueCommentEvent' && event.payload?.comment && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium mb-1">评论内容:</div>
                    <div className="text-gray-600 overflow-hidden">
                      <div className={`${!isExpanded ? 'line-clamp-3' : ''} break-words`}>
                        {formatTextWithUrls(event.payload.comment.body, isExpanded)}
                      </div>
                      {shouldShowExpandButton(event.payload.comment.body, 3) && (
                        <button
                          onClick={() => toggleEventExpansion(event.id)}
                          className="text-blue-600 hover:text-blue-800 text-xs mt-1 font-medium block"
                        >
                          {isExpanded ? '收起' : '查看更多'}
                        </button>
                      )}
                    </div>
                    {event.payload?.issue && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="text-xs text-gray-500 mb-1">相关 Issue:</div>
                        <div className="font-medium text-sm">
                          <a 
                            href={generateGitHubLink(event.repo.name, 'issue', event.payload.issue.number)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 hover:underline break-words"
                          >
                            <div className={`${!isExpanded ? 'line-clamp-1' : ''}`}>
                              #{event.payload.issue.number}: {event.payload.issue.title}
                            </div>
                          </a>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Commit Comment Event */}
                {event.type === 'CommitCommentEvent' && event.payload?.comment && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium mb-1">评论内容:</div>
                    <div className="text-gray-600 overflow-hidden">
                      <div className={`${!isExpanded ? 'line-clamp-3' : ''} break-words`}>
                        {formatTextWithUrls(event.payload.comment.body, isExpanded)}
                      </div>
                      {shouldShowExpandButton(event.payload.comment.body, 3) && (
                        <button
                          onClick={() => toggleEventExpansion(event.id)}
                          className="text-blue-600 hover:text-blue-800 text-xs mt-1 font-medium block"
                        >
                          {isExpanded ? '收起' : '查看更多'}
                        </button>
                      )}
                    </div>
                    {event.payload.comment.commit_id && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="text-xs text-gray-500 mb-1">提交:</div>
                        <a 
                          href={generateGitHubLink(event.repo.name, 'commit', event.payload.comment.commit_id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="font-mono text-sm text-blue-600 hover:text-blue-800 hover:underline break-all"
                        >
                          {event.payload.comment.commit_id.substring(0, 7)}
                        </a>
                      </div>
                    )}
                  </div>
                )}

                {/* Pull Request Review Event */}
                {event.type === 'PullRequestReviewEvent' && event.payload?.review && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium mb-1">审查内容:</div>
                    <div className="text-gray-600 overflow-hidden">
                      <div className="mb-2">
                        <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                          {event.payload.review.state}
                        </span>
                      </div>
                      {event.payload.review.body && (
                        <div className={`${!isExpanded ? 'line-clamp-3' : ''} break-words`}>
                          {formatTextWithUrls(event.payload.review.body, isExpanded)}
                        </div>
                      )}
                      {shouldShowExpandButton(event.payload.review.body, 3) && (
                        <button
                          onClick={() => toggleEventExpansion(event.id)}
                          className="text-blue-600 hover:text-blue-800 text-xs mt-1 font-medium block"
                        >
                          {isExpanded ? '收起' : '查看更多'}
                        </button>
                      )}
                    </div>
                    {event.payload?.pull_request && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="text-xs text-gray-500 mb-1">相关 PR:</div>
                        <div className="font-medium text-sm">
                          <a 
                            href={generateGitHubLink(event.repo.name, 'pr', event.payload.pull_request.number)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 hover:underline break-words"
                          >
                            <div className={`${!isExpanded ? 'line-clamp-1' : ''}`}>
                              #{event.payload.pull_request.number}: {event.payload.pull_request.title}
                            </div>
                          </a>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Pull Request Review Comment Event */}
                {event.type === 'PullRequestReviewCommentEvent' && event.payload?.comment && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium mb-1">审查评论:</div>
                    <div className="text-gray-600 overflow-hidden">
                      <div className={`${!isExpanded ? 'line-clamp-3' : ''} break-words`}>
                        {formatTextWithUrls(event.payload.comment.body, isExpanded)}
                      </div>
                      {shouldShowExpandButton(event.payload.comment.body, 3) && (
                        <button
                          onClick={() => toggleEventExpansion(event.id)}
                          className="text-blue-600 hover:text-blue-800 text-xs mt-1 font-medium block"
                        >
                          {isExpanded ? '收起' : '查看更多'}
                        </button>
                      )}
                    </div>
                    {event.payload?.pull_request && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <div className="text-xs text-gray-500 mb-1">相关 PR:</div>
                        <div className="font-medium text-sm">
                          <a 
                            href={generateGitHubLink(event.repo.name, 'pr', event.payload.pull_request.number)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 hover:underline break-words"
                          >
                            <div className={`${!isExpanded ? 'line-clamp-1' : ''}`}>
                              #{event.payload.pull_request.number}: {event.payload.pull_request.title}
                            </div>
                          </a>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* PR Events (non-review) */}
                {event.type === 'PullRequestEvent' && event.payload?.pull_request && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium break-words mb-1">
                      <div className={`${!isExpanded ? 'line-clamp-2' : ''}`}>
                        {event.payload.pull_request.title}
                      </div>
                    </div>
                    {event.payload.pull_request.body && (
                      <div className="text-gray-600 mt-1 overflow-hidden">
                        <div className={`${!isExpanded ? 'line-clamp-3' : ''} break-words`}>
                          {formatTextWithUrls(event.payload.pull_request.body, isExpanded)}
                        </div>
                        {shouldShowExpandButton(event.payload.pull_request.body, 3) && (
                          <button
                            onClick={() => toggleEventExpansion(event.id)}
                            className="text-blue-600 hover:text-blue-800 text-xs mt-1 font-medium block"
                          >
                            {isExpanded ? '收起' : '查看更多'}
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                )}
                
                {/* Issue Events (non-comment) */}
                {event.type === 'IssuesEvent' && event.payload?.issue && (
                  <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                    <div className="font-medium break-words mb-1">
                      <div className={`${!isExpanded ? 'line-clamp-2' : ''}`}>
                        {event.payload.issue.title}
                      </div>
                    </div>
                    {event.payload.issue.body && (
                      <div className="text-gray-600 mt-1 overflow-hidden">
                        <div className={`${!isExpanded ? 'line-clamp-3' : ''} break-words`}>
                          {formatTextWithUrls(event.payload.issue.body, isExpanded)}
                        </div>
                        {shouldShowExpandButton(event.payload.issue.body, 3) && (
                          <button
                            onClick={() => toggleEventExpansion(event.id)}
                            className="text-blue-600 hover:text-blue-800 text-xs mt-1 font-medium block"
                          >
                            {isExpanded ? '收起' : '查看更多'}
                          </button>
                        )}
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