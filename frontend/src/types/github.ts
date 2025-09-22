export interface GitHubEvent {
  id: string;
  type: string;
  actor: {
    id: number;
    login: string;
    display_login?: string;
    gravatar_id?: string;
    url: string;
    avatar_url: string;
  };
  repo: {
    id: number;
    name: string;
    url: string;
  };
  payload: any;
  public: boolean;
  created_at: string;
  org?: {
    id: number;
    login: string;
    gravatar_id?: string;
    url: string;
    avatar_url: string;
  };
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T[];
  message: string;
  count: number;
}

export interface EventTypeConfig {
  icon: string;
  color: string;
  label: string;
  description: (payload: any, repo: string) => string;
}