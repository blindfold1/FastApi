import React, { Component } from 'react';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Обновляем состояние, чтобы показать запасной UI при следующей отрисовке
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Логируем ошибку (можно отправить на сервер для мониторинга)
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // Запасной UI при ошибке
      return (
        <div>
          <h2>Something went wrong.</h2>
          <p>{this.state.error?.message || 'Unknown error'}</p>
          <button onClick={() => window.location.reload()}>Reload Page</button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;