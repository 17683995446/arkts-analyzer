export class Like_102 {

    public field0: number = 58
    public field1: boolean = true
    public field2: string = 'value'
    public field3: number = 7
    public field4: number = 32
    public field5: number = 97
    public field6: boolean = false
    public field7: Date = new Date()
    public field8: string = 'hello'
    public field9: Date = new Date()
    public field10: boolean = true

  constructor(data?: Partial<Like_102>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
