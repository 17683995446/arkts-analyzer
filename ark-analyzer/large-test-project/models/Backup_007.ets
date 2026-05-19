export class Token_007 {

    public field0: string[] = []
    public field1: boolean = true
    public field2: boolean = false
    public field3: number[] = []
    public field4: number[] = []
    public field5: string[] = []
    public field6: number[] = []
    public field7: string[] = []
    public field8: number[] = []

  constructor(data?: Partial<Token_007>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
