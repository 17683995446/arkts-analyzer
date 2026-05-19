export class Config_156 {

    public field0: string[] = []
    public field1: number[] = []
    public field2: string = 'default'
    public field3: string = 'hello'
    public field4: string[] = []
    public field5: number = 97
    public field6: string[] = []
    public field7: string = 'hello'
    public field8: boolean = false

  constructor(data?: Partial<Config_156>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
