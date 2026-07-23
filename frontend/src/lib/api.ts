import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
  AxiosResponse,
  AxiosRequestConfig,
} from "axios";
import { API_CONFIG } from "./constants";
import { useAuthStore } from "@store/authStore";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      // Don't set default Content-Type - let Axios handle it automatically
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        // Token is injected from authStore state
        const token = useAuthStore.getState().token;

        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // Set Content-Type based on data type
        if (config.data instanceof FormData) {
          // For FormData, let Axios set Content-Type automatically with boundary
          // Don't set it manually - Axios will add the boundary parameter
          delete config.headers["Content-Type"];
        } else if (config.data && typeof config.data === "object") {
          // Set JSON Content-Type for object data
          config.headers["Content-Type"] = "application/json";
        }

        return config;
      },
      (error: AxiosError) => {
        void 0;
        return Promise.reject(error);
      },
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      (error: AxiosError) => {
        void 0;
        // Return authentication errors without navigation
        // Navigation should be handled by the application layer
        if (error.response?.status === 401) {
          // Auto logout on token expiration / unauthorized
          useAuthStore.getState().logout();
          error.name = "AuthenticationError";
        }
        return Promise.reject(error);
      },
    );
  }

  public get<T = unknown>(url: string, config?: AxiosRequestConfig) {
    return this.client.get<T>(url, config);
  }

  public post<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ) {
    return this.client.post<T>(url, data, config);
  }

  public put<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ) {
    return this.client.put<T>(url, data, config);
  }

  public delete<T = unknown>(url: string, config?: AxiosRequestConfig) {
    return this.client.delete<T>(url, config);
  }

  public patch<T = unknown>(
    url: string,
    data?: unknown,
    config?: AxiosRequestConfig,
  ) {
    return this.client.patch<T>(url, data, config);
  }
}

export const apiClient = new ApiClient();
