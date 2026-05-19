export class Cart_052 {

    public field0: string = ''
    public field1: number[] = []
    public field2: string[] = []
    public field3: boolean = false
    public field4: number = 22
    public field5: string[] = []
    public field6: number = 42
    public field7: number = 21
    public field8: number = 91

  constructor(data?: Partial<Cart_052>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
