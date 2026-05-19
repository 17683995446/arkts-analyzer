export class Config_107 {

    public field0: Date = new Date()
    public field1: string[] = []
    public field2: number[] = []
    public field3: boolean = false
    public field4: Date = new Date()
    public field5: Date = new Date()
    public field6: boolean = false

  constructor(data?: Partial<Config_107>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
