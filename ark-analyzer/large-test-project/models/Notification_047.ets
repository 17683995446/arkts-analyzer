export class Setting_047 {

    public field0: string = 'value'
    public field1: string[] = []
    public field2: string[] = []
    public field3: number = 16
    public field4: boolean = true
    public field5: string = ''
    public field6: boolean = true
    public field7: boolean = true
    public field8: string = 'default'
    public field9: number[] = []

  constructor(data?: Partial<Setting_047>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
