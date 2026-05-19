export class Order_090 {

    public field0: string = ''
    public field1: number = 91
    public field2: string = 'test'
    public field3: string = 'value'
    public field4: Date = new Date()
    public field5: boolean = false

  constructor(data?: Partial<Order_090>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
