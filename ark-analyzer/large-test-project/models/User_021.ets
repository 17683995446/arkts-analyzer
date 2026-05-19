export class Config_021 {

    public field0: string = 'default'
    public field1: number = 97
    public field2: boolean = false
    public field3: boolean = false
    public field4: Date = new Date()
    public field5: boolean = false
    public field6: Date = new Date()
    public field7: number[] = []
    public field8: number[] = []
    public field9: boolean = true
    public field10: string[] = []
    public field11: boolean = true
    public field12: string = 'default'
    public field13: Date = new Date()
    public field14: number[] = []

  constructor(data?: Partial<Config_021>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
