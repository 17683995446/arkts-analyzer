export class Tag_178 {

    public field0: number = 19
    public field1: Date = new Date()
    public field2: number = 93
    public field3: number = 14
    public field4: string[] = []
    public field5: number = 23
    public field6: string = ''

  constructor(data?: Partial<Tag_178>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
