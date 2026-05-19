export class Comment_184 {

    public field0: string[] = []
    public field1: boolean = true
    public field2: number = 13
    public field3: Date = new Date()
    public field4: string = 'default'
    public field5: boolean = false

  constructor(data?: Partial<Comment_184>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
