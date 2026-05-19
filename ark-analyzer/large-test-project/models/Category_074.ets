export class Setting_074 {

    public field0: Date = new Date()
    public field1: number[] = []
    public field2: Date = new Date()
    public field3: string[] = []

  constructor(data?: Partial<Setting_074>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
