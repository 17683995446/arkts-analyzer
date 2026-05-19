export interface Model {
  id: number
  createdAt: string
  updatedAt: string
}

export interface User extends Model {
  name: string
  email: string
  avatar?: string
  role: UserRole
  status: UserStatus
}

export interface Post extends Model {
  title: string
  content: string
  authorId: number
  author?: User
  tags: string[]
  viewCount: number
  likeCount: number
  commentCount: number
  published: boolean
}

export interface Comment extends Model {
  content: string
  authorId: number
  author?: User
  postId: number
  parentId?: number
  replies?: Comment[]
}

export interface Category extends Model {
  name: string
  description: string
  slug: string
  icon?: string
  parentId?: number
  children?: Category[]
}

export interface Tag extends Model {
  name: string
  slug: string
  color?: string
  count?: number
}

export class UserStatus {
  static readonly Active = 'active'
  static readonly Inactive = 'inactive'
  static readonly Banned = 'banned'
}

export class UserRole {
  static readonly Admin = 'admin'
  static readonly User = 'user'
  static readonly Guest = 'guest'
  static readonly Moderator = 'moderator'
}

export class PaginationParams {
  page: number = 1
  limit: number = 20
  sortBy?: string
  order?: 'asc' | 'desc' = 'asc'

  constructor(params?: Partial<PaginationParams>) {
    if (params) {
      Object.assign(this, params)
    }
  }

  toQueryString(): string {
    const params = new URLSearchParams()
    params.append('page', this.page.toString())
    params.append('limit', this.limit.toString())
    if (this.sortBy) {
      params.append('sortBy', this.sortBy)
    }
    if (this.order) {
      params.append('order', this.order)
    }
    return params.toString()
  }
}

export class ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string

  constructor(success: boolean, data?: T, error?: string) {
    this.success = success
    this.data = data
    this.error = error
  }

  static success<T>(data: T, message?: string): ApiResponse<T> {
    const response = new ApiResponse<T>(true, data)
    response.message = message
    return response
  }

  static error(message: string): ApiResponse<null> {
    return new ApiResponse(false, null, message)
  }
}
