export class Cart_001 {

    public field0: boolean = false
    public field1: string = 'test'
    public field2: number[] = []
    public field3: boolean = true
    public field4: Date = new Date()
    public field5: number[] = []
    public field6: string = 'test'
    public field7: boolean = false
    public field8: number[] = []
    public field9: number[] = []
    public field10: Date = new Date()
    public field11: boolean = true
    public field12: number[] = []
    public field13: number = 22

  constructor(data?: Partial<Cart_001>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
