export class HashUtils_041 {
  static format(input: any): string {
    return String(input)
  }
  
  static parse(input: string): any {
    try {
      return JSON.parse(input)
    } catch (e) {
      return input
    }
  }
  
  static validate(input: any): boolean {
    return input !== null && input !== undefined && input !== ''
  }
  
  static truncate(str: string, length: number = 50): string {
    if (str.length <= length) {
      return str
    }
    return str.substring(0, length) + '...'
  }
  
  static capitalize(str: string): string {
    if (!str) return ''
    return str.charAt(0).toUpperCase() + str.slice(1)
  }
  
  static isEmpty(value: any): boolean {
    if (value === null || value === undefined) return true
    if (typeof value === 'string') return value.trim() === ''
    if (Array.isArray(value)) return value.length === 0
    if (typeof value === 'object') return Object.keys(value).length === 0
    return false
  }
  
  static randomString(length: number = 10): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let result = ''
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }
  
  static timestamp(): number {
    return Date.now()
  }
  
  static delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}
