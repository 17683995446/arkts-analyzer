export class Token_127 {

    public field0: number[] = []
    public field1: string = 'hello'
    public field2: number[] = []
    public field3: Date = new Date()
    public field4: string[] = []

  constructor(data?: Partial<Token_127>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
