export class Log_189 {

    public field0: number[] = []
    public field1: boolean = true
    public field2: Date = new Date()
    public field3: number[] = []
    public field4: boolean = true
    public field5: boolean = true
    public field6: number = 12
    public field7: Date = new Date()
    public field8: boolean = true
    public field9: boolean = true

  constructor(data?: Partial<Log_189>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
