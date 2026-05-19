export class Like_123 {

    public field0: string[] = []
    public field1: boolean = false
    public field2: number[] = []

  constructor(data?: Partial<Like_123>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
