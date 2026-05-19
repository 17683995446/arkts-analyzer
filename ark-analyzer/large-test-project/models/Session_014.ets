export class Follow_014 {

    public field0: Date = new Date()
    public field1: Date = new Date()
    public field2: number = 49
    public field3: string = 'value'
    public field4: string[] = []
    public field5: string = 'hello'
    public field6: string[] = []
    public field7: number[] = []
    public field8: boolean = true
    public field9: number[] = []
    public field10: string[] = []

  constructor(data?: Partial<Follow_014>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
