export class Log_011 {

    public field0: number = 41
    public field1: number[] = []
    public field2: boolean = false
    public field3: number = 79
    public field4: Date = new Date()
    public field5: string[] = []
    public field6: string = 'default'
    public field7: string = 'hello'
    public field8: string[] = []
    public field9: number[] = []

  constructor(data?: Partial<Log_011>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
