export class BaseService {
  protected apiClient: ApiClient

  constructor(apiClient: ApiClient) {
    this.apiClient = apiClient
  }

  protected async handleResponse<T>(promise: Promise<T>): Promise<T> {
    try {
      return await promise
    } catch (error) {
      console.error('Service error:', error)
      throw error
    }
  }
}

export class UserService extends BaseService {
  async getUsers(): Promise<User[]> {
    return this.handleResponse(
      this.apiClient.get<User[]>('/users')
    )
  }

  async getUserById(id: number): Promise<User | null> {
    return this.handleResponse(
      this.apiClient.get<User>(`/users/${id}`)
    )
  }

  async createUser(user: CreateUserDto): Promise<User> {
    return this.handleResponse(
      this.apiClient.post<User>('/users', user)
    )
  }

  async updateUser(id: number, user: UpdateUserDto): Promise<User> {
    return this.handleResponse(
      this.apiClient.put<User>(`/users/${id}`, user)
    )
  }

  async deleteUser(id: number): Promise<void> {
    return this.handleResponse(
      this.apiClient.delete<void>(`/users/${id}`)
    )
  }

  async searchUsers(query: string): Promise<User[]> {
    return this.handleResponse(
      this.apiClient.get<User[]>(`/users/search?q=${query}`)
    )
  }
}

export class AuthService extends BaseService {
  async login(credentials: LoginDto): Promise<AuthResponse> {
    return this.handleResponse(
      this.apiClient.post<AuthResponse>('/auth/login', credentials)
    )
  }

  async logout(): Promise<void> {
    return this.handleResponse(
      this.apiClient.post<void>('/auth/logout')
    )
  }

  async getCurrentUser(): Promise<User> {
    return this.handleResponse(
      this.apiClient.get<User>('/auth/me')
    )
  }

  async refreshToken(): Promise<AuthResponse> {
    return this.handleResponse(
      this.apiClient.post<AuthResponse>('/auth/refresh')
    )
  }
}

export interface User {
  id: number
  name: string
  email: string
  avatar?: string
  role: UserRole
  createdAt: string
  updatedAt: string
}

export interface CreateUserDto {
  name: string
  email: string
  password: string
  role?: UserRole
}

export interface UpdateUserDto {
  name?: string
  email?: string
  avatar?: string
}

export interface LoginDto {
  email: string
  password: string
}

export interface AuthResponse {
  token: string
  refreshToken: string
  user: User
}

export enum UserRole {
  Admin = 'admin',
  User = 'user',
  Guest = 'guest'
}
