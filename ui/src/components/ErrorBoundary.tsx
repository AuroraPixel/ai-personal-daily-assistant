import React, { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full bg-red-50 text-red-700 p-4 rounded-lg border border-red-200">
          <h1 className="text-lg font-bold mb-2">糟糕，渲染时出错了</h1>
          <p className="text-sm">我们已经记录了这个问题，请尝试刷新页面。</p>
          {this.state.error && (
            <pre className="mt-4 text-xs bg-red-100 p-2 rounded w-full overflow-auto">
              {this.state.error.toString()}
            </pre>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 