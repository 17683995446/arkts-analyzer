export class Comment_039 {

    public field0: string[] = []
    public field1: string[] = []
    public field2: boolean = true
    public field3: string[] = []
    public field4: string = 'test'
    public field5: boolean = false
    public field6: Date = new Date()
    public field7: string[] = []
    public field8: number = 17
    public field9: number[] = []
    public field10: string[] = []
    public field11: number = 58

  constructor(data?: Partial<Comment_039>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
