export class Token_113 {
  id: string
  name: string
  createdAt: number
  updatedAt: number
  active: boolean
  
  constructor(data?: object) {
    this.id = this.generateId()
    this.name = ''
    this.createdAt = Date.now()
    this.updatedAt = Date.now()
    this.active = true
    
    if (data) {
      Object.assign(this, data)
    }
  }
  
  private generateId(): string {
    return `id_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  save() {
    console.log(`Saving ${this.constructor.name}: ${this.id}`)
  }
  
  update(data: object) {
    Object.assign(this, data)
    this.updatedAt = Date.now()
    console.log(`Updated ${this.id}`)
  }
  
  delete() {
    console.log(`Deleting ${this.id}`)
  }
  
  toJSON(): object {
    return {
      id: this.id,
      name: this.name,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
      active: this.active
    }
  }
  
  static fromJSON(json: object): Token_113 {
    return new Token_113(json)
  }
  
  clone(): Token_113 {
    return Token_113.fromJSON(this.toJSON())
  }
}
