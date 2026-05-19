export class Comment_003 {

    public field0: string = 'default'
    public field1: boolean = true
    public field2: string[] = []

  constructor(data?: Partial<Comment_003>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
