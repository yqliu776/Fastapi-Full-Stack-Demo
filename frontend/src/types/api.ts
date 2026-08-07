// 统一 API 响应类型

export interface ListResponse<T> {
  code: number;
  message: string;
  data: {
    items: T[];
    total: number;
  };
}

export interface SingleResponse<T> {
  code: number;
  message: string;
  data: T;
}

// 操作响应类型
export interface OperationResponse {
  success: boolean;
  message?: string;
}
