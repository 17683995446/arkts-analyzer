export class Order_133 {

    public field0: boolean = true
    public field1: string[] = []
    public field2: number[] = []
    public field3: number = 18
    public field4: number[] = []
    public field5: Date = new Date()

  constructor(data?: Partial<Order_133>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
