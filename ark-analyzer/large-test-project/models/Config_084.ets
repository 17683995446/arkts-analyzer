export class Log_084 {

    public field0: Date = new Date()
    public field1: number[] = []
    public field2: Date = new Date()

  constructor(data?: Partial<Log_084>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
