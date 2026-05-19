export class Config_192 {

    public field0: boolean = true
    public field1: Date = new Date()
    public field2: number[] = []
    public field3: boolean = true
    public field4: string[] = []
    public field5: string = 'default'
    public field6: boolean = true
    public field7: boolean = true
    public field8: Date = new Date()
    public field9: string[] = []
    public field10: number[] = []
    public field11: boolean = false
    public field12: string[] = []

  constructor(data?: Partial<Config_192>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
