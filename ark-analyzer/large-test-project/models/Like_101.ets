export class Product_101 {

    public field0: string[] = []
    public field1: Date = new Date()
    public field2: number = 59
    public field3: boolean = true
    public field4: string[] = []
    public field5: boolean = false
    public field6: string[] = []
    public field7: number = 33
    public field8: number = 98
    public field9: string = 'hello'
    public field10: number = 100
    public field11: Date = new Date()
    public field12: number[] = []
    public field13: string = ''
    public field14: number[] = []

  constructor(data?: Partial<Product_101>) {
    if (data) {
      Object.assign(this, data)
    }
  }
  
  public toJSON(): Object {
    return { ...this }
  }
}
