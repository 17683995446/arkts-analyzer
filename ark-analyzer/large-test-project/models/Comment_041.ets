export class Product_041 {

    public field0: number = 31
    public field1: Date = new Date()
    public field2: string = 'test'
    public field3: string[] = []
    public field4: number[] = []
    public field5: string[] = []
    public field6: Date = new Date()
    public field7: string = 'test'
    public field8: string = 'value'
    public field9: string = 'default'
    public field10: number = 98
    public field11: string = 'hello'
    public field12: number[] = []

  constructor(data?: Partial<Product_041>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
