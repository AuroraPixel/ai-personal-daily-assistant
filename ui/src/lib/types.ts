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
  type: 'tool_call' | 'handoff' | 'context_update' | 'error'
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