import { APIResponse, GitHubEvent } from '@/types/github';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<APIResponse<T>> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new ApiError(response.status, `请求失败: ${response.statusText}`);
  }

  return response.json();
}

export const githubApi = {
  async getEvents(
    username: string, 
    eventType: string = 'public', 
    perPage: number = 30
  ): Promise<APIResponse<GitHubEvent>> {
    return apiRequest<GitHubEvent>(
      `/github/events/${username}?event_type=${eventType}&per_page=${perPage}`
    );
  },

  async getRepositoryEvents(
    owner: string, 
    repo: string, 
    perPage: number = 30
  ): Promise<APIResponse<GitHubEvent>> {
    return apiRequest<GitHubEvent>(
      `/github/repo-events/${owner}/${repo}?per_page=${perPage}`
    );
  },

  async getProfile(username: string): Promise<APIResponse> {
    return apiRequest('/github/profile', {
      method: 'POST',
      body: JSON.stringify({ username }),
    });
  },

  async getRepositories(username: string): Promise<APIResponse> {
    return apiRequest('/github/repositories', {
      method: 'POST',
      body: JSON.stringify({ username }),
    });
  },
};