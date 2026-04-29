import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
          <p className="font-semibold mb-2">Something went wrong rendering this component.</p>
          <button 
            className="px-3 py-1 bg-red-100 hover:bg-red-200 rounded"
            onClick={() => this.setState({ hasError: false })}
          >
            Reset
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
