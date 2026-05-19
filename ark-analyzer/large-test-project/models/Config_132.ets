export class Setting_132 {

    public field0: number[] = []
    public field1: number = 50
    public field2: string = 'value'
    public field3: boolean = true
    public field4: Date = new Date()
    public field5: string[] = []
    public field6: boolean = true

  constructor(data?: Partial<Setting_132>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
