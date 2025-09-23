import { EventTypeConfig } from '@/types/github';

export const eventTypeConfigs: Record<string, EventTypeConfig> = {
  PushEvent: {
    icon: "📝",
    color: "bg-blue-500",
    label: "Push",
    description: (payload, repo) => 
      `Pushed ${payload?.commits?.length || 0} commit(s) to ${repo}`
  },
  PullRequestEvent: {
    icon: "🔀",
    color: "bg-green-500",
    label: "Pull Request",
    description: (payload, repo) => 
      `${payload?.action || 'Updated'} pull request #${payload?.pull_request?.number || ''} in ${repo}`
  },
  IssuesEvent: {
    icon: "❗",
    color: "bg-red-500",
    label: "Issues",
    description: (payload, repo) => 
      `${payload?.action || 'Updated'} issue #${payload?.issue?.number || ''} in ${repo}`
  },
  CreateEvent: {
    icon: "🎯",
    color: "bg-yellow-500",
    label: "Create",
    description: (payload, repo) => 
      `Created ${payload?.ref_type || 'repository'} ${payload?.ref || ''} in ${repo}`
  },
  DeleteEvent: {
    icon: "🗑️",
    color: "bg-gray-500",
    label: "Delete",
    description: (payload, repo) => 
      `Deleted ${payload?.ref_type || 'branch'} ${payload?.ref || ''} in ${repo}`
  },
  ForkEvent: {
    icon: "🍴",
    color: "bg-purple-500",
    label: "Fork",
    description: (payload, repo) => 
      `Forked ${repo} to ${payload?.forkee?.full_name || ''}`
  },
  WatchEvent: {
    icon: "⭐",
    color: "bg-orange-500",
    label: "Star",
    description: (payload, repo) => 
      `${payload?.action === 'started' ? 'Starred' : 'Unstarred'} ${repo}`
  },
  ReleaseEvent: {
    icon: "🚀",
    color: "bg-indigo-500",
    label: "Release",
    description: (payload, repo) => 
      `${payload?.action || 'Published'} release ${payload?.release?.tag_name || ''} in ${repo}`
  },
  IssueCommentEvent: {
    icon: "💬",
    color: "bg-blue-400",
    label: "Comment",
    description: (payload, repo) => 
      `${payload?.action || 'Added'} comment on issue #${payload?.issue?.number || ''} in ${repo}`
  },
  CommitCommentEvent: {
    icon: "💭",
    color: "bg-cyan-500",
    label: "Commit Comment",
    description: (payload, repo) => 
      `Commented on commit in ${repo}`
  },
  PullRequestReviewEvent: {
    icon: "🔍",
    color: "bg-emerald-500",
    label: "PR Review",
    description: (payload, repo) => 
      `${payload?.action || 'Reviewed'} pull request #${payload?.pull_request?.number || ''} in ${repo}`
  },
  PullRequestReviewCommentEvent: {
    icon: "📝",
    color: "bg-teal-500",
    label: "PR Review Comment",
    description: (payload, repo) => 
      `${payload?.action || 'Added'} review comment on PR #${payload?.pull_request?.number || ''} in ${repo}`
  },
  GollumEvent: {
    icon: "📚",
    color: "bg-amber-500",
    label: "Wiki",
    description: (payload, repo) => 
      `Updated wiki pages in ${repo}`
  },
  MemberEvent: {
    icon: "👥",
    color: "bg-pink-500",
    label: "Member",
    description: (payload, repo) => 
      `${payload?.action || 'Added'} member to ${repo}`
  },
  PublicEvent: {
    icon: "🌐",
    color: "bg-green-600",
    label: "Public",
    description: (payload, repo) => 
      `Made ${repo} public`
  },
  SponsorshipEvent: {
    icon: "💖",
    color: "bg-red-400",
    label: "Sponsorship",
    description: (payload, repo) => 
      `${payload?.action || 'Updated'} sponsorship`
  },
  default: {
    icon: "📋",
    color: "bg-gray-400",
    label: "Activity",
    description: (payload, repo) => `Activity in ${repo}`
  }
};