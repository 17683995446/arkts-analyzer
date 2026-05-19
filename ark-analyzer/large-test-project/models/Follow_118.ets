export class Comment_118 {

    public field0: string[] = []
    public field1: number = 10
    public field2: boolean = false
    public field3: Date = new Date()
    public field4: boolean = true
    public field5: boolean = false
    public field6: boolean = true
    public field7: boolean = false
    public field8: string[] = []
    public field9: string[] = []

  constructor(data?: Partial<Comment_118>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
