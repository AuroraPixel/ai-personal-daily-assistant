import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import { login, clearError } from '../store/slices/authSlice';
import type { LoginCredentials } from '../lib/types';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Eye, EyeOff, Lock, User, AlertCircle, Loader2 } from 'lucide-react';

const Login: React.FC = () => {
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { isLoading, error, isAuthenticated } = useAppSelector((state) => state.auth);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginCredentials>();

  // 清除错误消息 - 只在组件卸载时清除
  useEffect(() => {
    return () => {
      dispatch(clearError());
    };
  }, [dispatch]);

  // 如果已经认证，直接跳转到主页
  useEffect(() => {
    if (isAuthenticated) {
      console.log('🏠 Login: 用户已认证，跳转到主页');
      navigate('/', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const onSubmit = async (data: LoginCredentials) => {
    console.log('📝 提交登录表单:', data);
    
    // 清除之前的错误
    dispatch(clearError());
    
    try {
      const result = await dispatch(login(data)).unwrap();
      console.log('✅ 登录成功:', result);
      // 不需要手动导航，上面的useEffect会自动处理
    } catch (error) {
      // 错误已经在store中处理，不需要额外操作
      console.error('❌ 登录失败:', error);
      // 不要导航，让用户留在登录页面看到错误信息
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-white shadow-xl">
        <div className="p-8">
          {/* Logo和标题 */}
          <div className="text-center mb-8">
            <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mb-4">
              <User className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              AI 个人助手
            </h1>
            <p className="text-gray-600">
              请登录您的账户
            </p>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <span className="text-red-700 text-sm">{error}</span>
            </div>
          )}

          {/* 登录表单 */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* 用户名字段 */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                用户名
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('username', {
                    required: '请输入用户名',
                    minLength: {
                      value: 2,
                      message: '用户名至少2个字符',
                    },
                  })}
                  type="text"
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                  placeholder="请输入用户名"
                  autoComplete="username"
                />
              </div>
              {errors.username && (
                <p className="text-red-500 text-sm">{errors.username.message}</p>
              )}
            </div>

            {/* 密码字段 */}
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">
                密码
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  {...register('password', {
                    required: '请输入密码',
                    minLength: {
                      value: 6,
                      message: '密码至少6个字符',
                    },
                  })}
                  type={showPassword ? 'text' : 'password'}
                  className="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                  placeholder="请输入密码"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center z-10 focus:outline-none bg-gray-50/50 hover:bg-gray-200 rounded-r-lg transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? '隐藏密码' : '显示密码'}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-gray-500 hover:text-gray-700 transition-colors" />
                  ) : (
                    <Eye className="h-4 w-4 text-gray-500 hover:text-gray-700 transition-colors" />
                  )}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-500 text-sm">{errors.password.message}</p>
              )}
            </div>

            {/* 登录按钮 */}
            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  登录中...
                </>
              ) : (
                '登录'
              )}
            </Button>
          </form>

          {/* 提示信息 */}
          <div className="mt-8 text-center">
            <div className="text-sm text-gray-600 space-y-1">
              <p className="font-medium text-blue-600">测试账户：<span className="font-mono">jsonplaceholder.typicode.com</span> 获取</p>
              <p className="text-xs">默认密码：<span className="font-mono">admin123456</span></p>
              <p className="text-xs text-gray-500">支持任意用户名登录</p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Login; 