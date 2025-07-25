import type { ReactNode } from 'react';

export interface Message {
  id: string
  content: string
  type: 'user' | 'ai' | 'system'
  agent: string
  timestamp: Date
  metadata?: any
}

export interface Agent {
  name: string
  description: string
  handoffs: string[]
  tools: string[]
  /** List of input guardrail identifiers for this agent */
  input_guardrails: string[]
}

export type EventType = "message" | "handoff" | "tool_call" | "tool_output" | "context_update"

export interface AgentEvent {
  id: string
  type: 'tool_call' | 'handoff' | 'context_update' | 'error' | 'message'
  agent: string
  content: string
  timestamp: Date
  metadata?: any
}

export interface GuardrailCheck {
  id: string
  name: string
  input: string
  reasoning: string
  passed: boolean
  timestamp: Date
}

export interface Conversation {
  id: string
  title: string
  description: string
  status: 'active' | 'inactive' | 'archived'
  last_active: string
  created_at: string
  updated_at: string
}

// =========================
// 笔记相关类型定义
// =========================

export interface Note {
  id: number
  user_id: number
  title: string
  content: string
  tag: string | null
  status: string
  created_at: string | null
  updated_at: string | null
  last_updated: string | null
  similarity_score?: number
}

export interface NoteCreateRequest {
  title: string
  content: string
  tag?: string
  status?: string
}

export interface NoteUpdateRequest {
  title?: string
  content?: string
  tag?: string
  status?: string
}

export interface NoteListResponse {
  success: boolean
  message: string
  data: Note[]
  total: number
  user_id: number
}

export interface NoteResponse {
  success: boolean
  message: string
  data: Note | null
}

export interface NoteSearchResponse {
  success: boolean
  message: string
  data: Note[]
  search_query: string
  total: number
  user_id: number
}

// =========================
// 待办事项相关类型定义
// =========================

export interface Todo {
  id: number
  user_id: number
  title: string
  description: string
  completed: boolean
  priority: 'high' | 'medium' | 'low'
  note_id: number | null
  due_date: string | null
  completed_at: string | null
  created_at: string | null
  updated_at: string | null
  last_updated: string | null
  is_overdue: boolean
  status_display: string
}

export interface TodoCreateRequest {
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  due_date?: string
  note_id?: number
}

export interface TodoUpdateRequest {
  title?: string
  description?: string
  priority?: 'high' | 'medium' | 'low'
  due_date?: string
  note_id?: number
  completed?: boolean
}

export interface TodoListResponse {
  success: boolean
  message: string
  data: Todo[]
  total: number
  user_id: number
}

export interface TodoResponse {
  success: boolean
  message: string
  data: Todo | null
}

export interface TodoStatsResponse {
  success: boolean
  message: string
  data: {
    total: number
    completed: number
    pending: number
    overdue: number
    high_priority: number
    medium_priority: number
    low_priority: number
  }
  user_id: number
}

// =========================
// Person Data 相关类型定义
// =========================

export type PersonDataTab = 'notes' | 'todos'

export interface PersonDataFilter {
  search?: string
  tag?: string
  status?: string
  priority?: 'high' | 'medium' | 'low'
  completed?: boolean
  overdue?: boolean
}

export interface User {
  user_id: string
  username: string
  email: string
  name?: string
  avatar?: string
}

export interface AuthToken {
  access_token: string
  token_type: string
  expires_in: number
  user_info: User
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

export interface ApiResponse<T = any> {
  success: boolean
  code: number
  message: string
  data?: T
  timestamp?: string
  request_id?: string
}

export interface ProtectedRouteProps {
  children: ReactNode
  requireAuth?: boolean
} 