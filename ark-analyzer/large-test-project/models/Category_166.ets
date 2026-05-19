export class Follow_166 {

    public field0: number[] = []
    public field1: boolean = false
    public field2: boolean = true
    public field3: Date = new Date()
    public field4: string = 'hello'
    public field5: number[] = []
    public field6: Date = new Date()
    public field7: number[] = []

  constructor(data?: Partial<Follow_166>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
