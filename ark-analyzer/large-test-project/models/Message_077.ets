export class Token_077 {

    public field0: string = 'test'
    public field1: string = 'default'
    public field2: number[] = []
    public field3: Date = new Date()
    public field4: string[] = []
    public field5: string[] = []
    public field6: number = 16
    public field7: boolean = true
    public field8: number[] = []
    public field9: number = 47

  constructor(data?: Partial<Token_077>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
