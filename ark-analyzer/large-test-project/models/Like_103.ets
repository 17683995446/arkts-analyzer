export class Message_103 {

    public field0: number[] = []
    public field1: string[] = []
    public field2: string = 'default'
    public field3: string[] = []
    public field4: boolean = true
    public field5: number = 77
    public field6: boolean = false
    public field7: number = 39
    public field8: boolean = true
    public field9: string = 'hello'

  constructor(data?: Partial<Message_103>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
