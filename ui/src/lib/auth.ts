/**
 * 认证相关的工具函数
 * 统一管理token的存储、获取和验证
 */

import type { AuthToken, User } from './types';

// 存储keys
const AUTH_KEYS = {
  TOKEN: 'auth_token',
  USER: 'auth_user',
  EXPIRES_AT: 'auth_expires_at',
} as const;

/**
 * Token管理类
 */
export class AuthManager {
  /**
   * 保存认证信息
   */
  static saveAuth(tokenData: AuthToken): void {
    try {
      localStorage.setItem(AUTH_KEYS.TOKEN, tokenData.access_token);
      
      if (tokenData.user_info) {
        localStorage.setItem(AUTH_KEYS.USER, JSON.stringify(tokenData.user_info));
      }
      
      // 计算过期时间
      if (tokenData.expires_in) {
        const expiresAt = Date.now() + (tokenData.expires_in * 1000);
        localStorage.setItem(AUTH_KEYS.EXPIRES_AT, expiresAt.toString());
      }
      
      console.log('✅ 认证信息已保存到localStorage');
    } catch (error) {
      console.error('❌ 保存认证信息失败:', error);
    }
  }

  /**
   * 获取token
   */
  static getToken(): string | null {
    try {
      return localStorage.getItem(AUTH_KEYS.TOKEN);
    } catch (error) {
      console.error('❌ 获取token失败:', error);
      return null;
    }
  }

  /**
   * 获取用户信息
   */
  static getUser(): User | null {
    try {
      const userStr = localStorage.getItem(AUTH_KEYS.USER);
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('❌ 获取用户信息失败:', error);
      return null;
    }
  }

  /**
   * 获取token过期时间
   */
  static getExpiresAt(): number | null {
    try {
      const expiresAtStr = localStorage.getItem(AUTH_KEYS.EXPIRES_AT);
      return expiresAtStr ? parseInt(expiresAtStr, 10) : null;
    } catch (error) {
      console.error('❌ 获取过期时间失败:', error);
      return null;
    }
  }

  /**
   * 检查token是否过期
   */
  static isTokenExpired(): boolean {
    const expiresAt = this.getExpiresAt();
    if (!expiresAt) return true;
    
    // 提前5分钟认为过期，给刷新token留时间
    const now = Date.now();
    const fiveMinutes = 5 * 60 * 1000;
    return now >= (expiresAt - fiveMinutes);
  }

  /**
   * 检查是否有有效的认证状态
   */
  static hasValidAuth(): boolean {
    const token = this.getToken();
    const user = this.getUser();
    
    if (!token || !user) return false;
    if (this.isTokenExpired()) return false;
    
    return true;
  }

  /**
   * 获取完整的认证状态
   */
  static getAuthState(): { token: string | null; user: User | null; isAuthenticated: boolean } {
    const token = this.getToken();
    const user = this.getUser();
    const isAuthenticated = this.hasValidAuth();
    
    return { token, user, isAuthenticated };
  }

  /**
   * 清除认证信息
   */
  static clearAuth(): void {
    try {
      localStorage.removeItem(AUTH_KEYS.TOKEN);
      localStorage.removeItem(AUTH_KEYS.USER);
      localStorage.removeItem(AUTH_KEYS.EXPIRES_AT);
      console.log('✅ 认证信息已清除');
    } catch (error) {
      console.error('❌ 清除认证信息失败:', error);
    }
  }

  /**
   * 检查token是否即将过期（用于自动刷新）
   */
  static isTokenExpiringSoon(): boolean {
    const expiresAt = this.getExpiresAt();
    if (!expiresAt) return true;
    
    // 30分钟内过期就认为即将过期
    const now = Date.now();
    const thirtyMinutes = 30 * 60 * 1000;
    return now >= (expiresAt - thirtyMinutes);
  }
}

// 便捷的导出函数
export const {
  saveAuth,
  getToken,
  getUser,
  hasValidAuth,
  getAuthState,
  clearAuth,
  isTokenExpired,
  isTokenExpiringSoon,
} = AuthManager; 