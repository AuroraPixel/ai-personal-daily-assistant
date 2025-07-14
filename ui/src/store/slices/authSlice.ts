import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { AuthState, User, LoginCredentials, AuthToken } from '../../lib/types';
import { authAPI } from '../../services/apiService';
import { AuthManager } from '../../lib/auth';

// 从localStorage恢复初始状态
const initialAuthState = AuthManager.getAuthState();

// 初始状态
const initialState: AuthState = {
  user: initialAuthState.user,
  token: initialAuthState.token,
  isAuthenticated: initialAuthState.isAuthenticated,
  isLoading: false,
  error: null,
};

// 异步actions
export const login = createAsyncThunk<AuthToken, LoginCredentials, { rejectValue: string }>(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials);
      if (response.success && response.data) {
        // 使用认证管理器保存token
        AuthManager.saveAuth(response.data);
        return response.data;
      }
      return rejectWithValue(response.message || '登录失败');
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const logout = createAsyncThunk<void, void, { rejectValue: string }>(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await authAPI.logout();
      AuthManager.clearAuth();
    } catch (error: any) {
      // 即使登出API失败，也清除本地token
      AuthManager.clearAuth();
      return rejectWithValue(error.message);
    }
  }
);

export const refreshToken = createAsyncThunk<AuthToken, void, { rejectValue: string }>(
  'auth/refreshToken',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.refreshToken();
      if (response.success && response.data) {
        AuthManager.saveAuth(response.data);
        return response.data;
      }
      return rejectWithValue(response.message || '刷新token失败');
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

export const getCurrentUser = createAsyncThunk<User, void, { rejectValue: string }>(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.getCurrentUser();
      if (response.success && response.data) {
        return response.data;
      }
      return rejectWithValue(response.message || '获取用户信息失败');
    } catch (error: any) {
      return rejectWithValue(error.message);
    }
  }
);

// 验证当前token有效性
export const validateToken = createAsyncThunk<User, void, { rejectValue: string }>(
  'auth/validateToken',
  async (_, { rejectWithValue }) => {
    try {
      // 检查本地token是否过期
      if (AuthManager.isTokenExpired()) {
        throw new Error('Token已过期');
      }
      
      // 验证token是否有效
      const response = await authAPI.getCurrentUser();
      if (response.success && response.data) {
        return response.data;
      }
      throw new Error(response.message || 'Token无效');
    } catch (error: any) {
      // Token无效，清除本地存储
      AuthManager.clearAuth();
      return rejectWithValue(error.message);
    }
  }
);

// 认证slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    clearAuth: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.error = null;
      AuthManager.clearAuth();
    },
    // 新增：恢复认证状态
    restoreAuth: (state) => {
      const authState = AuthManager.getAuthState();
      state.user = authState.user;
      state.token = authState.token;
      state.isAuthenticated = authState.isAuthenticated;
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 登录
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.error = null;
        if (action.payload.access_token && action.payload.user_info) {
          state.token = action.payload.access_token;
          state.user = action.payload.user_info;
          state.isAuthenticated = true;
        }
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        state.isAuthenticated = false;
      })
      // 登出
      .addCase(logout.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(logout.fulfilled, (state) => {
        state.isLoading = false;
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
        state.error = null;
      })
      .addCase(logout.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        // 即使登出失败，也清除本地状态
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      // 刷新token
      .addCase(refreshToken.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(refreshToken.fulfilled, (state, action) => {
        state.isLoading = false;
        state.error = null;
        if (action.payload.access_token && action.payload.user_info) {
          state.token = action.payload.access_token;
          state.user = action.payload.user_info;
          state.isAuthenticated = true;
        }
      })
      .addCase(refreshToken.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        // token刷新失败，清除认证状态
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      // 获取当前用户
      .addCase(getCurrentUser.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.error = null;
        if (action.payload) {
          state.user = action.payload;
          state.isAuthenticated = true;
        }
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        // 获取用户信息失败，清除认证状态
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      })
      // 验证token
      .addCase(validateToken.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(validateToken.fulfilled, (state, action) => {
        state.isLoading = false;
        state.error = null;
        if (action.payload) {
          state.user = action.payload;
          state.isAuthenticated = true;
        }
      })
      .addCase(validateToken.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
        // Token验证失败，清除认证状态
        state.user = null;
        state.token = null;
        state.isAuthenticated = false;
      });
  },
});

export const { clearError, setUser, clearAuth, restoreAuth } = authSlice.actions;
export default authSlice.reducer; 