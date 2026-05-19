export class Message_005 {

    public field0: number = 51
    public field1: boolean = true
    public field2: Date = new Date()
    public field3: Date = new Date()
    public field4: Date = new Date()
    public field5: string = 'default'
    public field6: string = 'test'
    public field7: number = 44
    public field8: boolean = true
    public field9: string[] = []

  constructor(data?: Partial<Message_005>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
