/**
 * 错误处理工具函数
 * 用于统一处理API错误，包括权限错误、验证错误等
 */

// 自定义错误接口
export interface CustomError extends Error {
  response?: any;
  name: string;
}

/**
 * 处理API错误并返回用户友好的错误消息
 * 
 * @param error 捕获的错误对象
 * @param defaultMessage 默认错误消息
 * @returns 用户友好的错误消息
 */
export function handleApiError(error: any, defaultMessage: string = '操作失败'): string {
  console.error('API错误:', error);
  
  // 检查是否为权限错误
  if (error && error.name === 'PermissionError') {
    return error.message || '您没有权限执行此操作';
  }
  
  // 检查是否有错误响应
  if (error && error.response) {
    // 处理有响应体的情况
    const response = error.response;
    
    // 检查是否有消息字段
    if (response.data && response.data.message) {
      return response.data.message;
    }
    
    // 检查是否有详情字段
    if (response.data && response.data.detail) {
      try {
        const detail = response.data.detail;
        // 处理数组格式的错误详情
        if (Array.isArray(detail)) {
          return detail.map(item => item.msg || item).join(', ');
        }
        // 处理字符串格式的错误详情
        if (typeof detail === 'string') {
          return detail;
        }
      } catch {
        // 忽略解析错误
      }
    }
    
    // 根据HTTP状态码返回信息
    switch (response.status) {
      case 400:
        return '请求参数错误';
      case 401:
        return '未授权，请重新登录';
      case 403:
        return '您没有权限执行此操作';
      case 404:
        return '请求的资源不存在';
      case 500:
        return '服务器内部错误';
      default:
        return `请求失败 (${response.status})`;
    }
  }
  
  // 网络错误等
  if (error && error.message) {
    if (error.message.includes('Network Error')) {
      return '网络连接失败，请检查您的网络';
    }
    if (error.message.includes('timeout')) {
      return '请求超时，请稍后重试';
    }
    return error.message;
  }
  
  // 默认错误消息
  return defaultMessage;
}

/**
 * 为Vue组件提供的错误处理函数
 * 调用此函数会在控制台打印错误，并返回用户友好的错误消息
 * 
 * @param error 捕获的错误对象
 * @param defaultMessage 默认错误消息
 * @returns 用户友好的错误消息
 */
export function handleComponentError(error: any, defaultMessage: string = '操作失败'): string {
  return handleApiError(error, defaultMessage);
} 